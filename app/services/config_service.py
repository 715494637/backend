"""
系统配置业务逻辑服务模块

提供系统配置的查询、更新以及开屏图的管理等业务逻辑
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import SystemConfig
from app.schemas import SystemConfigUpdate
from app.utils import logger


class ConfigService:
    """系统配置业务逻辑服务"""

    @staticmethod
    async def get_config(db: AsyncSession) -> SystemConfig:
        """
        获取系统配置

        Args:
            db: 异步数据库会话

        Returns:
            SystemConfig: 系统配置对象
        """
        config = await db.execute(select(SystemConfig))
        config = config.scalar_one_or_none()

        if not config:
            # 创建默认配置
            config = SystemConfig(
                enable_phone_login=True,
                welcome_message="您好！我是东元物业法务助手。我可以为您提供《民法典》咨询、文书草拟及风险建议。（回答仅供参考）"
            )
            db.add(config)
            await db.commit()
            await db.refresh(config)
            logger.info("创建默认系统配置")

        logger.info("获取系统配置")
        return config

    @staticmethod
    async def update_config(db: AsyncSession, config_data: SystemConfigUpdate) -> None:
        """
        更新系统配置

        Args:
            db: 异步数据库会话
            config_data: 更新数据
        """
        config = await db.execute(select(SystemConfig))
        config = config.scalar_one_or_none()

        if not config:
            config = SystemConfig()
            db.add(config)

        # 更新配置信息
        for key, value in config_data.model_dump(exclude_unset=True).items():
            setattr(config, key, value)

        await db.commit()
        logger.info("系统配置更新成功")

    @staticmethod
    async def get_splash_image(db: AsyncSession) -> Optional[str]:
        """
        获取开屏图

        Args:
            db: 异步数据库会话

        Returns:
            Optional[str]: 开屏图URL，不存在返回None
        """
        config = await db.execute(select(SystemConfig))
        config = config.scalar_one_or_none()

        if config and config.splash_image:
            logger.info("获取开屏图")
            return config.splash_image

        logger.info("开屏图不存在")
        return None

    @staticmethod
    async def upload_splash_image(db: AsyncSession, splash_data: dict) -> None:
        """
        上传开屏图

        Args:
            db: 异步数据库会话
            splash_data: 包含开屏图数据的字典
        """
        config = await db.execute(select(SystemConfig))
        config = config.scalar_one_or_none()

        if not config:
            config = SystemConfig()
            db.add(config)

        config.splash_image = splash_data.get("splash_image")
        await db.commit()
        logger.info("开屏图上传成功")

    @staticmethod
    async def delete_splash_image(db: AsyncSession) -> None:
        """
        删除开屏图

        Args:
            db: 异步数据库会话
        """
        config = await db.execute(select(SystemConfig))
        config = config.scalar_one_or_none()

        if config:
            config.splash_image = None
            await db.commit()
            logger.info("开屏图删除成功")
        else:
            logger.warning("系统配置不存在，无需删除开屏图")