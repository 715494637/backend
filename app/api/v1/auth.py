"""
认证 API 路由模块

提供用户登录、注册和短信验证码发送功能
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas import LoginRequest, Token, UserCreate
from app.services import UserService
from app.core import create_access_token
from app.utils import logger

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    用户登录

    Args:
        request: 登录请求数据，包含用户名和密码
        db: 异步数据库会话

    Returns:
        Token: 包含访问令牌和用户信息的响应

    Raises:
        HTTPException: 登录失败时抛出 401 错误
        HTTPException: 账号未审批时抛出 403 错误
    """
    logger.info(f"用户登录请求: {request.username}")

    # 验证用户凭据
    user = await UserService.authenticate_user(db, request.username, request.password)
    if not user:
        logger.warning(f"用户 {request.username} 登录失败：用户名或密码错误")
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 检查审批状态（管理员除外）
    if user.approval_status != "APPROVED" and user.role != "ADMIN":
        logger.warning(f"用户 {request.username} 登录失败：账号未通过审批")
        raise HTTPException(status_code=403, detail="账号未通过审批")

    # 生成访问令牌
    token_data = {"sub": user.id, "role": user.role}
    access_token = create_access_token(token_data)

    logger.info(f"用户 {request.username} 登录成功")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/register")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    用户注册

    Args:
        user_data: 用户创建数据
        db: 异步数据库会话

    Returns:
        dict: 注册结果消息

    Raises:
        HTTPException: 注册失败时抛出
    """
    logger.info(f"用户注册请求: {user_data.username}")

    # 创建新用户
    new_user = await UserService.create_user(db, user_data)

    return {"message": "注册成功，等待管理员审批"}


@router.post("/send-sms")
async def send_sms(phone: str):
    """
    发送短信验证码（模拟）

    Args:
        phone: 手机号码

    Returns:
        dict: 发送结果消息

    Note:
        当前为模拟实现，实际生产环境需要对接短信服务商
    """
    logger.info(f"模拟发送短信验证码到: {phone}")
    # 模拟短信发送
    return {"message": "验证码已发送"}