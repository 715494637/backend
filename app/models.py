from sqlalchemy import Column, String, Text, Boolean
from app.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
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

class DocumentTemplate(Base):
    __tablename__ = "document_templates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    content = Column(Text)
    file_url = Column(Text)

class RiskScenario(Base):
    __tablename__ = "risk_scenarios"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    risk_level = Column(String(10))
    content = Column(Text)
    questions = Column(Text)  # JSON string

class EvidenceList(Base):
    __tablename__ = "evidence_lists"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    items = Column(Text)  # JSON string

class CivilCodeArticle(Base):
    __tablename__ = "civil_code_articles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)

class Enterprise(Base):
    __tablename__ = "enterprises"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)

class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    enable_phone_login = Column(Boolean, default=True)
    welcome_message = Column(Text)
    ai_knowledge_base = Column(Text)
    enterprise_logo = Column(Text)
    splash_image = Column(Text)

class CustomPoster(Base):
    __tablename__ = "custom_posters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    image_base64 = Column(Text)

class ContactQRCode(Base):
    __tablename__ = "contact_qr_codes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    image_base64 = Column(Text)