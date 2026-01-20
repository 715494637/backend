"""
AI 知识库 API 路由模块

提供 AI 知识库的配置和查询功能
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.core import get_current_admin
from app.models import User
from app.services.config_service import ConfigService
from app.schemas import SystemConfigUpdate
from app.utils import logger

router = APIRouter()

# 默认 AI 知识库内容
DEFAULT_AI_KB = """东元法务助手是专业的物业法律服务助手，专注于为物业管理企业提供法律咨询、文书草拟和风险建议。
主要功能包括：
1. 《民法典》相关法律咨询
2. 物业服务合同模板生成
3. 欠费催收法律建议
4. 装修违规处理指导
5. 劳动用工风险提示
6. 消防安全管理合规建议

请用专业、简洁的语言回答用户问题，并在涉及重大法律风险时提醒用户咨询专业律师。"""


@router.get("")
async def get_ai_kb(db: AsyncSession = Depends(get_db)):
    """
    获取 AI 知识库内容（公开接口）

    Args:
        db: 异步数据库会话

    Returns:
        dict: 包含 AI 知识库内容的字典
    """
    config = await ConfigService.get_config(db)
    ai_kb = config.ai_knowledge_base if config and config.ai_knowledge_base else DEFAULT_AI_KB
    return {"ai_kb": ai_kb}


@router.put("")
async def update_ai_kb(
    data: dict,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    更新 AI 知识库内容（仅管理员）

    Args:
        data: 包含新 AI 知识库内容的字典
        current_admin: 当前管理员用户
        db: 异步数据库会话

    Returns:
        dict: 更新结果消息
    """
    new_kb = data.get("ai_kb", "")
    logger.info(f"管理员 {current_admin.username} 更新了 AI 知识库，内容长度: {len(new_kb)}")

    # 保存到数据库
    await ConfigService.update_config(db, SystemConfigUpdate(ai_knowledge_base=new_kb))

    return {"message": "AI 知识库更新成功", "ai_kb": new_kb}
