"""
认证 API 路由模块

提供用户登录、注册和短信验证码发送功能
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas import LoginRequest, Token, UserCreate
from app.services import UserService
from app.core import create_access_token, get_current_user
from app.utils import logger
from app.models import User

router = APIRouter()

# 默认用户协议内容
DEFAULT_AGREEMENT = """【东元法务通 · 用户服务协议及免责声明】
1. 本平台提供的所有法律建议、文书模板（含AI生成内容）仅供参考，不构成具有法律效力的正式法律意见书。
2. 涉及重大财产处分、人身安全及诉讼程序的，请务必咨询专业律师。
3. 用户应确保录入的业务数据（如欠费金额、业主信息）的真实性，因数据错误导致的法律后果由用户自行承担。
4. 禁止利用本平台从事任何违法违规活动。"""


@router.get("/agreement")
async def get_agreement():
    """
    获取用户服务协议内容（公开接口）

    Returns:
        dict: 包含协议内容的字典
    """
    return {"agreement": DEFAULT_AGREEMENT}


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息

    Args:
        current_user: 当前登录用户

    Returns:
        User: 用户信息
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "phone_number": current_user.phone_number,
        "role": current_user.role,
        "enterprise_name": current_user.enterprise_name,
        "approval_status": current_user.approval_status,
        "is_certified": current_user.is_certified,
        "quota": current_user.quota
    }


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

    # 返回响应（保持与前端兼容的结构）
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "approval_status": user.approval_status,
            "is_certified": user.is_certified
        }
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
