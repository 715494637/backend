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
from app.config.settings import settings
from app.config.database import init_db, close_db
from app.utils.logger import setup_logging, logger
from app.api.v1 import api_router


# ============================================
# 应用生命周期管理
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    在应用启动时初始化数据库连接，关闭时清理资源
    """
    # 启动时执行
    logger.info(f"{settings.app_name} 正在启动...")
    await init_db()
    logger.info(f"{settings.app_name} 启动完成")

    yield

    # 关闭时执行
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
    """
    全局异常处理器

    捕获所有未处理的异常，记录详细日志并返回统一格式的错误响应

    Args:
        request: 请求对象
        exc: 异常对象

    Returns:
        JSONResponse: 错误响应
    """
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
    """
    请求日志中间件

    记录每个请求的开始和完成时间，以及处理耗时

    Args:
        request: 请求对象
        call_next: 下一个中间件或路由处理器

    Returns:
        Response: 响应对象
    """
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
app.include_router(api_router, prefix="/api/v1")


# ============================================
# 根路由
# ============================================
@app.get("/", tags=["根路由"])
async def root():
    """
    根路由

    返回应用基本信息

    Returns:
        dict: 应用信息
    """
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
    """
    健康检查端点

    用于负载均衡器或监控服务检查应用健康状态

    Returns:
        dict: 健康状态信息
    """
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