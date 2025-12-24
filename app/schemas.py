from pydantic import BaseModel
from typing import Optional, List
import json

class UserBase(BaseModel):
    username: str
    phone_number: Optional[str] = None
    enterprise_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone_number: Optional[str] = None
    enterprise_name: Optional[str] = None
    approval_status: Optional[str] = None
    is_certified: Optional[bool] = None

class User(UserBase):
    id: str
    role: str
    approval_status: str
    is_certified: bool
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class DocumentTemplateBase(BaseModel):
    title: str
    category: str
    description: Optional[str] = None
    content: Optional[str] = None

class DocumentTemplateCreate(DocumentTemplateBase):
    pass

class DocumentTemplate(DocumentTemplateBase):
    id: str
    file_url: Optional[str] = None

    class Config:
        from_attributes = True

class RiskScenarioBase(BaseModel):
    title: str
    risk_level: Optional[str] = None
    content: Optional[str] = None
    questions: Optional[List[str]] = []

class RiskScenarioCreate(RiskScenarioBase):
    pass

class RiskScenario(RiskScenarioBase):
    id: str

    class Config:
        from_attributes = True

class EvidenceListBase(BaseModel):
    title: str
    items: Optional[List[str]] = []

class EvidenceListCreate(EvidenceListBase):
    pass

class EvidenceList(EvidenceListBase):
    id: str

    class Config:
        from_attributes = True

class CivilCodeArticleBase(BaseModel):
    title: str
    content: str

class CivilCodeArticleCreate(CivilCodeArticleBase):
    pass

class CivilCodeArticle(CivilCodeArticleBase):
    id: str

    class Config:
        from_attributes = True

class EnterpriseBase(BaseModel):
    name: str

class EnterpriseCreate(EnterpriseBase):
    pass

class Enterprise(EnterpriseBase):
    id: str

    class Config:
        from_attributes = True

class SystemConfigBase(BaseModel):
    enable_phone_login: bool = True
    welcome_message: Optional[str] = None
    ai_knowledge_base: Optional[str] = None
    enterprise_logo: Optional[str] = None
    splash_image: Optional[str] = None

class SystemConfigUpdate(SystemConfigBase):
    pass

class SystemConfig(SystemConfigBase):
    id: str

    class Config:
        from_attributes = True

class CustomPosterBase(BaseModel):
    name: str
    image_base64: str

class CustomPosterCreate(CustomPosterBase):
    pass

class CustomPoster(CustomPosterBase):
    id: str

    class Config:
        from_attributes = True

class ContactQRCodeBase(BaseModel):
    name: str
    image_base64: str

class ContactQRCodeCreate(ContactQRCodeBase):
    pass

class ContactQRCode(ContactQRCodeBase):
    id: str

    class Config:
        from_attributes = True