"""
联系二维码领域 - SQLAlchemy 模型
"""

from sqlalchemy import Column, String, Text
from app.db import Base
import uuid


def generate_uuid():
    """生成 UUID"""
    return str(uuid.uuid4())


class ContactQRCode(Base):
    """联系二维码表"""
    __tablename__ = "contact_qr_codes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    image_url = Column(Text)  # 存储图片 URL

    def __repr__(self):
        return f"<ContactQRCode(id={self.id}, name={self.name})>"
