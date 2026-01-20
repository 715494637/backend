"""
服务模块

导出所有业务逻辑服务类，简化导入路径
"""

from app.services.user_service import UserService
from app.services.document_service import DocumentService
from app.services.risk_service import RiskService
from app.services.enterprise_service import EnterpriseService
from app.services.evidence_service import EvidenceService
from app.services.poster_service import PosterService
from app.services.civil_code_service import CivilCodeService
from app.services.config_service import ConfigService
from app.services.contact_qr_service import ContactQRService
from app.services.imagebb_service import ImageBBService
from app.services.collection_service import CollectionService
from app.services.script_service import ScriptService
from app.services.sop_service import SOPService
from app.services.renovation_service import RenovationService
from app.services.vip_service import VipService
from app.services.special_project_service import SpecialProjectService
from app.services.health_check_service import HealthCheckService
from app.services.service_request_service import ServiceRequestService

__all__ = [
    "UserService",
    "DocumentService",
    "RiskService",
    "EnterpriseService",
    "EvidenceService",
    "PosterService",
    "CivilCodeService",
    "ConfigService",
    "ContactQRService",
    "ImageBBService",
    "CollectionService",
    "ScriptService",
    "SOPService",
    "RenovationService",
    "VipService",
    "SpecialProjectService",
    "HealthCheckService",
    "ServiceRequestService"
]
