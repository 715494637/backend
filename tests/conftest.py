"""
测试配置文件

提供全局 pytest fixtures
"""

import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import AsyncSessionLocal


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    提供测试用的异步数据库会话

    每个测试函数都会获得一个独立的会话
    测试完成后会自动回滚并关闭会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # 测试成功后回滚，保持数据库干净
            await session.rollback()
        except Exception:
            # 测试失败时回滚
            await session.rollback()
            raise