"""
用户业务逻辑服务模块

提供用户认证、创建、查询、更新和删除等业务逻辑
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from passlib.context import CryptContext
import bcrypt  # 移到文件顶部，避免每次调用都导入
from app.models import User
from app.schemas import UserCreate, UserUpdate, AdminUserCreate
from app.utils import logger

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """密码哈希 - 使用 bcrypt"""
    # 确保密码是有效的字符串
    if not isinstance(password, str):
        password = str(password)
    if not password:
        password = "default"
    # 截取前 72 个字符（bcrypt 限制）
    password = password[:72]
    # 使用文件顶部导入的 bcrypt
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        # 如果哈希格式不对，返回 False
        return False


class UserService:
    """用户业务逻辑服务"""

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """
        验证用户登录（密码必须是 bcrypt 哈希存储）

        Args:
            db: 异步数据库会话
            username: 用户名
            password: 密码（明文）

        Returns:
            User: 验证成功返回用户对象，失败返回None
        """
        logger.info(f"尝试验证用户: {username}")

        # Step 1: 先用用户名查询用户
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"用户 {username} 不存在")
            return None

        # Step 2: 用 bcrypt 验证密码
        if not verify_password(password, user.password):
            logger.warning(f"用户 {username} 密码错误")
            return None

        logger.info(f"用户 {username} 验证成功")
        return user

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """
        创建新用户

        Args:
            db: 异步数据库会话
            user_data: 用户创建数据

        Returns:
            User: 创建的用户对象

        Raises:
            HTTPException: 用户名或手机号已存在时抛出
        """
        # 检查用户名是否存在
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            logger.warning(f"用户名 {user_data.username} 已存在")
            raise HTTPException(status_code=400, detail="用户名已存在")

        # 检查手机号是否存在
        if user_data.phone_number:
            result = await db.execute(
                select(User).where(User.phone_number == user_data.phone_number)
            )
            if result.scalar_one_or_none():
                logger.warning(f"手机号 {user_data.phone_number} 已被注册")
                raise HTTPException(status_code=400, detail="手机号已被注册")

        # 创建新用户（密码用 bcrypt哈希存储）
        new_user = User(
            username=user_data.username,
            password=get_password_hash(user_data.password),
            phone_number=user_data.phone_number,
            enterprise_name=user_data.enterprise_name,
            role="USER",
            approval_status="PENDING"
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"新用户 {user_data.username} 注册成功，等待审批")
        return new_user

    @staticmethod
    async def create_user_by_admin(db: AsyncSession, user_data: AdminUserCreate) -> User:
        """
        管理员创建用户（直接审批通过）

        Args:
            db: 异步数据库会话
            user_data: 用户创建数据

        Returns:
            User: 创建的用户对象

        Raises:
            HTTPException: 用户名或手机号已存在时抛出
        """
        # 检查用户名是否存在
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            logger.warning(f"用户名 {user_data.username} 已存在")
            raise HTTPException(status_code=400, detail="用户名已存在")

        # 检查手机号是否存在
        if user_data.phone_number:
            result = await db.execute(
                select(User).where(User.phone_number == user_data.phone_number)
            )
            if result.scalar_one_or_none():
                logger.warning(f"手机号 {user_data.phone_number} 已被注册")
                raise HTTPException(status_code=400, detail="手机号已被注册")

        # 创建新用户（使用管理员指定的参数，密码用 bcrypt哈希存储）
        new_user = User(
            username=user_data.username,
            password=get_password_hash(user_data.password),
            phone_number=user_data.phone_number,
            enterprise_name=user_data.enterprise_name,
            role=user_data.role,
            approval_status=user_data.approval_status,
            is_certified=user_data.is_certified
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"管理员创建用户 {user_data.username} 成功，审批状态: {user_data.approval_status}")
        return new_user

    @staticmethod
    async def get_users(db: AsyncSession) -> List[User]:
        """
        获取所有用户列表

        Args:
            db: 异步数据库会话

        Returns:
            List[User]: 用户列表
        """
        result = await db.execute(select(User))
        users = result.scalars().all()
        logger.info(f"获取用户列表，共 {len(users)} 个用户")
        return users

    @staticmethod
    async def approve_user(db: AsyncSession, user_id: str) -> User:
        """
        审批用户

        Args:
            db: 异步数据库会话
            user_id: 用户ID

        Returns:
            User: 审批后的用户对象

        Raises:
            HTTPException: 用户不存在时抛出
            HTTPException: 用户已审批时抛出
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            logger.error(f"用户 {user_id} 不存在")
            raise HTTPException(status_code=404, detail="用户不存在")

        if user.approval_status == "APPROVED":
            logger.warning(f"用户 {user.username} 已审批")
            raise HTTPException(status_code=400, detail="用户已审批")

        user.approval_status = "APPROVED"
        await db.commit()

        logger.info(f"用户 {user.username} 审批成功")
        return user

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, user_data: UserUpdate, current_user: User) -> User:
        """
        更新用户信息

        Args:
            db: 异步数据库会话
            user_id: 用户ID
            user_data: 更新数据
            current_user: 当前操作用户

        Returns:
            User: 更新后的用户对象

        Raises:
            HTTPException: 权限不足或用户不存在时抛出
        """
        # 检查权限：用户只能更新自己的信息，管理员可以更新所有用户
        if current_user.role != "ADMIN" and current_user.id != user_id:
            logger.warning(f"用户 {current_user.username} 尝试越权更新用户 {user_id}")
            raise HTTPException(status_code=403, detail="权限不足")

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            logger.error(f"用户 {user_id} 不存在")
            raise HTTPException(status_code=404, detail="用户不存在")

        # 普通用户只能更新用户名、手机号和头像
        if current_user.role != "ADMIN":
            allowed_fields = {"username", "phone_number", "avatar_url"}
            for field in user_data.model_dump(exclude_unset=True):
                if field not in allowed_fields:
                    logger.warning(f"普通用户 {current_user.username} 尝试更新禁止字段 {field}")
                    raise HTTPException(status_code=403, detail=f"普通用户不能更新{field}字段")

        # 检查用户名是否已存在（如果要更新的话）
        if user_data.username and user_data.username != user.username:
            result = await db.execute(
                select(User).where(User.username == user_data.username, User.id != user_id)
            )
            if result.scalar_one_or_none():
                logger.warning(f"用户名 {user_data.username} 已存在")
                raise HTTPException(status_code=400, detail="用户名已存在")

        # 更新用户信息
        # 先处理特殊字段
        update_data = user_data.model_dump(exclude_unset=True)

        # 处理密码更新（需要哈希）
        # 只在密码有实际内容时才更新
        if update_data.get('password'):
            password_value = update_data['password']
            # 确保密码是有效的非空字符串
            if isinstance(password_value, str) and password_value.strip():
                user.password = get_password_hash(password_value)
            del update_data['password']  # 移除，避免设置普通字段

        # 处理角色更新（仅管理员）
        if 'role' in update_data and current_user.role == "ADMIN":
            user.role = update_data['role']
            del update_data['role']  # 移除，避免重复设置

        # 更新其他字段
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)

        logger.info(f"用户 {user.username} 信息更新成功")
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: str) -> None:
        """
        删除用户

        Args:
            db: 异步数据库会话
            user_id: 用户ID

        Raises:
            HTTPException: 用户不存在时抛出
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            logger.error(f"用户 {user_id} 不存在")
            raise HTTPException(status_code=404, detail="用户不存在")

        username = user.username
        await db.delete(user)
        await db.commit()

        logger.info(f"用户 {username} 删除成功")

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """
        获取单个用户信息

        Args:
            db: 异步数据库会话
            user_id: 用户ID

        Returns:
            User: 用户对象，不存在返回None
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()