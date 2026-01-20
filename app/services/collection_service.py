"""
催收记录服务模块 (更新以匹配实际数据库)
"""

import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import CollectionRecord as CollectionRecordModel


class CollectionService:
    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: str) -> List[dict]:
        result = await db.execute(
            select(CollectionRecordModel).where(CollectionRecordModel.user_id == user_id)
        )
        records = result.scalars().all()
        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "debtor_name": r.debtor_name,
                "property_unit": r.property_unit,
                "arrears_amount": float(r.arrears_amount) if r.arrears_amount else 0,
                "collection_status": r.collection_status,
                "created_at": r.created_at
            }
            for r in records
        ]

    @staticmethod
    async def create(db: AsyncSession, user_id: str, data: dict) -> dict:
        record = CollectionRecordModel(
            user_id=user_id,
            debtor_name=data.get("debtor_name", ""),
            property_unit=data.get("property_unit", ""),
            arrears_amount=str(data.get("amount", 0)),
            collection_status="PENDING"
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return {
            "id": record.id,
            "user_id": record.user_id,
            "debtor_name": record.debtor_name,
            "property_unit": record.property_unit,
            "arrears_amount": float(record.arrears_amount),
            "collection_status": record.collection_status
        }

    @staticmethod
    async def update(db: AsyncSession, record_id: str, data: dict) -> Optional[dict]:
        result = await db.execute(select(CollectionRecordModel).where(CollectionRecordModel.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            return None
        record.debtor_name = data.get("debtor_name", record.debtor_name)
        record.property_unit = data.get("property_unit", record.property_unit)
        record.arrears_amount = str(data.get("amount", record.arrears_amount))
        await db.commit()
        return {
            "id": record.id,
            "user_id": record.user_id,
            "debtor_name": record.debtor_name,
            "property_unit": record.property_unit,
            "arrears_amount": float(record.arrears_amount)
        }

    @staticmethod
    async def delete(db: AsyncSession, record_id: str) -> bool:
        result = await db.execute(select(CollectionRecordModel).where(CollectionRecordModel.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            return False
        await db.delete(record)
        await db.commit()
        return True

    @staticmethod
    async def get_by_id(db: AsyncSession, record_id: str) -> Optional[dict]:
        result = await db.execute(select(CollectionRecordModel).where(CollectionRecordModel.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            return None
        return {
            "id": record.id,
            "user_id": record.user_id,
            "debtor_name": record.debtor_name,
            "property_unit": record.property_unit,
            "arrears_amount": float(record.arrears_amount) if record.arrears_amount else 0,
            "collection_status": record.collection_status
        }
