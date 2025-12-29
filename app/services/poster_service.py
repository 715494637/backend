"""
海报管理业务逻辑服务模块

提供自定义海报的查询、创建和删除等业务逻辑
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models import CustomPoster
from app.schemas import CustomPosterCreate
from app.utils.logger import logger


class PosterService:
    """海报管理业务逻辑服务"""

    @staticmethod
    async def get_posters(db: AsyncSession) -> List[CustomPoster]:
        """
        获取所有自定义海报列表

        Args:
            db: 异步数据库会话

        Returns:
            List[CustomPoster]: 自定义海报列表
        """
        result = await db.execute(select(CustomPoster))
        posters = result.scalars().all()
        logger.info(f"获取自定义海报列表，共 {len(posters)} 个")
        return posters

    @staticmethod
    async def create_poster(db: AsyncSession, poster_data: CustomPosterCreate) -> CustomPoster:
        """
        创建新的自定义海报

        Args:
            db: 异步数据库会话
            poster_data: 海报创建数据

        Returns:
            CustomPoster: 创建的海报对象
        """
        new_poster = CustomPoster(
            name=poster_data.name,
            image_base64=poster_data.image_base64
        )

        db.add(new_poster)
        await db.commit()
        await db.refresh(new_poster)

        logger.info(f"新自定义海报 {new_poster.name} 创建成功")
        return new_poster

    @staticmethod
    async def delete_poster(db: AsyncSession, poster_id: str) -> None:
        """
        删除海报

        Args:
            db: 异步数据库会话
            poster_id: 海报ID

        Raises:
            HTTPException: 海报不存在时抛出
        """
        result = await db.execute(select(CustomPoster).where(CustomPoster.id == poster_id))
        poster = result.scalar_one_or_none()

        if not poster:
            logger.error(f"海报 {poster_id} 不存在")
            raise HTTPException(status_code=404, detail="海报不存在")

        name = poster.name
        await db.delete(poster)
        await db.commit()

        logger.info(f"海报 {name} 删除成功")