"""
VIP权益 API 路由模块 (更新以匹配实际数据库)
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.vip_service import VipService
from app.core import get_current_user, get_current_admin
from app.models import User

router = APIRouter()


# 请求体模型
class SelectProjectsRequest(BaseModel):
    project_ids: List[str]


@router.get("/levels")
async def get_vip_levels(db: AsyncSession = Depends(get_db)) -> List[Any]:
    """获取VIP等级配置（公开接口）"""
    return await VipService.get_levels(db)


@router.get("/levels/{level_id}")
async def get_vip_level(level_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """获取单个VIP等级详情"""
    level = await VipService.get_level_by_id(db, level_id)
    if not level:
        raise HTTPException(status_code=404, detail="VIP等级不存在")
    return level


@router.post("/levels")
async def create_vip_level(
    data: dict,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """创建VIP等级（仅管理员）"""
    return await VipService.create_level(db, data)


@router.put("/levels/{level_id}")
async def update_vip_level(
    level_id: str,
    data: dict,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """更新VIP等级（仅管理员）"""
    level = await VipService.update_level(db, level_id, data)
    if not level:
        raise HTTPException(status_code=404, detail="VIP等级不存在")
    return level


@router.delete("/levels/{level_id}")
async def delete_vip_level(
    level_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """删除VIP等级（仅管理员）"""
    if not await VipService.delete_level(db, level_id):
        raise HTTPException(status_code=404, detail="VIP等级不存在")
    return {"message": "删除成功"}


@router.get("/stats")
async def get_vip_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """获取企业统计数据（普通用户获取自己的，管理员可查看任意企业）"""
    # 管理员可以查看任意企业的统计数据
    enterprise_name = current_user.enterprise_name
    if not enterprise_name:
        raise HTTPException(status_code=400, detail="用户未关联企业")
    return await VipService.get_stats(db, enterprise_name)


@router.get("/stats/{enterprise_name}")
async def get_enterprise_stats_by_name(
    enterprise_name: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """管理员获取指定企业的统计数据"""
    return await VipService.get_stats(db, enterprise_name)


@router.put("/stats")
async def update_vip_stats(
    data: dict,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """更新企业统计数据（仅管理员）"""
    enterprise_name = data.get("enterprise_name")
    if not enterprise_name:
        raise HTTPException(status_code=400, detail="缺少企业名称")
    return await VipService.update_stats(db, enterprise_name, data)


@router.put("/select-projects")
async def select_projects(
    request: SelectProjectsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """选择专项服务"""
    await VipService.select_projects(db, current_user.id, request.project_ids)
    return {"message": "保存成功"}
