"""
SQLAlchemy ORM 模型定义

定义所有数据库表的 ORM 模型
"""

from sqlalchemy import Column, String, Text, Boolean
from app.config.database import Base
import uuid


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
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True)
    role = Column(String(10), default='USER')
    enterprise_name = Column(String(100))
    approval_status = Column(String(10), default='PENDING')
    is_certified = Column(Boolean, default=False)
    avatar_url = Column(Text)


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