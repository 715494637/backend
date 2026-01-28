"""
物业公司领域 - SQLAlchemy 模型
"""

from sqlalchemy import Column, String
from app.db import Base
from app.utils import generate_uuid


class Enterprise(Base):
    """企业表"""
    __tablename__ = "enterprises"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
