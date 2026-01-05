"""
文档模板业务逻辑服务模块

提供文档模板的查询、创建、更新和删除等业务逻辑
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models import DocumentTemplate
from app.schemas import DocumentTemplateCreate
from app.utils import logger


class DocumentService:
    """文档模板业务逻辑服务"""

    @staticmethod
    async def get_documents(db: AsyncSession) -> List[DocumentTemplate]:
        """
        获取所有文档模板列表

        Args:
            db: 异步数据库会话

        Returns:
            List[DocumentTemplate]: 文档模板列表
        """
        result = await db.execute(select(DocumentTemplate))
        documents = result.scalars().all()
        logger.info(f"获取文档模板列表，共 {len(documents)} 个")
        return documents

    @staticmethod
    async def create_document(db: AsyncSession, doc_data: DocumentTemplateCreate) -> DocumentTemplate:
        """
        创建新的文档模板

        Args:
            db: 异步数据库会话
            doc_data: 文档模板创建数据

        Returns:
            DocumentTemplate: 创建的文档模板对象
        """
        new_doc = DocumentTemplate(
            title=doc_data.title,
            category=doc_data.category,
            description=doc_data.description,
            content=doc_data.content,
            file_url=doc_data.file_url
        )

        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)

        logger.info(f"新文档模板 {new_doc.title} 创建成功")
        return new_doc

    @staticmethod
    async def update_document(db: AsyncSession, doc_id: str, doc_data: DocumentTemplateCreate) -> DocumentTemplate:
        """
        更新文档模板

        Args:
            db: 异步数据库会话
            doc_id: 文档模板ID
            doc_data: 更新数据

        Returns:
            DocumentTemplate: 更新后的文档模板对象

        Raises:
            HTTPException: 文档不存在时抛出
        """
        result = await db.execute(select(DocumentTemplate).where(DocumentTemplate.id == doc_id))
        doc = result.scalar_one_or_none()

        if not doc:
            logger.error(f"文档模板 {doc_id} 不存在")
            raise HTTPException(status_code=404, detail="文档不存在")

        # 更新文档模板信息
        doc.title = doc_data.title
        doc.category = doc_data.category
        doc.description = doc_data.description
        doc.content = doc_data.content
        doc.file_url = doc_data.file_url

        await db.commit()
        await db.refresh(doc)

        logger.info(f"文档模板 {doc.title} 更新成功")
        return doc

    @staticmethod
    async def delete_document(db: AsyncSession, doc_id: str) -> None:
        """
        删除文档模板

        Args:
            db: 异步数据库会话
            doc_id: 文档模板ID

        Raises:
            HTTPException: 文档不存在时抛出
        """
        result = await db.execute(select(DocumentTemplate).where(DocumentTemplate.id == doc_id))
        doc = result.scalar_one_or_none()

        if not doc:
            logger.error(f"文档模板 {doc_id} 不存在")
            raise HTTPException(status_code=404, detail="文档不存在")

        title = doc.title
        await db.delete(doc)
        await db.commit()

        logger.info(f"文档模板 {title} 删除成功")