"""
法务体检 API 路由模块 (更新以匹配实际数据库)
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.health_check_service import HealthCheckService
from app.core import get_current_user, get_current_admin
from app.models import User

router = APIRouter()


@router.get("")
async def get_health_check_sections(db: AsyncSession = Depends(get_db)) -> List[Any]:
    """获取法务体检题目（公开接口）"""
    return await HealthCheckService.get_all(db)


@router.get("/{section_id}")
async def get_health_check_section(
    section_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """获取单个法务体检板块详情"""
    section = await HealthCheckService.get_by_id(db, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="法务体检板块不存在")
    return section


@router.post("")
async def create_health_check_section(
    data: dict,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """创建法务体检题目（仅管理员）"""
    return await HealthCheckService.create(db, data)


@router.put("/{section_id}")
async def update_health_check_section(
    section_id: str,
    data: dict,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """更新法务体检题目（仅管理员）"""
    section = await HealthCheckService.update(db, section_id, data)
    if not section:
        raise HTTPException(status_code=404, detail="法务体检板块不存在")
    return section


@router.delete("/{section_id}")
async def delete_health_check_section(
    section_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """删除法务体检题目（仅管理员）"""
    if not await HealthCheckService.delete(db, section_id):
        raise HTTPException(status_code=404, detail="法务体检板块不存在")
    return {"message": "删除成功"}
