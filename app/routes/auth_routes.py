from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.auth import UserRegister, UserLogin, TokenResponse, RefreshTokenRequest, UserInfo
from app.models.response import ApiResponse
from app.models.user import User, UserState, RefreshTokenBlacklist
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials
    payload = AuthService.verify_token(token, token_type="access")
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    return user


@router.post("/register", response_model=ApiResponse[UserInfo])
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """用户注册"""
    try:
        user = AuthService.register_user(db, user_data.email, user_data.password)
        return ApiResponse(
            code=200,
            message="注册成功，请登录",
            data=UserInfo(
                id=user.id,
                email=user.email,
                state=user.state,
                created_at=user.created_at
            )
        )
    except HTTPException as e:
        return ApiResponse(
            code=e.status_code,
            message=e.detail,
            data=None
        )
    except Exception as e:
        return ApiResponse(
            code=500,
            message=f"注册失败: {str(e)}",
            data=None
        )


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """用户登录"""
    try:
        user = AuthService.authenticate_user(db, user_data.email, user_data.password)
        if not user:
            return ApiResponse(
                code=401,
                message="邮箱或密码错误",
                data=None
            )
        
        # 创建token
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        refresh_token = AuthService.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return ApiResponse(
            code=200,
            message="登录成功",
            data=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
        )
    except Exception as e:
        return ApiResponse(
            code=500,
            message=f"登录失败: {str(e)}",
            data=None
        )


@router.post("/logout", response_model=ApiResponse[None])
async def logout(
    refresh_token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """用户退出登录"""
    try:
        # 验证refresh token
        payload = AuthService.verify_token(refresh_token_data.refresh_token, token_type="refresh")
        user_id = int(payload.get("sub"))
        
        # 检查token是否已在黑名单
        if AuthService.is_token_blacklisted(db, refresh_token_data.refresh_token):
            return ApiResponse(
                code=400,
                message="该token已失效",
                data=None
            )
        
        # 将refresh token加入黑名单
        AuthService.add_token_to_blacklist(db, refresh_token_data.refresh_token, user_id)
        
        return ApiResponse(
            code=200,
            message="退出登录成功",
            data=None
        )
    except HTTPException as e:
        return ApiResponse(
            code=e.status_code,
            message=e.detail,
            data=None
        )
    except Exception as e:
        return ApiResponse(
            code=500,
            message=f"退出登录失败: {str(e)}",
            data=None
        )


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_token(
    refresh_token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    try:
        # 验证refresh token
        payload = AuthService.verify_token(refresh_token_data.refresh_token, token_type="refresh")
        
        # 检查token是否在黑名单中
        if AuthService.is_token_blacklisted(db, refresh_token_data.refresh_token):
            return ApiResponse(
                code=401,
                message="该refresh token已失效",
                data=None
            )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        # 验证用户是否存在
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            return ApiResponse(
                code=401,
                message="用户不存在",
                data=None
            )
        
        # 生成新的access token和refresh token
        new_access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        new_refresh_token = AuthService.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # 将旧的refresh token加入黑名单
        AuthService.add_token_to_blacklist(db, refresh_token_data.refresh_token, user.id)
        
        return ApiResponse(
            code=200,
            message="刷新token成功",
            data=TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer"
            )
        )
    except HTTPException as e:
        return ApiResponse(
            code=e.status_code,
            message=e.detail,
            data=None
        )
    except Exception as e:
        return ApiResponse(
            code=500,
            message=f"刷新token失败: {str(e)}",
            data=None
        )


@router.get("/me", response_model=ApiResponse[UserInfo])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return ApiResponse(
        code=200,
        message="获取用户信息成功",
        data=UserInfo(
            id=current_user.id,
            email=current_user.email,
            state=current_user.state,
            created_at=current_user.created_at
        )
    )


@router.delete("/me", response_model=ApiResponse[None])
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除当前用户账号"""
    try:
        # 删除用户相关的refresh token黑名单记录
        blacklist_records = db.query(RefreshTokenBlacklist).filter(
            RefreshTokenBlacklist.user_id == current_user.id
        ).all()
        
        for record in blacklist_records:
            db.delete(record)
        
        # 删除用户本身
        db.delete(current_user)
        db.commit()
        
        return ApiResponse(
            code=200,
            message="用户账号删除成功",
            data=None
        )
    except Exception as e:
        db.rollback()
        return ApiResponse(
            code=500,
            message=f"删除用户失败: {str(e)}",
            data=None
        )

