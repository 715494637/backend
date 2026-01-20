"""
用户管理 API 路由模块

提供用户列表查询、审批、更新和删除功能
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.schemas import User as UserSchema, UserUpdate, AdminUserCreate, UpdateQuotaRequest, UserQuotaResponse
from app.services import UserService
from app.core import get_current_admin, get_current_user
from app.models import User

router = APIRouter()


@router.get("", response_model=List[UserSchema])
async def get_users(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有用户列表（仅管理员）

    Args:
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        List[User]: 用户列表

    Raises:
        HTTPException: 非管理员用户访问时抛出 403 错误
    """
    return await UserService.get_users(db)


@router.put("/{user_id}/approve")
async def approve_user(
    user_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    审批用户（仅管理员）

    Args:
        user_id: 用户ID
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        dict: 审批结果消息

    Raises:
        HTTPException: 非管理员用户访问时抛出 403 错误
        HTTPException: 用户不存在时抛出 404 错误
    """
    await UserService.approve_user(db, user_id)
    return {"message": "用户审批成功"}


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户信息

    Args:
        user_id: 用户ID
        user_data: 更新的用户数据
        current_user: 当前操作用户
        db: 异步数据库会话

    Returns:
        User: 更新后的用户对象

    Raises:
        HTTPException: 无权限时抛出 403 错误
        HTTPException: 用户不存在时抛出 404 错误
    """
    return await UserService.update_user(db, user_id, user_data, current_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    删除用户（仅管理员）

    Args:
        user_id: 用户ID
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        dict: 删除结果消息

    Raises:
        HTTPException: 非管理员用户访问时抛出 403 错误
        HTTPException: 用户不存在时抛出 404 错误
    """
    await UserService.delete_user(db, user_id)
    return {"message": "用户删除成功"}


@router.post("", response_model=UserSchema)
async def create_user_by_admin(
    user_data: AdminUserCreate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    管理员创建用户（仅管理员）

    Args:
        user_data: 用户创建数据
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        User: 创建的用户对象

    Raises:
        HTTPException: 非管理员用户访问时抛出 403 错误
        HTTPException: 用户名或手机号已存在时抛出 400 错误
    """
    return await UserService.create_user_by_admin(db, user_data)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个用户信息

    Args:
        user_id: 用户ID
        current_user: 当前操作用户
        db: 异步数据库会话

    Returns:
        User: 用户对象

    Raises:
        HTTPException: 用户不存在时抛出 404 错误
    """
    from app.services import UserService
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.get("/{user_id}/quota", response_model=UserQuotaResponse)
async def get_user_quota(
    user_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户额度（仅管理员）

    Args:
        user_id: 用户ID
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        UserQuotaResponse: 用户额度信息

    Raises:
        HTTPException: 用户不存在时抛出 404 错误
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    current_quota = user.quota or {}
    return UserQuotaResponse(
        lawyer_letters=current_quota.get('lawyerLetters', 0),
        consultations=current_quota.get('consultations', 0)
    )


@router.put("/{user_id}/quota")
async def update_user_quota(
    user_id: str,
    data: UpdateQuotaRequest,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    管理员手动调整用户额度（充值或扣减）

    Args:
        user_id: 用户ID
        data: 额度更新数据
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        dict: 更新结果消息

    Raises:
        HTTPException: 用户不存在时抛出 404 错误
        HTTPException: 无效的操作类型时抛出 400 错误
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取当前额度
    current_quota = user.quota or {}

    # 根据操作类型计算新额度
    if data.operation == 'set':
        # 直接设置
        new_lawyer_letters = data.lawyer_letters
        new_consultations = data.consultations
    elif data.operation == 'add':
        # 累加
        new_lawyer_letters = current_quota.get('lawyerLetters', 0) + data.lawyer_letters
        new_consultations = current_quota.get('consultations', 0) + data.consultations
    elif data.operation == 'deduct':
        # 扣减
        new_lawyer_letters = max(0, current_quota.get('lawyerLetters', 0) - data.lawyer_letters)
        new_consultations = max(0, current_quota.get('consultations', 0) - data.consultations)
    else:
        raise HTTPException(status_code=400, detail="无效的操作类型")

    # 更新额度
    user.quota = {
        'lawyerLetters': new_lawyer_letters,
        'consultations': new_consultations
    }
    await db.commit()
    await db.refresh(user)

    return {"message": "额度更新成功", "quota": user.quota}