"""
装修巡查 API 路由模块 (更新以匹配实际数据库)
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.renovation_service import RenovationService
from app.core import get_current_user, get_current_admin
from app.models import User

router = APIRouter()


@router.get("")
async def get_renovation_records(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Any]:
    """获取当前用户的装修巡查记录"""
    return await RenovationService.get_by_user(db, current_user.id)


@router.get("/{record_id}")
async def get_renovation_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """获取单个装修巡查记录详情"""
    record = await RenovationService.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.post("")
async def create_renovation_record(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """提交装修巡查记录"""
    return await RenovationService.create(db, current_user.id, data)


@router.put("/{record_id}")
async def update_renovation_record(
    record_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """更新装修巡查记录"""
    record = await RenovationService.update(db, record_id, data)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.delete("/{record_id}")
async def delete_renovation_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除装修巡查记录"""
    if not await RenovationService.delete(db, record_id):
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"message": "删除成功"}
