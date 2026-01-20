"""
专项服务模块 (精简版 - 2026-01-16)
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import SpecialProject as SpecialProjectModel


class SpecialProjectService:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[dict]:
        """获取所有专项服务"""
        result = await db.execute(select(SpecialProjectModel))
        projects = result.scalars().all()
        return [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description
            }
            for p in projects
        ]

    @staticmethod
    async def get_by_id(db: AsyncSession, project_id: str) -> Optional[dict]:
        """获取单个专项服务"""
        result = await db.execute(select(SpecialProjectModel).where(SpecialProjectModel.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return None
        return {
            "id": project.id,
            "title": project.title,
            "description": project.description
        }

    @staticmethod
    async def create(db: AsyncSession, data: dict) -> dict:
        """创建专项服务"""
        project = SpecialProjectModel(
            title=data.get("title", ""),
            description=data.get("description", "")
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return {
            "id": project.id,
            "title": project.title,
            "description": project.description
        }

    @staticmethod
    async def update(db: AsyncSession, project_id: str, data: dict) -> Optional[dict]:
        """更新专项服务"""
        result = await db.execute(select(SpecialProjectModel).where(SpecialProjectModel.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return None
        if "title" in data:
            project.title = data["title"]
        if "description" in data:
            project.description = data["description"]
        await db.commit()
        return {
            "id": project.id,
            "title": project.title,
            "description": project.description
        }

    @staticmethod
    async def delete(db: AsyncSession, project_id: str) -> bool:
        """删除专项服务"""
        result = await db.execute(select(SpecialProjectModel).where(SpecialProjectModel.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return False
        await db.delete(project)
        await db.commit()
        return True
