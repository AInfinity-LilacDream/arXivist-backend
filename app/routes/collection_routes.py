from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.user import User
from app.models.collection import Collection, CollectionPaper
from app.models.collection_schema import (
    CollectionCreate,
    CollectionUpdate,
    CollectionInfo,
    CollectionDetail,
    CollectionPaperInfo
)
from app.models.response import ApiResponse
from app.routes.auth_routes import get_current_user
from app.services.collection_service import CollectionService
from app.services.arxiv_service import ArxivService

router = APIRouter(prefix="/api/collections", tags=["collections"])


def convert_collection_to_info(collection: Collection) -> CollectionInfo:
    """将 Collection 对象转换为 CollectionInfo"""
    paper_count = collection.papers.count() if hasattr(collection.papers, 'count') else len(list(collection.papers))
    return CollectionInfo(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        created_at=collection.created_at,
        updated_at=collection.updated_at,
        paper_count=paper_count
    )




@router.post("", response_model=ApiResponse[CollectionInfo])
async def create_collection(
    collection_data: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建收藏夹"""
    try:
        collection = CollectionService.create_collection(db, current_user.id, collection_data)
        collection_info = convert_collection_to_info(collection)
        return ApiResponse(
            code=201,
            message="收藏夹创建成功",
            data=collection_info
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
            message=f"创建收藏夹失败: {str(e)}",
            data=None
        )


@router.get("", response_model=ApiResponse[List[CollectionInfo]])
async def get_collections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有收藏夹"""
    try:
        collections = CollectionService.get_user_collections(db, current_user.id)
        collections_info = [convert_collection_to_info(c) for c in collections]
        return ApiResponse(
            code=200,
            message="获取收藏夹列表成功",
            data=collections_info
        )
    except Exception as e:
        return ApiResponse(
            code=500,
            message=f"获取收藏夹列表失败: {str(e)}",
            data=None
        )


@router.get("/{collection_id}", response_model=ApiResponse[CollectionDetail])
async def get_collection_detail(
    collection_id: int = Path(..., description="收藏夹ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取收藏夹详情（包含论文列表）"""
    try:
        collection = CollectionService.get_collection_by_id(db, collection_id, current_user.id)
        if not collection:
            return ApiResponse(
                code=404,
                message="收藏夹不存在",
                data=None
            )

        papers = CollectionService.get_collection_papers(db, collection_id, current_user.id)
        # 从 arXiv API 获取论文详情并添加收藏时间
        papers_info = []
        for paper_record in papers:
            try:
                # 从 arXiv 获取论文信息
                paper = ArxivService.fetch_paper_by_id(paper_record.arxiv_id)
                if paper:
                    # 创建 CollectionPaperInfo（Paper + added_at）
                    paper_info = CollectionPaperInfo(
                        arxiv_id=paper.arxiv_id,
                        title=paper.title,
                        authors=paper.authors,
                        summary=paper.summary,
                        published=paper.published,
                        updated=paper.updated,
                        pdf_url=paper.pdf_url,
                        categories=paper.categories,
                        entry_id=paper.entry_id,
                        added_at=paper_record.added_at
                    )
                    papers_info.append(paper_info)
                else:
                    # 如果论文不存在，返回基本信息
                    papers_info.append(CollectionPaperInfo(
                        arxiv_id=paper_record.arxiv_id,
                        title="论文信息获取失败",
                        authors=[],
                        summary=None,
                        published=None,
                        updated=None,
                        pdf_url=None,
                        categories=[],
                        entry_id=None,
                        added_at=paper_record.added_at
                    ))
            except Exception as e:
                # 如果论文获取失败，仍然返回基本信息
                papers_info.append(CollectionPaperInfo(
                    arxiv_id=paper_record.arxiv_id,
                    title="论文信息获取失败",
                    authors=[],
                    summary=None,
                    published=None,
                    updated=None,
                    pdf_url=None,
                    categories=[],
                    entry_id=None,
                    added_at=paper_record.added_at
                ))

        collection_detail = CollectionDetail(
            id=collection.id,
            name=collection.name,
            description=collection.description,
            created_at=collection.created_at,
            updated_at=collection.updated_at,
            papers=papers_info,
            paper_count=len(papers_info)
        )

        return ApiResponse(
            code=200,
            message="获取收藏夹详情成功",
            data=collection_detail
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
            message=f"获取收藏夹详情失败: {str(e)}",
            data=None
        )


@router.put("/{collection_id}", response_model=ApiResponse[CollectionInfo])
async def update_collection(
    collection_id: int = Path(..., description="收藏夹ID"),
    collection_data: CollectionUpdate = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新收藏夹信息"""
    try:
        collection = CollectionService.update_collection(
            db, collection_id, current_user.id, collection_data
        )
        collection_info = convert_collection_to_info(collection)
        return ApiResponse(
            code=200,
            message="更新收藏夹成功",
            data=collection_info
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
            message=f"更新收藏夹失败: {str(e)}",
            data=None
        )


@router.delete("/{collection_id}", response_model=ApiResponse[None])
async def delete_collection(
    collection_id: int = Path(..., description="收藏夹ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除收藏夹"""
    try:
        CollectionService.delete_collection(db, collection_id, current_user.id)
        return ApiResponse(
            code=200,
            message="删除收藏夹成功",
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
            message=f"删除收藏夹失败: {str(e)}",
            data=None
        )


@router.post("/{collection_id}/papers/{arxiv_id}", response_model=ApiResponse[CollectionPaperInfo])
async def add_paper_to_collection(
    collection_id: int = Path(..., description="收藏夹ID"),
    arxiv_id: str = Path(..., description="arXiv ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加论文到收藏夹"""
    try:
        collection_paper = CollectionService.add_paper_to_collection(
            db, collection_id, current_user.id, arxiv_id
        )
        # 从 arXiv 获取论文详情
        paper = ArxivService.fetch_paper_by_id(arxiv_id)
        if not paper:
            return ApiResponse(
                code=404,
                message="未找到论文信息",
                data=None
            )
        # 创建 CollectionPaperInfo（Paper + added_at）
        paper_info = CollectionPaperInfo(
            arxiv_id=paper.arxiv_id,
            title=paper.title,
            authors=paper.authors,
            summary=paper.summary,
            published=paper.published,
            updated=paper.updated,
            pdf_url=paper.pdf_url,
            categories=paper.categories,
            entry_id=paper.entry_id,
            added_at=collection_paper.added_at
        )
        return ApiResponse(
            code=201,
            message="添加论文成功",
            data=paper_info
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
            message=f"添加论文失败: {str(e)}",
            data=None
        )


@router.delete("/{collection_id}/papers/{arxiv_id}", response_model=ApiResponse[None])
async def remove_paper_from_collection(
    collection_id: int = Path(..., description="收藏夹ID"),
    arxiv_id: str = Path(..., description="arXiv ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从收藏夹删除论文"""
    try:
        CollectionService.remove_paper_from_collection(
            db, collection_id, current_user.id, arxiv_id
        )
        return ApiResponse(
            code=200,
            message="删除论文成功",
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
            message=f"删除论文失败: {str(e)}",
            data=None
        )

