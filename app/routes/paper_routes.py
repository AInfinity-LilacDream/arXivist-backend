from fastapi import APIRouter, Query, Path
from datetime import date
from typing import Optional
from app.models.paper import PaperListData, Paper, AISummary, AIScoreTaskStatus, AIScoreTaskCreate
from app.models.response import ApiResponse
from app.services.arxiv_service import ArxivService
from app.services.ai_service import ai_service
from app.services.task_service import task_service

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


@router.get("/{arxiv_id}", response_model=ApiResponse[Paper])
async def get_paper_detail(
    arxiv_id: str = Path(..., description="arXiv ID，例如：2511.11570")
):
    """根据 arXiv ID 获取论文详情"""
    try:
        paper = ArxivService.fetch_paper_by_id(arxiv_id)
        
        if paper is None:
            return ApiResponse(
                code=404,
                message=f"未找到 arXiv ID 为 {arxiv_id} 的论文",
                data=None
            )
        
        return ApiResponse(
            code=200,
            message="获取论文详情成功",
            data=paper
        )
    except Exception as e:
        return ApiResponse(
            code=500,
            message=f"获取论文详情失败: {str(e)}",
            data=None
        )


@router.get("/{arxiv_id}/ai-score", response_model=ApiResponse[AISummary])
async def get_paper_ai_score(
    arxiv_id: str = Path(..., description="arXiv ID，例如：2511.11570")
):
    """获取论文的AI评分（同步版本，会阻塞直到完成）"""
    try:
        # 先获取论文基本信息
        paper = ArxivService.fetch_paper_by_id(arxiv_id)
        
        if paper is None:
            return ApiResponse(
                code=404,
                message=f"未找到 arXiv ID 为 {arxiv_id} 的论文",
                data=None
            )
        
        ai_summary = ai_service.generate(paper)
        
        if ai_summary is None:
            return ApiResponse(
                code=500,
                message="AI评分生成失败，请稍后重试",
                data=None
            )
        
        return ApiResponse(
            code=200,
            message="获取AI评分成功",
            data=ai_summary
        )
    except Exception as e:
        return ApiResponse(
            code=500,
            message=f"获取AI评分失败: {str(e)}",
            data=None
        )


@router.post("/{arxiv_id}/ai-score/async", response_model=ApiResponse[AIScoreTaskCreate])
async def start_ai_score_task(
    arxiv_id: str = Path(..., description="arXiv ID，例如：2511.11570")
):
    """启动异步AI评分任务"""
    try:
        task_id = task_service.create_task(arxiv_id)
        
        # 异步提交任务到 worker 池
        await task_service.start_task(task_id, arxiv_id)
        
        return ApiResponse(
            code=200,
            message="AI评分任务已启动",
            data=AIScoreTaskCreate(
                task_id=task_id,
                arxiv_id=arxiv_id,
                message="任务已启动，请使用任务ID查询评分状态"
            )
        )
    except Exception as e:
        return ApiResponse(
            code=500,
            message=f"启动AI评分任务失败: {str(e)}",
            data=None
        )


@router.get("/ai-score/tasks/{task_id}", response_model=ApiResponse[AIScoreTaskStatus])
async def get_ai_score_task_status(
    task_id: str = Path(..., description="任务ID")
):
    """查询AI评分任务状态"""
    try:
        task_info = task_service.get_task(task_id)
        
        if task_info is None:
            return ApiResponse(
                code=404,
                message=f"未找到任务ID为 {task_id} 的任务",
                data=None
            )
        
        # 构建响应数据
        task_status = AIScoreTaskStatus(
            task_id=task_info.task_id,
            arxiv_id=task_info.arxiv_id,
            status=task_info.status.value,
            created_at=task_info.created_at,
            completed_at=task_info.completed_at,
            result=task_info.result,
            error_message=task_info.error_message
        )
        
        return ApiResponse(
            code=200,
            message="获取任务状态成功",
            data=task_status
        )
    except Exception as e:
        return ApiResponse(
            code=500,
            message=f"获取任务状态失败: {str(e)}",
            data=None
        )

