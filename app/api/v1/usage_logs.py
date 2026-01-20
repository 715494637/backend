"""
使用日志 API 路由模块

提供系统使用日志的查询功能
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db import get_db
from app.core import get_current_admin
from app.models import User

router = APIRouter()


# 使用日志数据结构（模拟）
class UsageLog:
    def __init__(self, id: str, user_id: str, username: str, enterprise_name: str, feature_id: str, feature_name: str, timestamp: int):
        self.id = id
        self.user_id = user_id
        self.username = username
        self.enterprise_name = enterprise_name
        self.feature_id = feature_id
        self.feature_name = feature_name
        self.timestamp = timestamp


# 模拟数据
MOCK_LOGS = [
    UsageLog("1", "2", "boss", "东元示范物业", "docs", "文档查询", 1704067200000),
    UsageLog("2", "3", "manager", "东元示范物业", "civil-code", "民法典查询", 1704153600000),
    UsageLog("3", "2", "boss", "东元示范物业", "risks", "风险自查", 1704240000000),
]


@router.get("")
async def get_usage_logs(
    enterprise: Optional[str] = None,
    feature: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """
    获取使用日志列表（仅管理员）

    Args:
        enterprise: 可选，按企业名称过滤
        feature: 可选，按功能名称过滤
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        List[dict]: 使用日志列表
    """
    logs = MOCK_LOGS

    if enterprise:
        logs = [l for l in logs if l.enterprise_name == enterprise]
    if feature:
        logs = [l for l in logs if l.feature_id == feature]

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "username": log.username,
            "enterprise_name": log.enterprise_name,
            "feature_id": log.feature_id,
            "feature_name": log.feature_name,
            "timestamp": log.timestamp,
            "timestamp_str": datetime.fromtimestamp(log.timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
        }
        for log in logs
    ]
