# Backend Refactor - Domain-Driven Architecture Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 重构后端项目，采用领域驱动设计（DDD）架构，按业务领域模块化组织代码，提升代码可维护性和可扩展性，同时保持所有现有 API 路径向后兼容。

**Architecture:** 将现有分层架构重构为领域模块化架构。每个业务领域（auth、users、collections 等）作为一个独立模块，包含 models、schemas、service、router 和 tests。所有 API 路径保持不变，通过统一的路由注册机制确保向前兼容。

**Tech Stack:**
- FastAPI 0.115+ (Python 3.13)
- SQLAlchemy 2.0 (async/await)
- Pydantic V2
- aiomysql (异步 MySQL)
- bcrypt (密码哈希)
- Pytest (测试)

---

## Phase 1: Foundation Setup (基础架构搭建)

### Task 1: Create domains directory structure

**Files:**
- Create: `app/domains/__init__.py`

**Step 1: Create the domains directory and init file**

```python
"""
业务领域模块

采用领域驱动设计（DDD）思想，将应用按业务领域划分为独立模块。
每个领域模块包含：models, schemas, service, router, tests
"""

from app.domains import auth, users, collections, documents, risks, evidence, civil_code

__all__ = [
    "auth",
    "users",
    "collections",
    "documents",
    "risks",
    "evidence",
    "civil_code",
]
```

**Step 2: Commit**

```bash
git add app/domains/__init__.py
git commit -m "feat: create domains directory structure"
```

---

### Task 2: Create domain module template

**Files:**
- Create: `app/domains/auth/__init__.py`

**Step 1: Create domain module template**

```python
"""
认证领域模块

提供用户登录、注册、令牌验证等认证相关功能
"""

from app.domains.auth.models import User
from app.domains.auth.schemas import (
    LoginRequest,
    Token,
    UserCreate,
    UserUpdate,
)
from app.domains.auth.service import AuthService
from app.domains.auth.router import router as auth_router

__all__ = [
    "User",
    "LoginRequest",
    "Token",
    "UserCreate",
    "UserUpdate",
    "AuthService",
    "auth_router",
]
```

**Step 2: Commit**

```bash
git add app/domains/auth/__init__.py
git commit -m "feat: create auth domain module template"
```

---

## Phase 2: Auth Domain (认证领域)

### Task 3: Create Auth Domain - Models

**Files:**
- Create: `app/domains/auth/models.py`

**Step 1: Create user model in auth domain**

```python
"""
认证领域 - 数据模型

定义用户相关的数据库模型
"""

from sqlalchemy import Column, String, Boolean, JSON
from app.config.database import Base


def generate_uuid() -> str:
    """生成 UUID 字符串"""
    import uuid
    return str(uuid.uuid4())


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True)
    role = Column(String(10), default='USER')
    enterprise_name = Column(String(100))
    approval_status = Column(String(10), default='PENDING')
    is_certified = Column(Boolean, default=False)
    avatar_url = Column(String(500))
    quota = Column(JSON)  # {lawyerLetters: int, consultations: int}
```

**Step 2: Commit**

```bash
git add app/domains/auth/models.py
git commit -m "feat(auth): add User model to auth domain"
```

---

### Task 4: Create Auth Domain - Schemas

**Files:**
- Create: `app/domains/auth/schemas.py`

**Step 1: Create auth schemas**

```python
"""
认证领域 - Pydantic Schema

定义认证相关的数据验证模型
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    phone_number: Optional[str] = None
    enterprise_name: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模型"""
    password: str


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    phone_number: Optional[str] = None
    enterprise_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None
    approval_status: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模型"""
    id: str
    role: str
    approval_status: str
    is_certified: bool
    avatar_url: Optional[str] = None
    quota: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

**Step 2: Commit**

```bash
git add app/domains/auth/schemas.py
git commit -m "feat(auth): add auth schemas"
```

---

### Task 5: Create Auth Domain - Service

**Files:**
- Create: `app/domains/auth/service.py`

**Step 1: Create auth service**

```python
"""
认证领域 - 业务逻辑服务

提供用户认证、创建、验证等业务逻辑
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
from app.domsins.auth.models import User
from app.domsins.auth.schemas import UserCreate
from app.utils import logger


def get_password_hash(password: str) -> str:
    """使用 bcrypt 生成密码哈希"""
    password = str(password)[:72] if password else "default"
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """使用 bcrypt 验证密码"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


class AuthService:
    """认证业务逻辑服务"""

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        """验证用户登录凭据"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password):
            return None

        return user

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data: UserCreate
    ) -> User:
        """创建新用户"""
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            password=hashed_password,
            phone_number=user_data.phone_number,
            enterprise_name=user_data.enterprise_name,
            role="USER",
            approval_status="PENDING"
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"创建新用户: {new_user.username}")
        return new_user

    @staticmethod
    async def get_user_by_username(
        db: AsyncSession,
        username: str
    ) -> Optional[User]:
        """根据用户名查询用户"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
```

**Step 2: Commit**

```bash
git add app/domains/auth/service.py
git commit -m "feat(auth): add AuthService with authentication logic"
```

---

### Task 6: Create Auth Domain - Router

**Files:**
- Create: `app/domains/auth/router.py`

**Step 1: Create auth router**

```python
"""
认证领域 - API 路由

提供登录、注册等认证相关的 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.core.auth import create_access_token, get_current_user
from app.core.dependencies import get_current_approved_user
from app.domains.auth.schemas import (
    LoginRequest,
    Token,
    UserCreate,
    UserResponse,
)
from app.domains.auth.service import AuthService
from app.domains.auth.models import User
from app.utils import logger

# 默认用户协议内容
DEFAULT_AGREEMENT = """【东元法务通 · 用户服务协议及免责声明】
1. 本平台提供的所有法律建议、文书模板（含AI生成内容）仅供参考，不构成具有法律效力的正式法律意见书。
2. 涉及重大财产处分、人身安全及诉讼程序的，请务必咨询专业律师。
3. 用户应确保录入的业务数据（如欠费金额、业主信息）的真实性，因数据错误导致的法律后果由用户自行承担。
4. 禁止利用本平台从事任何违法违规活动。"""

router = APIRouter()


@router.get("/agreement")
async def get_agreement():
    """获取用户服务协议内容（公开接口）"""
    return {"agreement": DEFAULT_AGREEMENT}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserResponse.model_validate(current_user)


@router.post("/login", response_model=Token, tags=["认证"])
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    用户登录

    API 兼容性：路径 /api/v1/auth/login 保持不变
    """
    logger.info(f"用户登录请求: {request.username}")

    user = await AuthService.authenticate_user(db, request.username, request.password)
    if not user:
        logger.warning(f"用户 {request.username} 登录失败：用户名或密码错误")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if user.approval_status != "APPROVED" and user.role != "ADMIN":
        logger.warning(f"用户 {request.username} 登录失败：账号未通过审批")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号未通过审批"
        )

    token_data = {"sub": user.id, "role": user.role}
    access_token = create_access_token(token_data)

    logger.info(f"用户 {request.username} 登录成功")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.post("/register", tags=["认证"])
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    用户注册

    API 兼容性：路径 /api/v1/auth/register 保持不变
    """
    logger.info(f"用户注册请求: {user_data.username}")

    # 检查用户名是否存在
    existing = await AuthService.get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    new_user = await AuthService.create_user(db, user_data)

    return {"message": "注册成功，等待管理员审批"}


@router.post("/send-sms", tags=["认证"])
async def send_sms(phone: str):
    """发送短信验证码（模拟实现）"""
    logger.info(f"模拟发送短信验证码到: {phone}")
    return {"message": "验证码已发送"}
```

**Step 2: Commit**

```bash
git add app/domains/auth/router.py
git commit -m "feat(auth): add auth router with login/register endpoints"
```

---

### Task 7: Create Auth Domain - Tests

**Files:**
- Create: `app/domains/auth/tests/__init__.py`
- Create: `app/domains/auth/tests/test_service.py`

**Step 1: Create test directory and init file**

```python
"""认证领域测试模块"""
```

**Step 2: Create auth service tests**

```python
"""
认证领域 - 业务逻辑测试
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.auth.service import AuthService
from app.domains.auth.schemas import UserCreate


@pytest.mark.asyncio
async def test_authenticate_user_success(db: AsyncSession):
    """测试成功的用户认证"""
    # 先创建一个用户
    user_data = UserCreate(
        username="testuser",
        password="testpass123",
        enterprise_name="Test Enterprise"
    )
    created_user = await AuthService.create_user(db, user_data)

    # 验证认证成功
    authenticated = await AuthService.authenticate_user(
        db,
        "testuser",
        "testpass123"
    )

    assert authenticated is not None
    assert authenticated.id == created_user.id
    assert authenticated.username == "testuser"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db: AsyncSession):
    """测试错误的密码"""
    user_data = UserCreate(
        username="testuser2",
        password="correctpass",
        enterprise_name="Test Enterprise"
    )
    await AuthService.create_user(db, user_data)

    # 验证错误密码认证失败
    authenticated = await AuthService.authenticate_user(
        db,
        "testuser2",
        "wrongpass"
    )

    assert authenticated is None


@pytest.mark.asyncio
async def test_authenticate_user_not_exists(db: AsyncSession):
    """测试不存在的用户"""
    authenticated = await AuthService.authenticate_user(
        db,
        "nonexistent",
        "anypass"
    )

    assert authenticated is None


@pytest.mark.asyncio
async def test_create_user(db: AsyncSession):
    """测试创建用户"""
    user_data = UserCreate(
        username="newuser",
        password="securepass",
        phone_number="13800138000",
        enterprise_name="New Enterprise"
    )

    user = await AuthService.create_user(db, user_data)

    assert user.id is not None
    assert user.username == "newuser"
    assert user.role == "USER"
    assert user.approval_status == "PENDING"
    assert user.password != "securepass"  # 密码应该被哈希
```

**Step 3: Run tests**

```bash
pytest app/domains/auth/tests/test_service.py -v
```

Expected: All tests PASS

**Step 4: Commit**

```bash
git add app/domains/auth/tests/
git commit -m "test(auth): add auth service tests"
```

---

## Phase 3: Users Domain (用户管理领域)

### Task 8: Create Users Domain - Models

**Files:**
- Create: `app/domains/users/__init__.py`
- Create: `app/domains/users/models.py`

**Step 1: Create users module structure**

```bash
# Create these files
```

`app/domains/users/__init__.py`:
```python
"""
用户管理领域模块

提供用户查询、更新、审核等管理功能
"""

from app.domains.users.service import UserService
from app.domains.users.router import router as users_router

__all__ = ["UserService", "users_router"]
```

`app/domains/users/models.py`:
```python
"""
用户管理领域 - 数据模型

共享 User 模型（定义在 auth domain）
"""

from app.domains.auth.models import User

__all__ = ["User"]
```

**Step 2: Commit**

```bash
git add app/domains/users/
git commit -m "feat(users): create users domain structure"
```

---

### Task 9: Create Users Domain - Schemas

**Files:**
- Create: `app/domains/users/schemas.py`

**Step 1: Create users schemas**

```python
"""
用户管理领域 - Pydantic Schema

定义用户管理相关的 Schema（扩展开认证 schema）
"""

from app.domains.auth.schemas import UserUpdate, UserResponse
from pydantic import BaseModel, Field

# 重新导出共享的 Schema
__all__ = ["UserUpdate", "UserResponse"]


class ApproveUserRequest(BaseModel):
    """用户审批请求"""
    admin_password: str = Field(..., min_length=6, description="管理员密码")


class UpdateUserQuotaRequest(BaseModel):
    """更新用户配额请求"""
    operation: str = Field(..., pattern="^(set|add|deduct)$")
    lawyer_letters: int = Field(default=0, ge=0)
    consultations: int = Field(default=0, ge=0)


class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_users: int = 0
    pending_users: int = 0
    approved_users: int = 0
    admin_count: int = 0
```

**Step 2: Commit**

```bash
git add app/domains/users/schemas.py
git commit -m "feat(users): add user management schemas"
```

---

### Task 10: Create Users Domain - Service

**Files:**
- Create: `app/domains/users/service.py`

**Step 1: Create users service**

```python
"""
用户管理领域 - 业务逻辑服务

提供用户查询、审批、更新、配额管理等功能
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import HTTPException, status
from app.domains.auth.models import User
from app.domains.auth.schemas import UserUpdate
from app.utils import logger


class UserService:
    """用户管理业务逻辑服务"""

    @staticmethod
    async def get_all_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """获取所有用户列表（分页）"""
        result = await db.execute(
            select(User).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """根据 ID 查询用户"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def approve_user(db: AsyncSession, user_id: str) -> User:
        """审批用户"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        if user.approval_status == "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户已通过审批"
            )

        user.approval_status = "APPROVED"
        await db.commit()
        await db.refresh(user)

        logger.info(f"用户 {user.username} 已通过审核")
        return user

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: str,
        update_data: UserUpdate,
        is_admin: bool = False
    ) -> User:
        """更新用户信息"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        # 非管理员只能更新特定字段
        if not is_admin:
            allowed_fields = {"username", "phone_number", "avatar_url"}
            for field in update_data.model_dump(exclude_unset=True):
                if field not in allowed_fields:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"权限不足，不能更新 {field} 字段"
                    )

        # 检查用户名是否重复
        if update_data.username and update_data.username != user.username:
            existing = await db.execute(
                select(User).where(
                    User.username == update_data.username,
                    User.id != user_id
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已存在"
                )

        # 更新字段
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)

        logger.info(f"用户 {user.username} 信息已更新")
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: str) -> None:
        """删除用户"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        await db.delete(user)
        await db.commit()

        logger.info(f"用户 {user.username} 已删除")

    @staticmethod
    async def get_user_stats(db: AsyncSession) -> dict:
        """获取用户统计信息"""
        result = await db.execute(select(User))
        all_users = result.scalars().all()

        return {
            "total_users": len(all_users),
            "pending_users": sum(1 for u in all_users if u.approval_status == "PENDING"),
            "approved_users": sum(1 for u in all_users if u.approval_status == "APPROVED"),
            "admin_count": sum(1 for u in all_users if u.role == "ADMIN"),
        }
```

**Step 2: Commit**

```bash
git add app/domains/users/service.py
git commit -m "feat(users): add UserService with user management logic"
```

---

### Task 11: Create Users Domain - Router

**Files:**
- Create: `app/domains/users/router.py`

**Step 1: Create users router**

```python
"""
用户管理领域 - API 路由

提供用户查询、更新、审批、删除等管理端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.domains.auth.models import User
from app.domains.auth.schemas import UserResponse
from app.domains.users.schemas import UserStatsResponse
from app.domains.users.service import UserService

router = APIRouter()


@router.get("", response_model=list[UserResponse], tags=["用户管理"])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户列表（管理员）

    API 兼容性：路径 /api/v1/users 保持不变
    """
    users = await UserService.get_all_users(db, skip, limit)
    return [UserResponse.model_validate(u) for u in users]


@router.get("/me", response_model=UserResponse, tags=["用户管理"])
async def get_my_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse, tags=["用户管理"])
async def get_user(
    user_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定用户信息（管理员）

    API 兼容性：路径 /api/v1/users/{user_id} 保持不变
    """
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return UserResponse.model_validate(user)


@router.put("/{user_id}/approve", tags=["用户管理"])
async def approve_user(
    user_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    审批用户（管理员）

    API 兼容性：路径 /api/v1/users/{user_id}/approve 保持不变
    """
    await UserService.approve_user(db, user_id)
    return {"message": "用户审批成功"}


@router.put("/{user_id}", response_model=UserResponse, tags=["用户管理"])
async def update_user(
    user_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户信息

    API 兼容性：路径 /api/v1/users/{user_id} 保持不变
    """
    # 判断是否为管理员
    is_admin = current_user.role == "ADMIN"

    # 构造 UserUpdate 对象
    from app.domains.auth.schemas import UserUpdate
    update_dto = UserUpdate(**update_data)

    updated_user = await UserService.update_user(db, user_id, update_dto, is_admin)
    return UserResponse.model_validate(updated_user)


@router.delete("/{user_id}", tags=["用户管理"])
async def delete_user(
    user_id: str,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    删除用户（管理员）

    API 兼容性：路径 /api/v1/users/{user_id} (DELETE) 保持不变
    """
    await UserService.delete_user(db, user_id)
    return {"message": "用户删除成功"}


@router.get("/stats/overview", response_model=UserStatsResponse, tags=["用户管理"])
async def get_user_stats(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取用户统计信息（管理员）"""
    return await UserService.get_user_stats(db)
```

**Step 2: Commit**

```bash
git add app/domains/users/router.py
git commit -m "feat(users): add users router with CRUD endpoints"
```

---

## Phase 4: Collections Domain (催收记录领域)

### Task 12: Create Collections Domain - Models

**Files:**
- Create: `app/domains/collections/__init__.py`
- Create: `app/domains/collections/models.py`

**Step 1: Create collections module structure**

`app/domains/collections/__init__.py`:
```python
"""
催收记录领域模块

提供催收记录的创建、查询、更新等功能
"""

from app.domains.collections.service import CollectionService
from app.domains.collections.router import router as collections_router

__all__ = ["CollectionService", "collections_router"]
```

`app/domains/collections/models.py`:
```python
"""
催收记录领域 - 数据模型
"""

from sqlalchemy import Column, String, Text
from app.config.database import Base


def generate_uuid() -> str:
    """生成 UUID 字符串"""
    import uuid
    return str(uuid.uuid4())


class CollectionRecord(Base):
    """催收记录表"""
    __tablename__ = "collection_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=False, index=True)
    debtor_name = Column(String(100), nullable=False)
    debtor_phone = Column(String(20))
    property_unit = Column(String(200), nullable=False)
    property_area = Column(String(50))
    arrears_amount = Column(String(20), nullable=False, default="0")
    arrears_months = Column(String(10))
    fee_type = Column(String(50))
    collection_status = Column(String(20), default='PENDING')
    last_collection_date = Column(String(20))
    notes = Column(Text)
    created_at = Column(String(30))
    updated_at = Column(String(30))
```

**Step 2: Commit**

```bash
git add app/domains/collections/
git commit -m "feat(collections): create collections domain with models"
```

---

### Task 13: Create Collections Domain - Schemas

**Files:**
- Create: `app/domains/collections/schemas.py`

**Step 1: Create collections schemas**

```python
"""
催收记录领域 - Pydantic Schema
"""

from pydantic import BaseModel, ConfigDict, Field


class CollectionRecordBase(BaseModel):
    """催收记录基础模型"""
    debtor_name: str = Field(..., min_length=1, max_length=100)
    debtor_phone: Optional[str] = Field(None, max_length=20)
    property_unit: str = Field(..., min_length=1, max_length=200)
    property_area: Optional[str] = Field(None, max_length=50)
    arrears_amount: str = Field(..., pattern=r'^\d+(\.\d{1,2})?$')
    arrears_months: Optional[str] = Field(None, max_length=10)
    fee_type: Optional[str] = Field(None, max_length=50)
    collection_status: str = Field(default="PENDING", max_length=20)
    last_collection_date: Optional[str] = None
    notes: Optional[str] = None


class CollectionRecordCreate(CollectionRecordBase):
    """创建催收记录"""
    pass


class CollectionRecordUpdate(BaseModel):
    """更新催收记录"""
    debtor_name: Optional[str] = Field(None, min_length=1, max_length=100)
    debtor_phone: Optional[str] = Field(None, max_length=20)
    property_unit: Optional[str] = Field(None, min_length=1, max_length=200)
    property_area: Optional[str] = Field(None, max_length=50)
    arrears_amount: Optional[str] = Field(None, pattern=r'^\d+(\.\d{1,2})?$')
    arrears_months: Optional[str] = Field(None, max_length=10)
    fee_type: Optional[str] = Field(None, max_length=50)
    collection_status: Optional[str] = Field(None, max_length=20)
    last_collection_date: Optional[str] = None
    notes: Optional[str] = None


class CollectionRecordResponse(CollectionRecordBase):
    """催收记录响应"""
    id: str
    user_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


from typing import Optional
```

**Step 2: Commit**

```bash
git add app/domains/collections/schemas.py
git commit -m "feat(collections): add collection record schemas"
```

---

### Task 14: Create Collections Domain - Service

**Files:**
- Create: `app/domains/collections/service.py`

**Step 1: Create collections service**

```python
"""
催收记录领域 - 业务逻辑服务
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime
from app.domains.collections.models import CollectionRecord
from app.domains.collections.schemas import CollectionRecordCreate, CollectionRecordUpdate
from app.utils import logger


def get_current_timestamp() -> str:
    """获取当前时间戳"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class CollectionService:
    """催收记录业务逻辑服务"""

    @staticmethod
    async def create_record(
        db: AsyncSession,
        user_id: str,
        record_data: CollectionRecordCreate
    ) -> CollectionRecord:
        """创建催收记录"""
        record = CollectionRecord(
            user_id=user_id,
            **record_data.model_dump(),
            created_at=get_current_timestamp(),
            updated_at=get_current_timestamp()
        )

        db.add(record)
        await db.commit()
        await db.refresh(record)

        logger.info(f" 创建催收记录: {record.id}")
        return record

    @staticmethod
    async def get_records_by_user(
        db: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CollectionRecord]:
        """获取用户的催收记录"""
        result = await db.execute(
            select(CollectionRecord)
            .where(CollectionRecord.user_id == user_id)
            .order_by(CollectionRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_record_by_id(
        db: AsyncSession,
        record_id: str
    ) -> Optional[CollectionRecord]:
        """根据 ID 获取催收记录"""
        result = await db.execute(
            select(CollectionRecord).where(CollectionRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_record(
        db: AsyncSession,
        record_id: str,
        user_id: str,
        update_data: CollectionRecordUpdate,
        is_admin: bool = False
    ) -> CollectionRecord:
        """更新催收记录"""
        record = await CollectionService.get_record_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="催收记录不存在"
            )

        # 权限检查：非管理员只能更新自己的记录
        if not is_admin and record.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )

        # 更新字段
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(record, field, value)

        record.updated_at = get_current_timestamp()
        await db.commit()
        await db.refresh(record)

        logger.info(f"更新催收记录: {record.id}")
        return record

    @staticmethod
    async def delete_record(
        db: AsyncSession,
        record_id: str,
        user_id: str,
        is_admin: bool = False
    ) -> None:
        """删除催收记录"""
        record = await CollectionService.get_record_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="催收记录不存在"
            )

        # 权限检查
        if not is_admin and record.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )

        await db.delete(record)
        await db.commit()

        logger.info(f"删除催收记录: {record.id}")
```

**Step 2: Commit**

```bash
git add app/domains/collections/service.py
git commit -m "feat(collections): add CollectionService with CRUD operations"
```

---

### Task 15: Create Collections Domain - Router

**Files:**
- Create: `app/domains/collections/router.py`

**Step 1: Create collections router**

```python
"""
催收记录领域 - API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.domains.auth.models import User
from app.domains.collections.schemas import (
    CollectionRecordCreate,
    CollectionRecordUpdate,
    CollectionRecordResponse,
)
from app.domains.collections.service import CollectionService

router = APIRouter()


@router.post("", response_model=CollectionRecordResponse, tags=["催收记录"])
async def create_collection_record(
    record_data: CollectionRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建催收记录

    API 兼容性：路径 /api/v1/collections 保持不变
    """
    record = await CollectionService.create_record(db, current_user.id, record_data)
    return CollectionRecordResponse.model_validate(record)


@router.get("", response_model=list[CollectionRecordResponse], tags=["催收记录"])
async def get_collection_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取催收记录列表

    API 兼容性：路径 /api/v1/collections (GET) 保持不变
    """
    records = await CollectionService.get_records_by_user(db, current_user.id, skip, limit)
    return [CollectionRecordResponse.model_validate(r) for r in records]


@router.get("/{record_id}", response_model=CollectionRecordResponse, tags=["催收记录"])
async def get_collection_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个催收记录

    API 兼容性：路径 /api/v1/collections/{record_id} 保持不变
    """
    record = await CollectionService.get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="催收记录不存在"
        )

    # 权限检查
    if record.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )

    return CollectionRecordResponse.model_validate(record)


@router.put("/{record_id}", response_model=CollectionRecordResponse, tags=["催收记录"])
async def update_collection_record(
    record_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新催收记录

    API 兼容性：路径 /api/v1/collections/{record_id} (PUT) 保持不变
    """
    update_dto = CollectionRecordUpdate(**update_data)
    is_admin = current_user.role == "ADMIN"

    record = await CollectionService.update_record(
        db, record_id, current_user.id, update_dto, is_admin
    )
    return CollectionRecordResponse.model_validate(record)


@router.delete("/{record_id}", tags=["催收记录"])
async def delete_collection_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除催收记录

    API 兼容性：路径 /api/v1/collections/{record_id} (DELETE) 保持不变
    """
    is_admin = current_user.role == "ADMIN"
    await CollectionService.delete_record(db, record_id, current_user.id, is_admin)
    return {"message": "催收记录删除成功"}
```

**Step 2: Commit**

```bash
git add app/domains/collections/router.py
git commit -m "feat(collections): add collections router with CRUD endpoints"
```

---

## Phase 5: Update Main Application (更新主应用)

### Task 16: Simplify main.py

**Files:**
- Modify: `app/main.py`

**Step 1: Update main.py to use domain routers**

```python
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
```

**Step 2: Commit**

```bash
git add app/main.py
git commit -m "refactor: simplify main.py to use domain routers"
```

---

### Task 17: Update imports in existing files

**Files:**
- Modify: `app/core/dependencies.py`
- Modify: `app/core/auth.py`

**Step 1: Update core/dependencies.py**

Change imports from `app.models` to domain models:

```python
"""
认证依赖注入模块（异步版本）
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.domains.auth.models import User  # Changed from app.models
from app.core.auth import verify_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前认证用户的依赖注入（异步）"""
    token = credentials.credentials
    token_data = verify_token(token)

    result = await db.execute(select(User).where(User.id == token_data["sub"]))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前管理员用户的依赖注入（异步）"""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user


async def get_current_approved_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前已审批用户的依赖注入（异步）"""
    if current_user.role != "ADMIN" and current_user.approval_status != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号未通过审批"
        )
    return current_user
```

**Step 2: Commit**

```bash
git add app/core/dependencies.py
git commit -m "refactor: update dependencies.py to use domain models"
```

---

## Phase 6: Clean Up Old Files (清理旧文件)

### Task 18: Remove old API routes directory

**After verifying new routes work correctly**

**Files:**
- Delete: `app/api/`
- Delete: `app/models.py`
- Delete: `app/schemas.py`

**Step 1: Remove old API directory**

```bash
# Remove old API directory
rm -rf app/api

# Remove old models.py and schemas.py (or rename to .bak for backup)
mv app/models.py app/models.py.bak
mv app/schemas.py app/schemas.py.bak
```

**Step 2: Commit**

```bash
git add -A
git commit -m "refactor: remove old API directory and model/schema files"
```

---

## Phase 7: Testing & Verification (测试与验证)

### Task 19: Run all tests

**Step 1: Run domain tests**

```bash
# Run auth domain tests
pytest app/domains/auth/tests/ -v

# Run all tests
pytest app/domains/ -v
```

Expected: All tests PASS

**Step 2: Run application server**

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Step 3: Verify API endpoints**

```bash
# Health check
curl http://localhost:8000/health

# Get agreement
curl http://localhost:8000/api/v1/auth/agreement

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123","enterprise_name":"Test Corp"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

Expected: All endpoints return correct responses

**Step 4: Verify API compatibility**

Test all existing API endpoints documented in `/docs` to ensure backward compatibility.

---

## Task 20: Final cleanup and documentation

**Files:**
- Create: `docs/architecture.md`

**Step 1: Create architecture documentation**

```markdown
# 后端架构文档

## 概述

采用领域驱动设计（DDD）架构，按业务领域模块化组织代码。

## 目录结构

```
app/
├── main.py                 # 应用入口
├── config/                 # 配置管理
├── core/                   # 核心认证逻辑
├── db/                     # 数据库会话
├── utils/                  # 工具函数
└── domains/                # 业务领域
    ├── auth/               # 认证
    ├── users/              # 用户管理
    ├── collections/        # 催收记录
    └── ...
```

## 领域模块结构

每个领域模块包含：

```
domains/{domain}/
├── __init__.py       # 模块导出
├── models.py         # 数据模型（可选）
├── schemas.py        # Pydantic 验证模型
├── service.py        # 业务逻辑
├── router.py         # API 路由
└── tests/            # 测试
```

## API 路径规范

所有 API 路径统一使用 `/api/v1` 前缀，确保向后兼容。

## 迁移指南

旧代码迁移要点：
1. `app/models` → `app/domains/*/{models.py}`
2. `app/schemas` → `app/domains/*/schemas.py`
3. `app/api/v1/*` → `app/domains/*/router.py`
4. `app/services/*` → `app/domains/*/service.py`
```

**Step 2: Commit**

```bash
git add docs/architecture.md
git commit -m "docs: add architecture documentation"
```

---

## Summary

此计划将后端重构为领域模块化架构，主要变更：

1. **新增 domains/** - 所有业务领域模块
2. **简化 main.py** - 只注册领域路由
3. **移除旧 api/** - 路由移到各自 domain
4. **保持 API 兼容** - 所有路径不变
5. **添加测试** - 每个领域有独立测试

重构完成后：
- 代码结构更清晰
- 高内聚低耦合
- 易于维护和扩展
- 支持未来微服务拆分