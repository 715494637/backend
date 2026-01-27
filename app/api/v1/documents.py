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
    DocumentTemplate as DocumentTemplateSchema,
    CategoryCreate,
    DocCategoryCreate as DocCategorySchemaCreate
)
from app.services import DocumentService
from app.core import get_current_admin
from app.models import User, DocumentTemplate, DocCategory

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
    # 从 doc_categories 表获取分类
    result = await db.execute(select(DocCategory.name).order_by(DocCategory.name))
    categories = [row[0] for row in result.fetchall() if row[0]]

    # 如果数据库为空，返回默认分类并写入数据库
    default_categories = ["前介承接", "违规整改", "内部管理", "风险防范", "催收增收"]
    if not categories:
        for cat_name in default_categories:
            new_category = DocCategory(name=cat_name)
            db.add(new_category)
        await db.commit()
        categories = default_categories

    # 始终添加"全部"选项在最前面
    all_categories = ["全部"] + categories
    return all_categories


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


@router.post("/categories")
async def create_category(
    category_data: CategoryCreate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    新增文档分类（仅管理员）

    Args:
        category_data: 分类创建数据
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        dict: 创建结果消息

    Raises:
        HTTPException: 非管理员用户访问时抛出 403 错误
        HTTPException: 分类名称为空时抛出 400 错误
        HTTPException: 分类已存在时抛出 400 错误
    """
    category = category_data.category
    if not category or not category.strip():
        raise HTTPException(status_code=400, detail="分类名称不能为空")

    category = category.strip()

    # 不能创建"全部"分类
    if category == "全部":
        raise HTTPException(status_code=400, detail="不能创建'全部'分类")

    # 检查 doc_categories 表中是否已存在
    result = await db.execute(
        select(DocCategory.name)
    )
    existing_categories = [row[0] for row in result.fetchall() if row[0]]

    if category in existing_categories:
        raise HTTPException(status_code=400, detail="分类已存在")

    # 插入新分类到 doc_categories 表
    new_category = DocCategory(name=category)
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    return {"message": f"分类 '{category}' 创建成功"}


@router.delete("/categories/{category}")
async def delete_category(
    category: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    删除文档分类（仅管理员）

    Args:
        category: 分类名称
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        dict: 删除结果消息

    Raises:
        HTTPException: 非管理员用户访问时抛出 403 错误
        HTTPException: 不能删除"全部"时抛出 400 错误
        HTTPException: 分类不存在时抛出 404 错误
        HTTPException: 该分类下存在文档时抛出 400 错误
    """
    # 不能删除"全部"
    if category == "全部":
        raise HTTPException(status_code=400, detail="不能删除'全部'分类")

    # 检查该分类下是否有文档
    result = await db.execute(
        select(DocumentTemplate).where(DocumentTemplate.category == category)
    )
    docs_with_category = result.scalars().all()

    if docs_with_category:
        raise HTTPException(status_code=400, detail=f"该分类下存在 {len(docs_with_category)} 个文档，无法删除")

    # 从 doc_categories 表中查找并删除分类
    result = await db.execute(
        select(DocCategory).where(DocCategory.name == category)
    )
    category_to_delete = result.scalars().first()

    if not category_to_delete:
        raise HTTPException(status_code=404, detail="分类不存在")

    await db.delete(category_to_delete)
    await db.commit()

    return {"message": f"分类 '{category}' 删除成功"}