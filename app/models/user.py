from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.config.database import Base


class UserState(str, enum.Enum):
    """用户状态枚举"""
    INACTIVE = "inactive"
    ACTIVE = "active"


class User(Base):
    """用户数据库模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    state = Column(SQLEnum(UserState), default=UserState.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class RefreshTokenBlacklist(Base):
    """Refresh Token 黑名单模型"""
    __tablename__ = "refresh_token_blacklist"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

