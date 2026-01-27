"""
Pydantic 数据模型定义

使用 Pydantic V2 语法定义所有 API 请求和响应的数据结构
"""

from pydantic import BaseModel, ConfigDict, field_validator, model_validator, Field
from typing import Optional, List, Any, Literal
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
    password: Optional[str] = None  # 允许更新密码
    role: Optional[str] = None      # 允许管理员更新角色


class User(UserBase):
    """用户响应模型"""
    id: str
    role: str
    approval_status: str
    is_certified: bool
    avatar_url: Optional[str] = None
    quota: Optional[dict] = None  # 用户额度

    model_config = ConfigDict(from_attributes=True)


class UpdateQuotaRequest(BaseModel):
    """管理员更新用户额度请求模型"""
    operation: Literal['set', 'add', 'deduct'] = 'set'
    lawyer_letters: int = 0
    consultations: int = 0


class UserQuotaResponse(BaseModel):
    """用户额度响应模型"""
    lawyer_letters: int = 0
    consultations: int = 0


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str
    user: User


class TokenResponse(BaseModel):
    """轻量级登录响应模型（优化性能）"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str
    approval_status: str


# ============================================
# 文档模板相关 Schema
# ============================================

class CategoryCreate(BaseModel):
    """分类创建模型"""
    category: str = Field(..., description="分类名称")


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
# 文档分类相关 Schema
# ============================================

class DocCategoryBase(BaseModel):
    """文档分类基础模型"""
    name: str


class DocCategoryCreate(DocCategoryBase):
    """文档分类创建模型"""
    pass


class DocCategory(DocCategoryBase):
    """文档分类响应模型"""
    id: int
    created_at: Optional[str] = None

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
    enable_splash_screen: bool = True  # 是否启用品牌开屏页


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
    image_url: str  # 改为存储图片 URL


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
    image_url: str  # 改为存储图片 URL


class ContactQRCodeCreate(ContactQRCodeBase):
    """联系二维码创建模型"""
    pass


class ContactQRCode(ContactQRCodeBase):
    """联系二维码响应模型"""
    id: str

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 催收记录相关 Schema (新增)
# ============================================

class CollectionAction(BaseModel):
    """催收动作模型"""
    id: str
    date: int
    type: str
    note: str


class CollectionRecordBase(BaseModel):
    """催收记录基础模型"""
    owner_name: str
    room_number: str
    amount: float


class CollectionRecordCreate(CollectionRecordBase):
    """催收记录创建模型"""
    pass


class CollectionRecord(CollectionRecordBase):
    """催收记录响应模型"""
    id: str
    user_id: str
    history: Optional[List[CollectionAction]] = []

    model_config = ConfigDict(from_attributes=True)


class CollectionActionAdd(BaseModel):
    """添加催收动作模型"""
    type: str
    note: Optional[str] = None


# ============================================
# 话术库相关 Schema (新增)
# ============================================

class ScriptStep(BaseModel):
    """话术步骤模型"""
    label: str
    content: str


class ScriptBase(BaseModel):
    """话术基础模型"""
    title: str
    category: Optional[str] = None
    content: Optional[str] = None


class ScriptCreate(ScriptBase):
    """话术创建模型"""
    pass


class ScriptUpdate(BaseModel):
    """话术更新模型"""
    title: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None


class Script(ScriptBase):
    """话术响应模型"""
    id: str
    category: Optional[str] = None
    content: Optional[str] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 应急预案相关 Schema (新增)
# ============================================

class SOPBase(BaseModel):
    """SOP基础模型"""
    title: str
    category: Optional[str] = None
    content: Optional[str] = None
    steps: Optional[List[dict]] = None


class SOPCreate(SOPBase):
    """SOP创建模型"""
    pass


class SOPUpdate(BaseModel):
    """SOP更新模型"""
    title: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None
    steps: Optional[List[dict]] = None
    is_active: Optional[bool] = None


class SOP(SOPBase):
    """SOP响应模型"""
    id: str
    category: Optional[str] = None
    content: Optional[str] = None
    steps: Optional[List[dict]] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 装修巡查相关 Schema (新增)
# ============================================

class RenovationRecordBase(BaseModel):
    """装修巡查基础模型"""
    property_unit: Optional[str] = None
    check_date: Optional[str] = None
    check_result: Optional[str] = None
    violations: Optional[str] = None
    images: Optional[List[str]] = None
    inspector: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class RenovationRecordCreate(RenovationRecordBase):
    """装修巡查创建模型"""
    property_unit: str
    check_date: str


class RenovationRecordUpdate(BaseModel):
    """装修巡查更新模型"""
    property_unit: Optional[str] = None
    check_date: Optional[str] = None
    check_result: Optional[str] = None
    violations: Optional[str] = None
    images: Optional[List[str]] = None
    inspector: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class RenovationRecord(RenovationRecordBase):
    """装修巡查响应模型"""
    id: str
    user_id: Optional[str] = None
    enterprise_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================
# VIP等级相关 Schema (新增)
# ============================================

class VipRight(BaseModel):
    """VIP权益模型"""
    title: str
    desc: Optional[str] = None


class VipLevelBase(BaseModel):
    """VIP等级基础模型"""
    level_name: str
    level_code: str
    min_amount: float
    max_amount: Optional[float] = None
    benefits: Optional[dict] = None
    sort_order: int = 0


class VipLevelCreate(VipLevelBase):
    """VIP等级创建模型"""
    pass


class VipLevelUpdate(BaseModel):
    """VIP等级更新模型"""
    level_name: Optional[str] = None
    level_code: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    benefits: Optional[dict] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class VipLevel(VipLevelBase):
    """VIP等级响应模型"""
    id: str
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 企业统计相关 Schema (新增)
# ============================================

class EnterpriseStatsResponse(BaseModel):
    """企业统计响应模型"""
    id: str
    enterprise_name: str
    total_recovered_amount: float
    total_entrusted_amount: float
    entrusted_count: int

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 专项服务相关 Schema (新增)
# ============================================

class SpecialProjectBase(BaseModel):
    """专项服务基础模型"""
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    features: Optional[dict] = None


class SpecialProjectCreate(SpecialProjectBase):
    """专项服务创建模型"""
    pass


class SpecialProjectUpdate(BaseModel):
    """专项服务更新模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    features: Optional[dict] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class SpecialProject(SpecialProjectBase):
    """专项服务响应模型"""
    id: str
    is_active: bool = True
    sort_order: int = 0

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 法务体检相关 Schema (新增)
# ============================================

class HealthCheckQuestion(BaseModel):
    """法务体检题目模型"""
    id: str
    question: str
    options: Optional[List[dict]] = None


class HealthCheckSectionBase(BaseModel):
    """法务体检板块基础模型"""
    section_title: str
    section_description: Optional[str] = None
    category: str
    questions: List[dict]
    weight: int = 1
    sort_order: int = 0


class HealthCheckSectionCreate(HealthCheckSectionBase):
    """法务体检板块创建模型"""
    pass


class HealthCheckSectionUpdate(BaseModel):
    """法务体检板块更新模型"""
    section_title: Optional[str] = None
    section_description: Optional[str] = None
    category: Optional[str] = None
    questions: Optional[List[dict]] = None
    weight: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class HealthCheckSectionResponse(BaseModel):
    """法务体检板块响应模型"""
    id: str
    section_title: str
    section_description: Optional[str] = None
    category: str
    questions: List[dict]
    weight: int = 1
    sort_order: int = 0
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class HealthCheckSubmit(BaseModel):
    """法务体检提交模型"""
    answers: dict  # { "sectionIndex-questionIndex": value }


class HealthCheckReportResponse(BaseModel):
    """AI生成报告响应模型"""
    report: str
    risk_count: int
    recommendations: List[dict]


# ============================================
# 服务请求相关 Schema (新增)
# ============================================

class ServiceRequestBase(BaseModel):
    """服务请求基础模型"""
    request_type: str
    title: str
    description: str


class ServiceRequestCreate(ServiceRequestBase):
    """服务请求创建模型"""
    priority: str = "normal"


class ServiceRequestUpdate(BaseModel):
    """服务请求更新模型"""
    request_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None


class ServiceRequest(ServiceRequestBase):
    """服务请求响应模型"""
    id: str
    user_id: str
    enterprise_name: Optional[str] = None
    status: str = "pending"
    priority: str = "normal"
    admin_response: Optional[str] = None
    resolved_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
