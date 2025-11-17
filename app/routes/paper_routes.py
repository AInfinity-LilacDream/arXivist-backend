from fastapi import APIRouter, HTTPException, Query
from datetime import date
from typing import Optional
from app.models.paper import PaperListResponse
from app.services.arxiv_service import ArxivService

router = APIRouter(prefix="/api/papers", tags=["papers"])


@router.get("/", response_model=PaperListResponse)
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
        
        return PaperListResponse(
            papers=papers,
            total=len(papers),
            date_range=date_range
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取论文失败: {str(e)}")

