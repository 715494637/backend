# 后端架构文档

## 概述

采用领域驱动设计（DDD）架构，按业务领域模块化组织代码，提升代码可维护性和可扩展性，同时保持所有现有 API 路径向后兼容。

### 设计原则

- **高内聚低耦合**：每个业务领域的所有代码集中在一个模块
- **单一职责**：每个组件只负责一个明确的功能
- **开闭原则**：对扩展开放，对修改关闭
- **依赖倒置**：依赖抽象而非具体实现

---

## 目录结构

```
app/
├── main.py                 # 应用入口
├── config/                 # 配置管理
│   ├── __init__.py
│   ├── database.py          # 数据库配置
│   └── settings.py          # 应用设置
├── core/                   # 核心认证逻辑
│   ├── __init__.py
│   ├── auth.py              # JWT 令牌创建和验证
│   └── dependencies.py      # 依赖注入（获取当前用户等）
├── db/                     # 数据库会话管理
│   ├── __init__.py
│   └── session.py           # 数据库会话工厂
├── utils/                  # 工具函数
│   ├── __init__.py
│   └── logger.py            # 日志配置
└── domains/                # 业务领域
    ├── __init__.py          # 领域模块导出
    ├── auth/               # 认证领域
    │   ├── __init__.py
    │   ├── models.py         # User 模型
    │   ├── schemas.py        # 认证相关 Schema
    │   ├── service.py        # 认证业务逻辑
    │   ├── router.py         # 认证 API 路由
    │   └── tests/            # 认证测试
    ├── users/              # 用户管理领域
    │   ├── __init__.py
    │   ├── models.py         # 共享 User 模型
    │   ├── schemas.py        # 用户管理 Schema
    │   ├── service.py        # 用户管理业务逻辑
    │   ├── router.py         # 用户管理 API 路由
    │   └── tests/            # 用户管理测试
    └── collections/        # 催收记录领域
        ├── __init__.py
        ├── models.py         # CollectionRecord 模型
        ├── schemas.py        # 催收记录 Schema
        ├── service.py        # 催收记录业务逻辑
        ├── router.py         # 催收记录 API 路由
        └── tests/            # 催收记录测试
```

---

## 领域模块结构

每个领域模块包含以下文件：

### `domains/{domain}/__init__.py`

模块导出文件，定义公共 API：

```python
"""
{domain} 领域模块

提供{domain}相关的功能
"""

from app.domains.{domain}.service import {Domain}Service
from app.domains.{domain}.router import router as {domain}_router

__all__ = ["{Domain}Service", "{domain}_router"]
```

### `domains/{domain}/models.py` (可选)

数据模型定义，如果模型已在其他领域定义，则重新导出：

```python
"""
{domain} 领域 - 数据模型
"""

from app.domains.auth.models import User  # 共享模型

__all__ = ["User"]
```

### `domains/{domain}/schemas.py`

Pydantic 验证模型：

```python
"""
{domain} 领域 - Pydantic Schema
"""

from pydantic import BaseModel

class {Domain}Create(BaseModel):
    """创建{domain}模型"""
    ...

class {Domain}Response(BaseModel):
    """{domain}响应模型"""
    ...
```

### `domains/{domain}/service.py`

业务逻辑服务类：

```python
"""
{domain} 领域 - 业务逻辑服务
"""

class {Domain}Service:
    """{domain}业务逻辑服务"""

    @staticmethod
    async def create_{domain}(db: AsyncSession, data: {Domain}Create) -> {Domain}:
        """创建{domain}"""
        ...

    @staticmethod
    async def get_{domain}(db: AsyncSession, id: str) -> Optional[{Domain}]:
        """获取{domain}"""
        ...
```

### `domains/{domain}/router.py`

FastAPI 路由：

```python
"""
{domain} 领域 - API 路由
"""

from fastapi import APIRouter

router = APIRouter()

@router.post("")
async def create_{domain}():
    """创建{domain}"""
    ...
```

### `domains/{domain}/tests/`

测试目录：

```python
"""
{domain} 领域 - 测试
"""
```

---

## API 路径规范

所有 API 路径统一使用 `/api/v1` 前缀：

| 领域 | 路径前缀 | 端点 |
|------|----------|------|
| auth | `/api/v1/auth` | `/login`, `/register`, `/me`, `/agreement`, `/send-sms` |
| users | `/api/v1/users` | `/`, `/me`, `/{user_id}`, `/{user_id}/approve`, `/stats/overview` |
| collections | `/api/v1/collections` | `/`, `/{record_id}` |

### API 兼容性保证

- 所有现有 API 路径保持不变
- 请求/响应格式保持不变
- 前端无需任何修改

---

## 迁移指南

### 旧代码迁移要点

| 旧位置 | 新位置 | 说明 |
|--------|--------|------|
| `app/models` | `app/domains/*/{models.py}` | 模型按领域拆分 |
| `app/schemas` | `app/domains/*/schemas.py` | Schema 按领域拆分 |
| `app/api/v1/*` | `app/domains/*/router.py` | 路由移到各自领域 |
| `app/services/*` | `app/domains/*/service.py` | 服务移到各自领域 |

### 导入路径更新

**旧导入：**
```python
from app.models import User
from app.schemas import UserCreate
from app.services.user_service import UserService
```

**新导入：**
```python
from app.domains.auth.models import User
from app.domains.auth.schemas import UserCreate
from app.domains.users.service import UserService
```

### 路由注册方式

**旧方式（统一注册）：**
```python
from app.api import api_router
app.include_router(api_router, prefix="/api/v1")
```

**新方式（分领域注册）：**
```python
from app.domains.auth.router import router as auth_router
from app.domains.users.router import router as users_router

app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(users_router, prefix="/api/v1/users")
```

---

## 技术栈

- **框架**: FastAPI 0.115+
- **Python**: 3.13
- **数据库**: MySQL
- **ORM**: SQLAlchemy 2.0 (async/await)
- **驱动**: aiomysql
- **认证**: bcrypt (密码哈希)
- **测试**: pytest

---

## 开发指南

### 添加新领域

1. 创建领域目录：`app/domains/{domain}/`
2. 创建 `__init__.py` 定义模块导出
3. 创建 `models.py` 定义数据模型（可选）
4. 创建 `schemas.py` 定义 Pydantic 模型
5. 创建 `service.py` 实现业务逻辑
6. 创建 `router.py` 定义 API 路由
7. 创建 `tests/` 目录并编写测试
8. 在 `app/main.py` 中注册路由
9. 在 `app/domains/__init__.py` 中导出新领域

### 测试

```bash
# 运行所有测试
pytest app/domains/ -v

# 运行特定领域测试
pytest app/domains/{domain}/tests/ -v

# 运行服务器
uv run uvicorn app.main:app --reload
```

### 查看 API 文档

访问 `/docs` 查看 Swagger UI 自动生成的 API 文档。