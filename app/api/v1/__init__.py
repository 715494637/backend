from fastapi import APIRouter
from app.api.v1 import (
    auth, users,
    documents, risks, evidence, civil_code,
    enterprises, config, posters, contact_qr
)

# 创建 API v1 路由器
api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(documents.router, prefix="/documents", tags=["文档管理"])
api_router.include_router(risks.router, prefix="/risks", tags=["风险场景"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["证据清单"])
api_router.include_router(civil_code.router, prefix="/civil-code", tags=["民法典"])
api_router.include_router(enterprises.router, prefix="/enterprises", tags=["物业公司"])
api_router.include_router(config.router, prefix="/config", tags=["系统配置"])
api_router.include_router(posters.router, prefix="/posters", tags=["海报管理"])
api_router.include_router(contact_qr.router, prefix="/contact-qr", tags=["联系二维码"])