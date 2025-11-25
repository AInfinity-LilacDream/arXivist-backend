from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import arxiv
from app.models.collection import Collection, CollectionPaper
from app.models.collection_schema import CollectionCreate, CollectionUpdate
from app.models.user import User


class CollectionService:
    """收藏夹服务类"""

    @staticmethod
    def create_collection(db: Session, user_id: int, collection_data: CollectionCreate) -> Collection:
        """创建收藏夹"""
        new_collection = Collection(
            user_id=user_id,
            name=collection_data.name,
            description=collection_data.description
        )
        db.add(new_collection)
        db.commit()
        db.refresh(new_collection)
        return new_collection

    @staticmethod
    def get_user_collections(db: Session, user_id: int) -> List[Collection]:
        """获取用户的所有收藏夹"""
        collections = db.query(Collection).filter(
            Collection.user_id == user_id
        ).order_by(Collection.updated_at.desc()).all()
        return collections

    @staticmethod
    def get_collection_by_id(db: Session, collection_id: int, user_id: int) -> Optional[Collection]:
        """根据ID获取收藏夹"""
        collection = db.query(Collection).filter(
            Collection.id == collection_id,
            Collection.user_id == user_id
        ).first()
        return collection

    @staticmethod
    def update_collection(
        db: Session,
        collection_id: int,
        user_id: int,
        collection_data: CollectionUpdate
    ) -> Collection:
        """更新收藏夹"""
        collection = CollectionService.get_collection_by_id(db, collection_id, user_id)
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收藏夹不存在"
            )

        if collection_data.name is not None:
            collection.name = collection_data.name
        if collection_data.description is not None:
            collection.description = collection_data.description

        db.commit()
        db.refresh(collection)
        return collection

    @staticmethod
    def delete_collection(db: Session, collection_id: int, user_id: int) -> None:
        """删除收藏夹"""
        collection = CollectionService.get_collection_by_id(db, collection_id, user_id)
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收藏夹不存在"
            )

        db.delete(collection)
        db.commit()

    @staticmethod
    def add_paper_to_collection(
        db: Session,
        collection_id: int,
        user_id: int,
        arxiv_id: str
    ) -> CollectionPaper:
        """添加论文到收藏夹"""
        # 验证收藏夹所有权
        collection = CollectionService.get_collection_by_id(db, collection_id, user_id)
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收藏夹不存在"
            )

        # 检查论文是否已在收藏夹中
        existing_paper = db.query(CollectionPaper).filter(
            CollectionPaper.collection_id == collection_id,
            CollectionPaper.arxiv_id == arxiv_id
        ).first()

        if existing_paper:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="论文已在该收藏夹中"
            )

        # 验证论文是否存在
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            paper_list = list(search.results())
            if not paper_list:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"未找到 arXiv ID 为 {arxiv_id} 的论文"
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"验证论文失败: {str(e)}"
            )

        # 创建收藏夹论文记录
        collection_paper = CollectionPaper(
            collection_id=collection_id,
            arxiv_id=arxiv_id
        )

        db.add(collection_paper)
        db.commit()
        db.refresh(collection_paper)
        return collection_paper

    @staticmethod
    def remove_paper_from_collection(
        db: Session,
        collection_id: int,
        user_id: int,
        arxiv_id: str
    ) -> None:
        """从收藏夹删除论文"""
        # 验证收藏夹所有权
        collection = CollectionService.get_collection_by_id(db, collection_id, user_id)
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收藏夹不存在"
            )

        # 查找论文
        paper = db.query(CollectionPaper).filter(
            CollectionPaper.collection_id == collection_id,
            CollectionPaper.arxiv_id == arxiv_id
        ).first()

        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文不在该收藏夹中"
            )

        db.delete(paper)
        db.commit()

    @staticmethod
    def get_collection_papers(db: Session, collection_id: int, user_id: int) -> List[CollectionPaper]:
        """获取收藏夹中的所有论文"""
        # 验证收藏夹所有权
        collection = CollectionService.get_collection_by_id(db, collection_id, user_id)
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收藏夹不存在"
            )

        papers = db.query(CollectionPaper).filter(
            CollectionPaper.collection_id == collection_id
        ).order_by(CollectionPaper.added_at.desc()).all()
        return papers

