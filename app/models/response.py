from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """API 响应基础结构"""
    code: int = Field(..., description="状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

