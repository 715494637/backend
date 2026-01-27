"""
催收记录 API 路由模块 (更新以匹配实际数据库)
"""

from typing import List, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.collection_service import CollectionService
from app.core import get_current_user
from app.models import User

router = APIRouter()


class CollectionCreateSchema(BaseModel):
    """创建催收记录的请求模型"""
    owner_name: str
    room_number: str
    amount: float
    arrears_months: Optional[int] = 0


class CollectionUpdateSchema(BaseModel):
    """更新催收记录的请求模型"""
    owner_name: Optional[str] = None
    room_number: Optional[str] = None
    amount: Optional[float] = None


@router.get("")
async def get_collections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Any]:
    """获取当前用户的催收记录列表"""
    return await CollectionService.get_by_user(db, current_user.id)


@router.post("")
async def create_collection(
    data: CollectionCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """创建新的催收记录"""
    return await CollectionService.create(db, current_user.id, data.model_dump())


@router.put("/{record_id}")
async def update_collection(
    record_id: str,
    data: CollectionUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """更新催收记录"""
    result = await CollectionService.update(db, record_id, data.model_dump())
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
