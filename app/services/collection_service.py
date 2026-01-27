"""
催收记录服务模块
"""

import datetime
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
                "owner_name": r.debtor_name or "",
                "room_number": r.property_unit or "",
                "amount": float(r.arrears_amount) if r.arrears_amount else 0,
                "created_at": r.created_at
            }
            for r in records
        ]

    @staticmethod
    async def create(db: AsyncSession, user_id: str, data: dict) -> dict:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = CollectionRecordModel(
            user_id=user_id,
            debtor_name=data.get("owner_name", ""),
            property_unit=data.get("room_number", ""),
            arrears_amount=str(data.get("amount", 0)),
            arrears_months=str(data.get("arrears_months", 0)),
            collection_status="PENDING",
            created_at=now,
            updated_at=now
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return {
            "id": record.id,
            "owner_name": record.debtor_name,
            "room_number": record.property_unit,
            "amount": float(record.arrears_amount)
        }

    @staticmethod
    async def update(db: AsyncSession, record_id: str, data: dict) -> Optional[dict]:
        result = await db.execute(select(CollectionRecordModel).where(CollectionRecordModel.id == record_id))
        record = result.scalar_one_or_none()
        if not record:
            return None
        if "owner_name" in data:
            record.debtor_name = data["owner_name"]
        if "room_number" in data:
            record.property_unit = data["room_number"]
        if "amount" in data:
            record.arrears_amount = str(data["amount"])
        await db.commit()
        return {
            "id": record.id,
            "owner_name": record.debtor_name,
            "room_number": record.property_unit,
            "amount": float(record.arrears_amount)
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
            "owner_name": record.debtor_name or "",
            "room_number": record.property_unit or "",
            "amount": float(record.arrears_amount) if record.arrears_amount else 0
        }
