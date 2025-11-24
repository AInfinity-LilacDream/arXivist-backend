from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserState


class UserRegister(BaseModel):
    """用户注册请求模型"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, description="密码，最少6位")


class UserLogin(BaseModel):
    """用户登录请求模型"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """Token响应模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class RefreshTokenRequest(BaseModel):
    """刷新Token请求模型"""
    refresh_token: str = Field(..., description="刷新令牌")


class UserInfo(BaseModel):
    """用户信息响应模型"""
    id: int
    email: str
    state: UserState
    created_at: datetime

    class Config:
        from_attributes = True

