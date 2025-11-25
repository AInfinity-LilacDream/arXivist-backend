from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import json
from app.config.database import Base


class Collection(Base):
    """收藏夹数据库模型"""
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关联关系
    user = relationship("User", backref="collections")
    papers = relationship("CollectionPaper", back_populates="collection", cascade="all, delete-orphan", lazy="dynamic")


class CollectionPaper(Base):
    """收藏夹中的论文关联表"""
    __tablename__ = "collection_papers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey('collections.id', ondelete='CASCADE'), nullable=False, index=True)
    arxiv_id = Column(String(50), nullable=False, index=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关联关系
    collection = relationship("Collection", back_populates="papers")
    
    __table_args__ = (
        UniqueConstraint('collection_id', 'arxiv_id', name='uq_collection_paper'),
    )

