"""
应急预案 API 路由模块 (简化版)
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.sop_service import SOPService
from app.core import get_current_admin
from app.models import User

router = APIRouter()


@router.get("")
async def get_sops(db: AsyncSession = Depends(get_db)) -> List[Any]:
    """获取所有应急预案（公开接口）"""
    return await SOPService.get_all(db)


@router.get("/{sop_id}")
async def get_sop(sop_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """获取单个应急预案详情"""
    sop = await SOPService.get_by_id(db, sop_id)
    if not sop:
        raise HTTPException(status_code=404, detail="应急预案不存在")
    return sop


@router.post("")
async def create_sop(data: dict, current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)) -> Any:
    """创建应急预案（仅管理员）"""
    return await SOPService.create(db, data)


@router.put("/{sop_id}")
async def update_sop(sop_id: str, data: dict, current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)) -> Any:
    """更新应急预案（仅管理员）"""
    sop = await SOPService.update(db, sop_id, data)
    if not sop:
        raise HTTPException(status_code=404, detail="应急预案不存在")
    return sop


@router.delete("/{sop_id}")
async def delete_sop(sop_id: str, current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    """删除应急预案（仅管理员）"""
    if not await SOPService.delete(db, sop_id):
        raise HTTPException(status_code=404, detail="应急预案不存在")
    return {"message": "删除成功"}
