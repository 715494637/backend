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
    "ImageBBService"
]