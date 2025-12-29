"""
Pydantic 数据模型定义

使用 Pydantic V2 语法定义所有 API 请求和响应的数据结构
"""

from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import Optional, List, Any
import json
from app.utils.logger import logger


# ============================================
# 用户相关 Schema
# ============================================

class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    phone_number: Optional[str] = None
    enterprise_name: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模型"""
    password: str


class AdminUserCreate(BaseModel):
    """管理员创建用户模型"""
    username: str
    password: str
    phone_number: Optional[str] = None
    enterprise_name: Optional[str] = None
    role: str = "USER"
    approval_status: str = "APPROVED"
    is_certified: bool = True


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    phone_number: Optional[str] = None
    enterprise_name: Optional[str] = None
    approval_status: Optional[str] = None
    is_certified: Optional[bool] = None
    avatar_url: Optional[str] = None


class User(UserBase):
    """用户响应模型"""
    id: str
    role: str
    approval_status: str
    is_certified: bool
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str
    user: User


# ============================================
# 文档模板相关 Schema
# ============================================

class DocumentTemplateBase(BaseModel):
    """文档模板基础模型"""
    title: str
    category: str
    description: Optional[str] = None
    content: Optional[str] = None
    file_url: Optional[str] = None


class DocumentTemplateCreate(DocumentTemplateBase):
    """文档模板创建模型"""
    pass


class DocumentTemplate(DocumentTemplateBase):
    """文档模板响应模型"""
    id: str
    file_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 风险场景相关 Schema
# ============================================

class RiskScenarioBase(BaseModel):
    """风险场景基础模型"""
    title: str
    risk_level: Optional[str] = None
    content: Optional[str] = None
    questions: Optional[List[str]] = []

    @field_validator('questions', mode='before')
    @classmethod
    def parse_questions(cls, v: Any) -> List[str]:
        """解析 questions 字段，支持 JSON 字符串或列表"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                logger.warning(f"questions 字段 JSON 解析失败: {e}")
                return []
        elif isinstance(v, list):
            return v
        return []


class RiskScenarioCreate(RiskScenarioBase):
    """风险场景创建模型"""
    pass


class RiskScenario(RiskScenarioBase):
    """风险场景响应模型"""
    id: str

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def validate_questions(cls, data: Any) -> Any:
        """验证并转换 questions 字段，将 JSON 字符串转换为列表"""
        if isinstance(data, dict) and 'questions' in data:
            if isinstance(data['questions'], str):
                try:
                    data['questions'] = json.loads(data['questions'])
                except:
                    data['questions'] = []
        return data


# ============================================
# 证据清单相关 Schema
# ============================================

class EvidenceListBase(BaseModel):
    """证据清单基础模型"""
    title: str
    items: Optional[List[str]] = []

    @field_validator('items', mode='before')
    @classmethod
    def parse_items(cls, v: Any) -> List[str]:
        """解析 items 字段，支持 JSON 字符串或列表"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        elif isinstance(v, list):
            return v
        return []


class EvidenceListCreate(EvidenceListBase):
    """证据清单创建模型"""
    pass


class EvidenceList(EvidenceListBase):
    """证据清单响应模型"""
    id: str

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def validate_items(cls, data: Any) -> Any:
        """验证并转换 items 字段，将 JSON 字符串转换为列表"""
        if isinstance(data, dict) and 'items' in data:
            if isinstance(data['items'], str):
                try:
                    data['items'] = json.loads(data['items'])
                except:
                    data['items'] = []
        return data


# ============================================
# 民法典相关 Schema
# ============================================

class CivilCodeArticleBase(BaseModel):
    """民法典基础模型"""
    title: str
    content: str


class CivilCodeArticleCreate(CivilCodeArticleBase):
    """民法典创建模型"""
    pass


class CivilCodeArticle(CivilCodeArticleBase):
    """民法典响应模型"""
    id: str

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 企业相关 Schema
# ============================================

class EnterpriseBase(BaseModel):
    """企业基础模型"""
    name: str


class EnterpriseCreate(EnterpriseBase):
    """企业创建模型"""
    pass


class Enterprise(EnterpriseBase):
    """企业响应模型"""
    id: str

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 系统配置相关 Schema
# ============================================

class SystemConfigBase(BaseModel):
    """系统配置基础模型"""
    enable_phone_login: bool = True
    welcome_message: Optional[str] = None
    ai_knowledge_base: Optional[str] = None
    enterprise_logo: Optional[str] = None
    splash_image: Optional[str] = None


class SystemConfigUpdate(SystemConfigBase):
    """系统配置更新模型"""
    pass


class SystemConfig(SystemConfigBase):
    """系统配置响应模型"""
    id: str

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 自定义海报相关 Schema
# ============================================

class CustomPosterBase(BaseModel):
    """自定义海报基础模型"""
    name: str
    image_base64: str


class CustomPosterCreate(CustomPosterBase):
    """自定义海报创建模型"""
    pass


class CustomPoster(CustomPosterBase):
    """自定义海报响应模型"""
    id: str

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 联系二维码相关 Schema
# ============================================

class ContactQRCodeBase(BaseModel):
    """联系二维码基础模型"""
    name: str
    image_base64: str


class ContactQRCodeCreate(ContactQRCodeBase):
    """联系二维码创建模型"""
    pass


class ContactQRCode(ContactQRCodeBase):
    """联系二维码响应模型"""
    id: str

    model_config = ConfigDict(from_attributes=True)
