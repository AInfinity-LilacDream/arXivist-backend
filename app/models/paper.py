from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Author(BaseModel):
    """作者模型"""
    name: str


class Paper(BaseModel):
    """论文模型"""
    arxiv_id: str = Field(..., description="arXiv ID")
    title: str = Field(..., description="论文标题")
    authors: List[str] = Field(..., description="作者列表")
    summary: str = Field(..., description="摘要")
    published: datetime = Field(..., description="提交日期")
    updated: Optional[datetime] = Field(None, description="最后更新日期")
    pdf_url: str = Field(..., description="PDF 链接")
    categories: List[str] = Field(default_factory=list, description="分类列表")
    entry_id: str = Field(..., description="arXiv 条目 ID")


class PaperListResponse(BaseModel):
    """论文列表响应模型"""
    papers: List[Paper] = Field(..., description="论文列表")
    total: int = Field(..., description="论文总数")
    date_range: str = Field(..., description="查询的日期范围")

