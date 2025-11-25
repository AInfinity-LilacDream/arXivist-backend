from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.paper import Paper


class CollectionCreate(BaseModel):
    """创建收藏夹请求模型"""
    name: str = Field(..., min_length=1, max_length=255, description="收藏夹名称")
    description: Optional[str] = Field(None, max_length=2000, description="收藏夹描述")


class CollectionUpdate(BaseModel):
    """更新收藏夹请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="收藏夹名称")
    description: Optional[str] = Field(None, max_length=2000, description="收藏夹描述")


class CollectionInfo(BaseModel):
    """收藏夹基本信息模型"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    paper_count: int = Field(..., description="论文数量")

    class Config:
        from_attributes = True


class CollectionPaperInfo(Paper):
    """收藏夹中的论文信息模型"""
    added_at: datetime = Field(..., description="收藏时间")


class CollectionDetail(BaseModel):
    """收藏夹详情模型"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    papers: List[CollectionPaperInfo] = Field(default_factory=list, description="论文列表")
    paper_count: int = Field(..., description="论文数量")

    class Config:
        from_attributes = True

