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