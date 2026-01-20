"""
服务请求 API 路由模块 (更新以匹配实际数据库)
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.service_request_service import ServiceRequestService
from app.core import get_current_user, get_current_admin
from app.models import User

router = APIRouter()


@router.get("")
async def get_service_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Any]:
    """获取当前用户的服务请求列表"""
    return await ServiceRequestService.get_by_user(db, current_user.id)


@router.get("/{request_id}")
async def get_service_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """获取单个服务请求详情"""
    request = await ServiceRequestService.get_by_id(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="服务请求不存在")
    return request


@router.post("")
async def create_service_request(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """提交服务请求"""
    return await ServiceRequestService.create(db, current_user.id, data)


@router.put("/{request_id}")
async def update_service_request(
    request_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """更新服务请求"""
    request = await ServiceRequestService.update(db, request_id, data)
    if not request:
        raise HTTPException(status_code=404, detail="服务请求不存在")
    return request


@router.delete("/{request_id}")
async def delete_service_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除服务请求"""
    if not await ServiceRequestService.delete(db, request_id):
        raise HTTPException(status_code=404, detail="服务请求不存在")
    return {"message": "删除成功"}


# ============ 管理端接口 ============

@router.get("/admin/all")
async def get_all_service_requests(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> List[Any]:
    """获取所有服务请求（仅管理员）"""
    return await ServiceRequestService.get_all(db)


@router.put("/admin/{request_id}/status")
async def update_service_request_status(
    request_id: str,
    status: str = Query(...),
    admin_response: str = Query(None),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """更新服务请求状态（仅管理员）"""
    request = await ServiceRequestService.update_status(db, request_id, status, admin_response)
    if not request:
        raise HTTPException(status_code=404, detail="服务请求不存在")
    return {"message": "状态更新成功", "status": status}


@router.delete("/admin/rejected")
async def delete_rejected_requests(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """批量删除已驳回的服务请求（仅管理员）"""
    deleted_count = await ServiceRequestService.delete_by_status(db, "REJECTED")
    return {"message": f"已删除 {deleted_count} 条已驳回记录"}
