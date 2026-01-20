"""
服务请求模块 (更新以匹配实际数据库)
"""

from typing import List, Optional
import datetime as dt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ServiceRequest as ServiceRequestModel, User as UserModel


def _parse_timestamp(value) -> int:
    """将 MySQL DATETIME 字符串或 datetime 对象转换为 Unix 时间戳（秒）"""
    if not value:
        return 0
    try:
        # 如果已经是 datetime 对象（数据库返回）
        if isinstance(value, dt.datetime):
            return int(value.timestamp())
        # 如果是纯数字字符串（时间戳）
        if isinstance(value, str) and value.isdigit():
            ts = int(value)
            # 如果时间戳小于 10 亿（2001年之前），说明是秒，否则是毫秒
            if ts < 1_000_000_000:
                return ts
            else:
                return ts // 1000
        # 解析 MySQL DATETIME 格式字符串
        if isinstance(value, str):
            return int(dt.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').timestamp())
        return 0
    except Exception as e:
        print(f"[WARN] Failed to parse timestamp: {value}, error: {e}")
        return 0


class ServiceRequestService:
    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: str) -> List[dict]:
        result = await db.execute(
            select(ServiceRequestModel).where(ServiceRequestModel.user_id == user_id)
        )
        requests = result.scalars().all()
        return [
            {
                "id": r.id,
                "userId": r.user_id,
                "requestType": r.request_type,
                "title": r.title,
                "content": r.description,
                "status": r.status,
                "timestamp": _parse_timestamp(r.created_at)
            }
            for r in requests
        ]

    @staticmethod
    async def get_all(db: AsyncSession) -> List[dict]:
        result = await db.execute(select(ServiceRequestModel))
        requests = result.scalars().all()

        # 获取所有用户ID
        user_ids = list(set(r.user_id for r in requests))
        user_result = await db.execute(select(UserModel).where(UserModel.id.in_(user_ids)))
        users = {u.id: u.username for u in user_result.scalars().all()}

        return [
            {
                "id": r.id,
                "userId": r.user_id,
                "username": users.get(r.user_id, "未知用户"),
                "enterpriseName": r.enterprise_name or "",
                "requestType": r.request_type,
                "title": r.title,
                "content": r.description,
                "status": r.status,
                "priority": r.priority,
                "timestamp": _parse_timestamp(r.created_at)
            }
            for r in requests
        ]

    @staticmethod
    async def get_by_id(db: AsyncSession, request_id: str) -> Optional[dict]:
        result = await db.execute(select(ServiceRequestModel).where(ServiceRequestModel.id == request_id))
        request = result.scalar_one_or_none()
        if not request:
            return None
        return {
            "id": request.id,
            "user_id": request.user_id,
            "request_type": request.request_type,
            "description": request.description,
            "status": request.status
        }

    @staticmethod
    async def create(db: AsyncSession, user_id: str, data: dict) -> dict:
        timestamp = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        request = ServiceRequestModel(
            user_id=user_id,
            request_type=data.get("request_type", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            status="PENDING",
            created_at=timestamp
        )
        db.add(request)
        await db.commit()
        await db.refresh(request)
        return {
            "id": request.id,
            "userId": request.user_id,
            "requestType": request.request_type,
            "title": request.title,
            "content": request.description,
            "status": request.status,
            "timestamp": _parse_timestamp(request.created_at)
        }

    @staticmethod
    async def update(db: AsyncSession, request_id: str, data: dict) -> Optional[dict]:
        result = await db.execute(select(ServiceRequestModel).where(ServiceRequestModel.id == request_id))
        request = result.scalar_one_or_none()
        if not request:
            return None
        if "description" in data:
            request.description = data["description"]
        if "status" in data:
            request.status = data["status"]
        await db.commit()
        return {
            "id": request.id,
            "user_id": request.user_id,
            "status": request.status
        }

    @staticmethod
    async def delete(db: AsyncSession, request_id: str) -> bool:
        result = await db.execute(select(ServiceRequestModel).where(ServiceRequestModel.id == request_id))
        request = result.scalar_one_or_none()
        if not request:
            return False
        await db.delete(request)
        await db.commit()
        return True

    @staticmethod
    async def update_status(db: AsyncSession, request_id: str, status: str, admin_response: str = None) -> Optional[dict]:
        result = await db.execute(select(ServiceRequestModel).where(ServiceRequestModel.id == request_id))
        request = result.scalar_one_or_none()
        if not request:
            return None
        request.status = status
        if admin_response:
            request.admin_response = admin_response
        await db.commit()
        return {
            "id": request.id,
            "status": request.status,
            "admin_response": request.admin_response
        }

    @staticmethod
    async def delete_by_status(db: AsyncSession, status: str) -> int:
        """批量删除指定状态的请求，返回删除数量"""
        result = await db.execute(select(ServiceRequestModel).where(ServiceRequestModel.status == status))
        requests = result.scalars().all()
        count = len(requests)
        for request in requests:
            await db.delete(request)
        await db.commit()
        return count
