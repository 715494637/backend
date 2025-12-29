"""
异步数据库配置模块

使用 SQLAlchemy 2.0 + aiomysql 实现异步数据库连接
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config.settings import settings
from app.utils.logger import logger

# ============================================
# 创建异步数据库引擎
# ============================================
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,  # 是否打印 SQL 语句
    pool_size=settings.db_pool_size,  # 连接池大小
    max_overflow=settings.db_max_overflow,  # 连接池最大溢出数
    pool_timeout=settings.db_pool_timeout,  # 连接池超时时间
    pool_recycle=settings.db_pool_recycle,  # 连接回收时间
    pool_pre_ping=True,  # 连接池预检查，防止连接失效
)

# ============================================
# 创建基础模型类
# ============================================
Base = declarative_base()


async def init_db() -> None:
    """
    初始化数据库表结构

    在应用启动时调用，创建所有定义的表
    注意：生产环境建议使用 Alembic 进行数据库迁移
    """
    async with async_engine.begin() as conn:
        # 导入所有模型以确保它们被注册
        from app import models  # noqa: F401

        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)

        logger.info("数据库表结构初始化完成")


async def close_db() -> None:
    """
    关闭数据库连接

    在应用关闭时调用，优雅地关闭所有数据库连接
    """
    await async_engine.dispose()
    logger.info("数据库连接已关闭")