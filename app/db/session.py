"""
数据库会话管理模块

提供异步数据库会话的依赖注入函数
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.config import async_engine
from app.utils import logger
from typing import AsyncGenerator


# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话的依赖注入函数

    用于 FastAPI 依赖注入系统，为每个请求提供独立的数据库会话

    Yields:
        AsyncSession: 异步数据库会话对象

    Example:
        ```python
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"数据库会话异常: {e}")
            await session.rollback()
            raise