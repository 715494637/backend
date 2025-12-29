[根目录](../CLAUDE.md) > **backend**

# backend - 后端模块

## 模块职责

东元法物后端 API 服务，基于 **FastAPI + Python 3.13 + MySQL + aiomysql** 构建，采用完全异步架构，提供用户认证、数据管理、业务逻辑等功能。

## 入口与启动

- **入口文件**: `app/main.py` - FastAPI 应用入口
- **启动命令**:
  ```bash
  # 开发模式（热重载）
  uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  # 生产模式
  uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
  ```
- **健康检查**: `GET /health`
- **API 文档**: `http://localhost:8000/docs`

## 对外接口

### API v1 路由 (`app/api/v1/`)

#### 认证接口 (`auth.py`)
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/send-sms` - 发送短信验证码

#### 用户管理 (`users.py`)
- `GET /api/v1/users` - 获取用户列表（管理员）
- `PUT /api/v1/users/{user_id}` - 更新用户信息
- `PUT /api/v1/users/{user_id}/approve` - 审批用户（管理员）
- `DELETE /api/v1/users/{user_id}` - 删除用户（管理员）

#### 其他模块（TODO）
- `/documents` - 文档管理
- `/risks` - 风险场景
- `/evidence` - 证据清单
- `/civil-code` - 民法典
- `/enterprises` - 物业公司
- `/config` - 系统配置
- `/posters` - 海报管理
- `/contact-qr` - 联系二维码

## 关键依赖与配置

### pyproject.toml 依赖
```toml
[project]
name = "backend"
version = "0.1.0"
requires-python = ">=3.13"

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["app"]

dependencies = [
    # Web 框架
    "fastapi==0.122.0",
    "uvicorn[standard]==0.34.0",

    # 数据库（异步）
    "sqlalchemy[asyncio]==2.0.37",
    "aiomysql==0.2.0",

    # 认证与安全
    "python-jose[cryptography]==3.3.0",
    "passlib[bcrypt]==1.7.4",
    "python-multipart==0.0.20",

    # 数据验证与配置
    "pydantic==2.10.5",
    "pydantic-settings==2.7.1",

    # 日志
    "loguru==0.7.3",

    # 加密
    "cryptography>=42.0.0",
]
```

### 配置文件 (`app/config/settings.py`)

使用 **Pydantic V2** 进行类型安全的配置管理：

主要配置项：
- `app_name`: "东元法务系统API"
- `app_version`: "1.0.0"
- `host`: "0.0.0.0"
- `port`: 8000
- `database_url`: MySQL 异步连接字符串 (`mysql+aiomysql://...`)
- `secret_key`: JWT 密钥
- `cors_origins`: CORS 允许的源

### 数据库配置 (`app/config/database.py`)

使用 **SQLAlchemy 2.0 异步引擎**：
- 引擎: `create_async_engine`
- 驱动: aiomysql
- 连接池配置:
  - `pool_size`: 5
  - `max_overflow`: 10
  - `pool_timeout`: 30
  - `pool_recycle`: 3600
  - `pool_pre_ping`: True

## 数据模型

### ORM 模型 (`app/models.py`)

```python
# 用户模型
class User(Base):
    id: String(36)  # UUID
    username: String(50)
    password: String(255)
    phone_number: String(20)
    role: String(10)  # ADMIN or USER
    enterprise_name: String(100)
    approval_status: String(10)  # PENDING, APPROVED, REJECTED
    is_certified: Boolean
    avatar_url: Text

# 文档模板
class DocumentTemplate(Base):
    id: String(36)
    title: String(200)
    category: String(50)
    description: Text
    content: Text
    file_url: Text

# 风险场景
class RiskScenario(Base):
    id: String(36)
    title: String(200)
    risk_level: String(10)  # High, Medium, Low
    content: Text
    questions: Text  # JSON string

# 证据清单
class EvidenceList(Base):
    id: String(36)
    title: String(200)
    items: Text  # JSON string

# 民法典条文
class CivilCodeArticle(Base):
    id: String(36)
    title: String(100)
    content: Text

# 物业公司
class Enterprise(Base):
    id: String(36)
    name: String(100)

# 系统配置
class SystemConfig(Base):
    id: String(36)
    enable_phone_login: Boolean
    welcome_message: Text
    ai_knowledge_base: Text
    enterprise_logo: Text
    splash_image: Text

# 自定义海报
class CustomPoster(Base):
    id: String(36)
    name: String(100)
    image_base64: Text

# 联系二维码
class ContactQRCode(Base):
    id: String(36)
    name: String(100)
    image_base64: Text
```

### Pydantic Schema (`app/schemas.py`)

使用 **Pydantic V2** 语法定义所有 API 请求和响应的数据结构：

```python
class User(BaseModel):
    """用户响应模型"""
    id: str
    role: str
    approval_status: str
    is_certified: bool
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
```

## 服务层

### 用户服务 (`app/services/user_service.py`)

所有方法都是**异步**的：
- `async authenticate_user(db, username, password)` - 用户认证
- `async create_user(db, user_data)` - 创建用户
- `async get_users(db)` - 获取用户列表
- `async approve_user(db, user_id)` - 审批用户
- `async update_user(db, user_id, user_data, current_user)` - 更新用户
- `async delete_user(db, user_id)` - 删除用户

## 认证与权限 (`app/core/`)

### 依赖注入 (`dependencies.py`)

所有依赖注入函数都是**异步**的：
- `async get_current_user()` - 获取当前用户
- `async get_current_admin()` - 获取当前管理员
- `async get_current_approved_user()` - 获取已审批用户

### 认证工具 (`auth.py`)
- `create_access_token(data)` - 创建 JWT 令牌
- `verify_token(token)` - 验证 JWT 令牌

## 数据库会话 (`app/db/session.py`)

异步会话管理：
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话的依赖注入函数"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"数据库会话异常: {e}")
            await session.rollback()
            raise
```

## 应用生命周期 (`app/main.py`)

使用 FastAPI 的 `lifespan` 上下文管理器：
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info(f"{settings.app_name} 正在启动...")
    await init_db()
    logger.info(f"{settings.app_name} 启动完成")

    yield

    # 关闭时执行
    logger.info(f"{settings.app_name} 正在关闭...")
    await close_db()
    logger.info(f"{settings.app_name} 已关闭")
```

## 中间件 (`app/main.py`)

1. **请求日志中间件** - 记录所有请求和响应
2. **全局异常处理器** - 捕获并记录所有异常
3. **CORS 中间件** - 跨域资源共享配置

## 日志系统 (`app/utils/logger.py`)

基于 Loguru 配置：
- 控制台输出（彩色）
- 应用日志文件（INFO 级，logs/app.log）
- 错误日志文件（ERROR 级，logs/error.log）
- 支持日志轮转、压缩和过期清理

## SQLAlchemy 2.0 异步语法

### 旧语法（同步）
```python
user = db.query(User).filter(User.id == user_id).first()
db.commit()
```

### 新语法（异步）
```python
result = await db.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()
await db.commit()
```

## 测试与质量

当前无自动化测试配置。建议添加：
- **pytest** - 测试框架
- **pytest-asyncio** - 异步测试支持
- **httpx** - HTTP 客户端测试
- **httpx.AsyncClient** - 异步 HTTP 客户端

## 常见问题 (FAQ)

1. **如何添加新的 API 路由？**
   - 在 `app/api/v1/` 下创建新模块
   - 使用 `async def` 定义路由函数
   - 使用 `AsyncSession` 作为数据库会话
   - 使用 `select()` 语法进行查询

2. **如何配置数据库？**
   - 修改 `.env` 文件中的 `DATABASE_URL`
   - 使用 `mysql+aiomysql://` 格式
   - 确保MySQL服务已启动

3. **如何启用调试模式？**
   - 设置 `.env` 文件中的 `DEBUG=true`
   - SQL语句将被打印到日志

4. **如何使用 Pydantic V2？**
   - 使用 `model_dump()` 替代 `dict()`
   - 使用 `model_config = ConfigDict(...)` 替代 `class Config`
   - 使用 `Field()` 添加字段描述

## 相关文件清单

### 核心文件
- `app/main.py` - 应用入口（含生命周期管理）
- `app/__init__.py` - 包初始化
- `pyproject.toml` - 项目配置
- `.env` - 环境变量配置

### 配置目录 (`app/config/`)
- `__init__.py` - 包初始化
- `settings.py` - Pydantic V2 应用配置
- `database.py` - 异步数据库引擎配置

### API 目录 (`app/api/`)
- `__init__.py` - 包初始化
- `routes.py` - 路由定义
- `v1/__init__.py` - API v1 路由聚合
- `v1/auth.py` - 认证接口（异步）
- `v1/users.py` - 用户管理（异步）

### 模型目录 (`app/`)
- `models.py` - ORM 模型定义
- `schemas.py` - Pydantic V2 Schema

### 服务目录 (`app/services/`)
- `__init__.py` - 包初始化
- `user_service.py` - 用户服务（异步）

### 核心目录 (`app/core/`)
- `__init__.py` - 包初始化
- `dependencies.py` - 依赖注入（异步）
- `auth.py` - 认证核心

### 数据库目录 (`app/db/`)
- `__init__.py` - 包初始化
- `session.py` - 异步会话管理

### 工具目录 (`app/utils/`)
- `__init__.py` - 包初始化
- `logger.py` - 日志工具

## 变更记录 (Changelog)

### 2025-12-26
- **重大升级**: Python 3.11 → **3.13**
- **数据库驱动**: PyMySQL → **aiomysql 0.2.0**（异步）
- **框架升级**: FastAPI 0.104.1 → **0.122.0**
- **ORM升级**: SQLAlchemy 2.0.23 → **2.0.37**（异步）
- **Pydantic升级**: V1 → **V2.10.5**
- **配置管理**: Pydantic Settings → **2.7.1**
- **服务器**: Uvicorn 0.24.0 → **0.34.0**
- **包管理**: 添加 **uv** 支持
- **完全异步化**: 所有数据库操作改为异步
- **代码优化**: 添加完整文档字符串和代码分区
- **生命周期管理**: 添加 lifespan 上下文管理器
- 初始化模块文档
- 完成 API 和模型结构分析