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
    collections,
    scripts,
    sops,
    renovation,
    vip,
    special_projects,
    health_check,
    service_requests,
    ai_kb,
    usage_logs,
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
    "collections",
    "scripts",
    "sops",
    "renovation",
    "vip",
    "special_projects",
    "health_check",
    "service_requests",
    "ai_kb",
    "usage_logs",
    "api_router"
]
