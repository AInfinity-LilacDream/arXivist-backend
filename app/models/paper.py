from datetime import datetime
from typing import List, Optional, Literal
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


class PaperListData(BaseModel):
    """论文列表数据模型"""
    papers: List[Paper] = Field(..., description="论文列表")
    total: int = Field(..., description="论文总数")
    date_range: str = Field(..., description="查询的日期范围")


class TokenUsage(BaseModel):
    """Token 使用情况模型"""
    prompt_tokens: Optional[int] = Field(None, description="Prompt tokens 数量")
    completion_tokens: Optional[int] = Field(None, description="Completion tokens 数量")
    total_tokens: Optional[int] = Field(None, description="Total tokens 数量")
    reasoning_length: Optional[int] = Field(None, description="推理长度")
    content_length: Optional[int] = Field(None, description="内容长度")


class AIScoreDetail(BaseModel):
    """AI 评分详情模型"""
    total_score: Optional[float] = Field(None, ge=0, le=100, description="总分（0-100分）")
    innovation_score: Optional[float] = Field(None, ge=0, le=30, description="创新性评分（0-30分）")
    technical_depth_score: Optional[float] = Field(None, ge=0, le=25, description="技术深度评分（0-25分）")
    practical_value_score: Optional[float] = Field(None, ge=0, le=20, description="实用价值评分（0-20分）")
    experiments_score: Optional[float] = Field(None, ge=0, le=15, description="实验充分性评分（0-15分）")
    writing_score: Optional[float] = Field(None, ge=0, le=10, description="可理解性/写作质量评分（0-10分）")
    summary: Optional[str] = Field(None, description="论文总结")
    strengths: Optional[List[str]] = Field(default_factory=list, description="论文优点列表")
    weaknesses: Optional[List[str]] = Field(default_factory=list, description="论文缺点列表")
    recommendation: Optional[Literal["推荐", "强烈推荐"]] = Field(None, description="推荐建议")
    reasoning: Optional[str] = Field(None, description="评分推理过程")
    paper_id: Optional[str] = Field(None, description="论文ID")
    api_model: Optional[str] = Field(None, description="API模型名称")
    api_request_id: Optional[str] = Field(None, description="API请求ID")
    api_created_timestamp: Optional[int] = Field(None, description="API创建时间戳")


class AISummary(BaseModel):
    """AI 生成的摘要模型"""
    score: Optional[float] = Field(None, ge=0, le=100, description="AI 综合评分（0-100分）")
    detail: Optional[AIScoreDetail] = Field(None, description="AI 评分详情")
    token_usage: Optional[TokenUsage] = Field(None, description="Token 使用情况")


class PaperDetail(Paper):
    """论文详情模型，扩展 Paper 模型"""
    ai_summary: Optional[AISummary] = Field(None, description="AI 生成的摘要")

