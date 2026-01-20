# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 东元法物后端 - FastAPI 服务

东元法物是专为物业公司打造的数字化法律服务工具包。后端采用 **FastAPI + Python 3.13 + MySQL + aiomysql** 异步架构。

## 常用命令

```bash
# 开发模式（热重载）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 安装依赖
uv pip install -e .

# 运行单个测试（暂无）
```

访问地址：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 架构概览

```
请求流程:
[客户端] → [FastAPI路由层 /api/v1/*] → [服务层 Service] → [异步数据库会话] → [MySQL]
                                     ↓
                              [依赖注入系统]
                                     ↓
                        [认证/权限中间件: JWT + bcrypt]
```

### 分层结构

| 目录 | 职责 |
|------|------|
| `app/api/v1/` | 18 个路由模块，统一以 `/api/v1` 为前缀 |
| `app/services/` | 业务逻辑层，对应各路由模块 |
| `app/core/` | 认证核心 + 依赖注入函数 |
| `app/config/` | Pydantic Settings 配置管理 |
| `app/db/` | 异步会话管理 (aiomysql + SQLAlchemy 2.0) |
| `app/models.py` | 21 个 ORM 模型定义 |
| `app/schemas.py` | Pydantic V2 数据验证模型 |
| `app/main.py` | 应用入口 + 生命周期管理 + 中间件 |

### 核心模型

| 模型 | 表名 | 用途 |
|------|------|------|
| User | users | 用户账户 (UUID 主键, bcrypt 密码) |
| CollectionRecord | collection_records | 催收记录 |
| Script | scripts | 话术库 (steps: JSON 步骤列表) |
| SOP | sops | 应急预案 |
| RenovationRecord | renovation_records | 装修巡查记录 |
| HealthCheckSection | health_check_sections | 法务体检题目 |
| ServiceRequest | service_requests | 服务请求 |

所有模型使用 `String(36)` UUID 作为主键。

### API 路由组织

所有路由注册在 `app/api/routes.py`，按模块划分：

```python
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(collections.router, prefix="/collections", tags=["催收记录"])
api_router.include_router(scripts.router, prefix="", tags=["话术库管理"])
# ... 更多路由
```

### 认证与权限

**依赖注入函数** (`app/core/dependencies.py`):
- `get_current_user()`: 获取当前认证用户
- `get_current_admin()`: 需要 ADMIN 角色
- `get_current_approved_user()`: 需审批通过

**权限规则**:
| 角色 | 权限 |
|------|------|
| ADMIN | 所有 API 访问权限、用户审批/删除、系统配置 |
| USER (APPROVED) | 登录、查询公开数据、操作个人数据 |
| USER (PENDING) | 仅登录受限 |

## 关键代码模式

### 异步数据库操作

```python
# 查询
result = await db.execute(select(Model).where(Model.id == id))
record = result.scalar_one_or_none()

# 提交
await db.commit()
await db.refresh(record)
```

### 服务层模式

每个业务模块对应一个 `Service` 类，使用静态方法：

```python
class CollectionService:
    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: str) -> List[dict]:
        # 实现
```

### Schema 验证 (Pydantic V2)

```python
class UserCreate(BaseModel):
    username: str
    password: str
    phone_number: Optional[str] = None
    enterprise_name: str

    model_config = ConfigDict(from_attributes=True)
```

### JSON 字段处理

JSON 数据存储为 Text，读取时解析：

```python
# 存储
record.questions = json.dumps(questions_list)

# 读取
questions = json.loads(record.questions or "[]")
```

## 配置文件

**环境变量** (`.env`):
```bash
DATABASE_URL=mysql+aiomysql://user:pass@host:3306/dong_legal?charset=utf8mb4
SECRET_KEY=jwt-secret-key
IMAGEBB_API_KEY=xxx
```

**配置读取** (`app/config/settings.py`):
- 使用 `Pydantic Settings` 管理环境变量
- 支持 `.env` 文件加载
- 所有配置通过 `settings.xxx` 访问

## 注意事项

1. **异步优先**: 所有数据库操作必须使用 `async/await`
2. **密码处理**: 使用 `bcrypt` (非 plain MD5)
3. **响应验证**: FastAPI 配置 `validate_response=False`
4. **日志**: 使用 Loguru，输出到 `logs/` 目录
5. **主键类型**: 所有表使用 UUID 字符串 (36位)
