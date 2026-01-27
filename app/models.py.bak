"""
SQLAlchemy ORM 模型定义

定义所有数据库表的 ORM 模型
"""

from sqlalchemy import Column, String, Text, Boolean, JSON, Integer, DateTime
from app.config.database import Base
import uuid
from datetime import datetime


def generate_uuid():
    """生成 UUID 字符串"""
    return str(uuid.uuid4())


# ============================================
# 用户模型
# ============================================
class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)  # 添加索引优化查询
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True)
    role = Column(String(10), default='USER')
    enterprise_name = Column(String(100))
    approval_status = Column(String(10), default='PENDING')
    is_certified = Column(Boolean, default=False)
    avatar_url = Column(Text)
    quota = Column(JSON)  # 用户额度：{lawyerLetters: int, consultations: int}


# ============================================
# 文档模板模型
# ============================================
class DocumentTemplate(Base):
    """文档模板表"""
    __tablename__ = "document_templates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    content = Column(Text)
    file_url = Column(Text)


# ============================================
# 文档分类模型
# ============================================
class DocCategory(Base):
    """文档分类表"""
    __tablename__ = "doc_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================
# 风险场景模型
# ============================================
class RiskScenario(Base):
    """风险场景表"""
    __tablename__ = "risk_scenarios"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    risk_level = Column(String(10))
    content = Column(Text)
    questions = Column(Text)  # JSON string


# ============================================
# 证据清单模型
# ============================================
class EvidenceList(Base):
    """证据清单表"""
    __tablename__ = "evidence_lists"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    items = Column(Text)  # JSON string


# ============================================
# 民法典条文模型
# ============================================
class CivilCodeArticle(Base):
    """民法典条文表"""
    __tablename__ = "civil_code_articles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)


# ============================================
# 企业模型
# ============================================
class Enterprise(Base):
    """企业表"""
    __tablename__ = "enterprises"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)


# ============================================
# 系统配置模型
# ============================================
class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    enable_phone_login = Column(Boolean, default=True)
    welcome_message = Column(Text)
    ai_knowledge_base = Column(Text)
    enterprise_logo = Column(Text)
    splash_image = Column(Text)
    enable_splash_screen = Column(Boolean, default=True)  # 是否启用品牌开屏页
    renovation_items = Column(Text)  # JSON string, 装修巡查项配置


# ============================================
# 自定义海报模型
# ============================================
class CustomPoster(Base):
    """自定义海报表"""
    __tablename__ = "custom_posters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    image_url = Column(Text)  # 改为存储图片 URL 而不是 base64


# ============================================
# 联系二维码模型
# ============================================
class ContactQRCode(Base):
    """联系二维码表"""
    __tablename__ = "contact_qr_codes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    image_url = Column(Text)  # 改为存储图片 URL 而不是 base64


# ============================================
# 催收记录模型 (更新以匹配实际数据库)
# ============================================
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


# ============================================
# 话术库模型 (更新以匹配实际数据库)
# ============================================
class Script(Base):
    """话术库表"""
    __tablename__ = "scripts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    category = Column(String(50))
    # content 字段已移除，统一使用 steps 存储话术内容
    steps = Column(JSON)  # 存储步骤列表：[{label, content, action}]
    is_active = Column(String(5), default="1")
    created_at = Column(String(30))
    updated_at = Column(String(30))


# ============================================
# 应急预案模型 (更新以匹配实际数据库)
# ============================================
class SOP(Base):
    """应急预案表"""
    __tablename__ = "sops"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    category = Column(String(50))
    content = Column(Text)
    steps = Column(Text)  # JSON string
    is_active = Column(String(5), default="1")
    created_at = Column(String(30))
    updated_at = Column(String(30))


# ============================================
# 装修巡查记录模型 (更新以匹配实际数据库)
# ============================================
class RenovationRecord(Base):
    """装修巡查记录表"""
    __tablename__ = "renovation_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=False, index=True)
    property_unit = Column(String(200), nullable=False)
    check_date = Column(String(20))
    check_result = Column(String(20))
    violations = Column(Text)
    images = Column(Text)  # JSON string
    inspector = Column(String(100), nullable=False)
    notes = Column(Text)
    status = Column(String(20), default='PENDING')
    enterprise_name = Column(String(100))
    created_at = Column(String(30))
    updated_at = Column(String(30))


# ============================================
# VIP等级配置模型 (更新以匹配实际数据库)
# ============================================
class VipLevel(Base):
    """VIP等级配置表"""
    __tablename__ = "vip_levels"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    level_name = Column(String(50), nullable=False)
    level_code = Column(String(20))
    min_amount = Column(String(20), nullable=False, default="0")
    max_amount = Column(String(20))
    benefits = Column(Text)  # JSON string
    selectable_projects_count = Column(String(10), default="0")  # 专项服务可选数量
    sort_order = Column(String(10), default="0")
    is_active = Column(String(5), default="1")
    created_at = Column(String(30))
    updated_at = Column(String(30))


# ============================================
# 企业统计数据模型 (更新以匹配实际数据库)
# ============================================
class EnterpriseStats(Base):
    """企业统计数据表"""
    __tablename__ = "enterprise_stats"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    enterprise_name = Column(String(100), unique=True, nullable=False, index=True)
    total_cases = Column(String(10), default="0")
    resolved_cases = Column(String(10), default="0")
    total_arrears = Column(String(20), default="0")
    collected_amount = Column(String(20), default="0")
    collection_rate = Column(String(10), default="0")
    last_calculated_date = Column(String(20))
    created_at = Column(String(30))
    updated_at = Column(String(30))


# ============================================
# 专项服务模型 (精简版 - 2026-01-16)
# ============================================
class SpecialProject(Base):
    """专项服务表"""
    __tablename__ = "special_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    description = Column(Text)


# ============================================
# 法务体检题目模型 (更新以匹配实际数据库)
# ============================================
class HealthCheckSection(Base):
    """法务体检题目表"""
    __tablename__ = "health_check_sections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    section_title = Column(String(200), nullable=False)
    section_description = Column(Text)
    category = Column(String(50))
    questions = Column(Text, nullable=False)  # JSON string
    weight = Column(String(10), default="1")
    sort_order = Column(String(10), default="0")
    is_active = Column(String(5), default="1")
    created_at = Column(String(30))
    updated_at = Column(String(30))


# ============================================
# 服务请求模型 (更新以匹配实际数据库)
# ============================================
class ServiceRequest(Base):
    """服务请求表"""
    __tablename__ = "service_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=False, index=True)
    enterprise_name = Column(String(100))
    request_type = Column(String(50), nullable=False)
    title = Column(String(200))
    description = Column(Text, nullable=False)
    status = Column(String(20), default='PENDING')
    priority = Column(String(10), default='NORMAL')
    admin_response = Column(Text)
    resolved_at = Column(String(30))
    created_at = Column(String(30))
    updated_at = Column(String(30))