"""
专项服务 API 路由模块 (简化版)
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.special_project_service import SpecialProjectService
from app.core import get_current_admin
from app.models import User

router = APIRouter()


@router.get("")
async def get_special_projects(db: AsyncSession = Depends(get_db)) -> List[Any]:
    """获取所有专项服务（公开接口）"""
    return await SpecialProjectService.get_all(db)


@router.get("/{project_id}")
async def get_special_project(project_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """获取单个专项服务详情"""
    project = await SpecialProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="专项服务不存在")
    return project


@router.post("")
async def create_special_project(data: dict, current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)) -> Any:
    """创建专项服务（仅管理员）"""
    return await SpecialProjectService.create(db, data)


@router.put("/{project_id}")
async def update_special_project(project_id: str, data: dict, current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)) -> Any:
    """更新专项服务（仅管理员）"""
    project = await SpecialProjectService.update(db, project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="专项服务不存在")
    return project


@router.delete("/{project_id}")
async def delete_special_project(project_id: str, current_admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    """删除专项服务（仅管理员）"""
    if not await SpecialProjectService.delete(db, project_id):
        raise HTTPException(status_code=404, detail="专项服务不存在")
    return {"message": "删除成功"}
