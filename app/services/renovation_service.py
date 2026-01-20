"""
装修巡查服务模块 (更新以匹配实际数据库)
"""

import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import RenovationRecord as RenovationRecordModel


class RenovationService:
    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: str) -> List[dict]:
        result = await db.execute(
            select(RenovationRecordModel).where(RenovationRecordModel.user_id == user_id)
        )
        records = result.scalars().all()
        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "property_unit": r.property_unit,
                "check_date": r.check_date,
                "check_result": r.check_result,
                "inspector": r.inspector,
                "status": r.status
            }
            for r in records
        ]

    @staticmethod
    async def get_by_id(db: AsyncSession, record_id: str) -> Optional[dict]:
        result = await db.execute(select(RenovationRecordModel).where(RenovationRecordModel.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            return None
        return {
            "id": record.id,
            "user_id": record.user_id,
            "property_unit": record.property_unit,
            "check_date": record.check_date,
            "check_result": record.check_result,
            "inspector": record.inspector
        }

    @staticmethod
    async def create(db: AsyncSession, user_id: str, data: dict) -> dict:
        record = RenovationRecordModel(
            user_id=user_id,
            property_unit=data.get("property_unit", ""),
            check_date=data.get("check_date", ""),
            check_result=data.get("check_result", ""),
            inspector=data.get("inspector", ""),
            status="PENDING"
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return {
            "id": record.id,
            "user_id": record.user_id,
            "property_unit": record.property_unit
        }

    @staticmethod
    async def update(db: AsyncSession, record_id: str, data: dict) -> Optional[dict]:
        result = await db.execute(select(RenovationRecordModel).where(RenovationRecordModel.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            return None
        if "property_unit" in data:
            record.property_unit = data["property_unit"]
        if "check_result" in data:
            record.check_result = data["check_result"]
        await db.commit()
        return {
            "id": record.id,
            "user_id": record.user_id,
            "property_unit": record.property_unit
        }

    @staticmethod
    async def delete(db: AsyncSession, record_id: str) -> bool:
        result = await db.execute(select(RenovationRecordModel).where(RenovationRecordModel.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            return False
        await db.delete(record)
        await db.commit()
        return True
