"""
文档模板 API 路由模块

提供文档模板的查询、创建、更新和删除功能
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db import get_db
from app.schemas import (
    DocumentTemplateCreate,
    DocumentTemplate as DocumentTemplateSchema
)
from app.services import DocumentService
from app.core import get_current_admin
from app.models import User

router = APIRouter()


@router.get("", response_model=List[DocumentTemplateSchema])
async def get_documents(db: AsyncSession = Depends(get_db)):
    """
    获取所有文档模板列表

    Args:
        db: 异步数据库会话

    Returns:
        List[DocumentTemplate]: 文档模板列表
    """
    return await DocumentService.get_documents(db)


@router.get("/categories")
async def get_document_categories(db: AsyncSession = Depends(get_db)):
    """
    获取文档分类列表

    Args:
        db: 异步数据库会话

    Returns:
        List[str]: 分类列表
    """
    result = await db.execute(select(func.distinct(DocumentTemplate.category)))
    categories = [row[0] for row in result.fetchall() if row[0]]
    # 确保包含默认分类
    default_categories = ["全部", "前介承接", "业户服务", "外包管理", "纠纷告知"]
    all_categories = list(set(categories + default_categories))
    return sorted(all_categories, key=lambda x: default_categories.index(x) if x in default_categories else 999)


@router.post("", response_model=DocumentTemplateSchema)
async def create_document(
    doc_data: DocumentTemplateCreate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的文档模板（仅管理员）

    Args:
        doc_data: 文档模板创建数据
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        DocumentTemplate: 创建的文档模板对象

    Raises:
        HTTPException: 非管理员用户访问时抛出 403 错误
    """
    return await DocumentService.create_document(db, doc_data)


@router.put("/{doc_id}", response_model=DocumentTemplateSchema)
async def update_document(
    doc_id: str,
    doc_data: DocumentTemplateCreate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    更新文档模板（仅管理员）

    Args:
        doc_id: 文档模板ID
        doc_data: 更新数据
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        DocumentTemplate: 更新后的文档模板对象

    Raises:
        HTTPException: 非管理员用户访问时抛出 403 错误
        HTTPException: 文档不存在时抛出 404 错误
    """
    return await DocumentService.update_document(db, doc_id, doc_data)


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    删除文档模板（仅管理员）

    Args:
        doc_id: 文档模板ID
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        dict: 删除结果消息

    Raises:
        HTTPException: 非管理员用户访问时抛出 403 错误
        HTTPException: 文档不存在时抛出 404 错误
    """
    await DocumentService.delete_document(db, doc_id)
    return {"message": "文档删除成功"}