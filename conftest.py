"""
测试配置文件

提供全局 pytest fixtures
"""

import sys
import asyncio

# Windows 上使用 SelectorEventLoop 避免 ProactorEventLoop 的兼容性问题
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import AsyncSessionLocal


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    提供测试用的异步数据库会话

    每个测试函数都会获得一个独立的会话
    """
    async with AsyncSessionLocal() as session:
        yield session
        # Session 会自动在退出时清理