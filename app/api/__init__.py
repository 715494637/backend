"""
API 模块

导出所有 API 路由模块，简化导入路径
"""

from app.api.v1 import (
    auth,
    users,
    documents,
    risks,
    evidence,
    civil_code,
    enterprises,
    config,
    posters,
    contact_qr,
    api_router
)

__all__ = [
    "auth",
    "users",
    "documents",
    "risks",
    "evidence",
    "civil_code",
    "enterprises",
    "config",
    "posters",
    "contact_qr",
    "api_router"
]