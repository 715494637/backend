"""
话术库服务模块 (更新以匹配实际数据库)
"""

from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Script as ScriptModel


class ScriptService:
    @staticmethod
    def _script_to_dict(s: ScriptModel) -> dict:
        """将 Script 模型转换为字典"""
        return {
            "id": s.id,
            "title": s.title,
            "category": s.category,
            # content 字段已移除，统一使用 steps 存储话术内容
            "steps": s.steps if s.steps else [],  # 确保 steps 返回数组
            "is_active": s.is_active == "1"
        }

    @staticmethod
    async def get_all(db: AsyncSession) -> List[dict]:
        """获取所有话术"""
        result = await db.execute(
            select(ScriptModel).where(ScriptModel.is_active == "1")
        )
        scripts = result.scalars().all()
        return [ScriptService._script_to_dict(s) for s in scripts]

    @staticmethod
    async def get_by_id(db: AsyncSession, script_id: str) -> Optional[dict]:
        """获取单个话术"""
        result = await db.execute(select(ScriptModel).where(ScriptModel.id == script_id))
        script = result.scalar_one_or_none()
        if not script:
            return None
        return ScriptService._script_to_dict(script)

    @staticmethod
    async def create(db: AsyncSession, data: dict) -> dict:
        """创建话术"""
        script = ScriptModel(
            title=data.get("title", ""),
            category=data.get("category", ""),
            # content 字段已移除，统一使用 steps 存储话术内容
            steps=data.get("steps", []),  # 支持 steps 字段
            is_active="1"
        )
        db.add(script)
        await db.commit()
        await db.refresh(script)
        return ScriptService._script_to_dict(script)

    @staticmethod
    async def update(db: AsyncSession, script_id: str, data: dict) -> Optional[dict]:
        """更新话术"""
        result = await db.execute(select(ScriptModel).where(ScriptModel.id == script_id))
        script = result.scalar_one_or_none()
        if not script:
            return None

        if "title" in data:
            script.title = data["title"]
        if "category" in data:
            script.category = data["category"]
        # content 字段已移除，不再处理
        if "steps" in data:
            script.steps = data["steps"]  # 更新 steps 字段

        await db.commit()
        return ScriptService._script_to_dict(script)

    @staticmethod
    async def delete(db: AsyncSession, script_id: str) -> bool:
        """删除话术（软删除）"""
        result = await db.execute(select(ScriptModel).where(ScriptModel.id == script_id))
        script = result.scalar_one_or_none()
        if not script:
            return False
        script.is_active = "0"
        await db.commit()
        return True
