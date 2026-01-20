"""
催收记录 API 路由模块 (更新以匹配实际数据库)
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.collection_service import CollectionService
from app.core import get_current_user
from app.models import User

router = APIRouter()


@router.get("")
async def get_collections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Any]:
    """获取当前用户的催收记录列表"""
    return await CollectionService.get_by_user(db, current_user.id)


@router.post("")
async def create_collection(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """创建新的催收记录"""
    return await CollectionService.create(db, current_user.id, data)


@router.put("/{record_id}")
async def update_collection(
    record_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """更新催收记录"""
    result = await CollectionService.update(db, record_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="记录不存在")
    return result


@router.delete("/{record_id}")
async def delete_collection(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除催收记录"""
    if not await CollectionService.delete(db, record_id):
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"message": "删除成功"}


@router.get("/{record_id}")
async def get_collection(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """获取单个催收记录详情"""
    result = await CollectionService.get_by_id(db, record_id)
    if not result:
        raise HTTPException(status_code=404, detail="记录不存在")
    return result
