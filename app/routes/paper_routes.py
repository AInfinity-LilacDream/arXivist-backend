from fastapi import APIRouter, Query, Path
from datetime import date
from typing import Optional
from app.models.paper import PaperListData, PaperDetail
from app.models.response import ApiResponse
from app.services.arxiv_service import ArxivService

router = APIRouter(prefix="/api/papers", tags=["papers"])


@router.get("/", response_model=ApiResponse[PaperListData])
async def get_papers(
    start_date: Optional[date] = Query(None, description="开始日期，格式：YYYY-MM-DD，默认为当日。查询从该日期到当天的论文"),
    max_results: Optional[int] = Query(100, ge=1, le=2000, description="最大返回数量，默认100，最大2000"),
    category: Optional[str] = Query(None, description="论文类别，如 cs.AI, cs.CV 等")
):
    """获取 arXiv 论文列表"""
    try:
        papers = ArxivService.fetch_papers(
            start_date=start_date,
            max_results=max_results,
            category=category
        )
        
        # 构建日期范围字符串
        today = date.today()
        actual_start = start_date if start_date else today
        
        if actual_start == today:
            date_range = f"{actual_start.strftime('%Y-%m-%d')}"
        else:
            date_range = f"{actual_start.strftime('%Y-%m-%d')} 至 {today.strftime('%Y-%m-%d')}"
        
        return ApiResponse(
            code=200,
            message="获取论文成功",
            data=PaperListData(
                papers=papers,
                total=len(papers),
                date_range=date_range
            )
        )
    except Exception as e:
        return ApiResponse(
            code=500,
            message=f"获取论文失败: {str(e)}",
            data=None
        )


@router.get("/{arxiv_id}", response_model=ApiResponse[PaperDetail])
async def get_paper_detail(
    arxiv_id: str = Path(..., description="arXiv ID，例如：2511.11570")
):
    """根据 arXiv ID 获取论文详情"""
    try:
        paper_detail = ArxivService.fetch_paper_by_id(arxiv_id)
        
        if paper_detail is None:
            return ApiResponse(
                code=404,
                message=f"未找到 arXiv ID 为 {arxiv_id} 的论文",
                data=None
            )
        
        return ApiResponse(
            code=200,
            message="获取论文详情成功",
            data=paper_detail
        )
    except Exception as e:
        return ApiResponse(
            code=500,
            message=f"获取论文详情失败: {str(e)}",
            data=None
        )

