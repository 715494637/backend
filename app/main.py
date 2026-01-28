"""
FastAPI 应用主入口模块

东元法物后端 API 服务 - 基于 FastAPI + Python 3.13 + MySQL + aiomysql
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
import time

from app.config import settings, init_db, close_db
from app.utils import logger

# 导入领域路由
from app.domains.auth.router import router as auth_router
from app.domains.users.router import router as users_router
from app.domains.collections.router import router as collections_router
from app.domains.documents.router import router as documents_router
from app.domains.renovation.router import router as renovation_router
from app.domains.evidence.router import router as evidence_router
from app.domains.sops.router import router as sops_router
from app.domains.risks.router import router as risks_router
from app.domains.service_requests.router import router as service_requests_router
from app.domains.civil_code.router import router as civil_code_router


# ============================================
# 应用生命周期管理
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"{settings.app_name} 正在启动...")
    await init_db()
    logger.info(f"{settings.app_name} 启动完成")

    yield

    logger.info(f"{settings.app_name} 正在关闭...")
    await close_db()
    logger.info(f"{settings.app_name} 已关闭")


# ============================================
# 创建 FastAPI 应用
# ============================================
app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    validate_response=False
)

# ============================================
# 配置 CORS
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 全局异常处理器
# ============================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error("=" * 60)
    logger.error("全局异常捕获")
    logger.error(f"请求路径: {request.url}")
    logger.error(f"请求方法: {request.method}")
    logger.error(f"异常类型: {type(exc).__name__}")
    logger.error(f"异常信息: {exc}")
    logger.error(f"详细堆栈:\n{traceback.format_exc()}")
    logger.error("=" * 60)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "内部服务器错误",
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "timestamp": time.time()
        }
    )


# ============================================
# 请求日志中间件
# ============================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    start_time = time.time()
    logger.info(f"请求开始: {request.method} {request.url}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"请求完成: {request.method} {request.url} - "
        f"状态码: {response.status_code} - 耗时: {process_time:.3f}s"
    )

    return response


# ============================================
# 注册 API 路由
# ============================================
# 认证相关
app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])

# 用户管理
app.include_router(users_router, prefix="/api/v1/users", tags=["用户管理"])

# 催收记录
app.include_router(collections_router, prefix="/api/v1/collections", tags=["催收记录"])

# 文档模板
app.include_router(documents_router, prefix="/api/v1/documents", tags=["文档模板"])

# 装修巡查
app.include_router(renovation_router, prefix="/api/v1/renovation", tags=["装修巡查"])

# 证据清单
app.include_router(evidence_router, prefix="/api/v1/evidence", tags=["证据清单"])

# 服务请求
app.include_router(service_requests_router, prefix="/api/v1/service-requests", tags=["服务请求"])

# 应急预案
app.include_router(sops_router, prefix="/api/v1/sops", tags=["应急预案"])

# 民法典
app.include_router(civil_code_router, prefix="/api/v1/civil-code", tags=["民法典"])


# ============================================
# 根路由
# ============================================
@app.get("/", tags=["根路由"])
async def root():
    """根路由"""
    return {
        "message": f"{settings.app_name} 正在运行",
        "version": settings.app_version,
        "status": "healthy"
    }


# ============================================
# 健康检查
# ============================================
@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "service": settings.app_name
    }


# ============================================
# 直接运行
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )