"""
法务体检领域 - SQLAlchemy 模型
"""

from sqlalchemy import Column, String, Text
from app.db import Base
from app.utils import generate_uuid


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
