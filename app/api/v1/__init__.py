from fastapi import APIRouter
from app.api.v1 import (
    auth, users,
    documents, risks, evidence, civil_code,
    enterprises, config, posters, contact_qr,
    collections, scripts, sops, renovation, vip,
    special_projects, health_check, service_requests,
    ai_kb, usage_logs, ai, wechat
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
api_router.include_router(collections.router, prefix="/collections", tags=["催收记录"])
api_router.include_router(scripts.router, prefix="", tags=["话术库管理"])
api_router.include_router(scripts.collection_router, prefix="", tags=["催收话术库"])
api_router.include_router(sops.router, prefix="/sops", tags=["应急预案"])
api_router.include_router(renovation.router, prefix="/renovation", tags=["装修巡查"])
api_router.include_router(vip.router, prefix="/vip", tags=["VIP权益"])
api_router.include_router(special_projects.router, prefix="/special-projects", tags=["专项服务"])
api_router.include_router(health_check.router, prefix="/health-check", tags=["法务体检"])
api_router.include_router(service_requests.router, prefix="/service-requests", tags=["服务请求"])
api_router.include_router(ai_kb.router, prefix="/ai-kb", tags=["AI知识库"])
api_router.include_router(usage_logs.router, prefix="/usage-logs", tags=["使用日志"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI代理"])
api_router.include_router(wechat.router, prefix="/wechat", tags=["微信"])
