"""
业务领域模块

采用领域驱动设计（DDD）思想，将应用按业务领域划分为独立模块。
每个领域模块包含：models, schemas, service, router, tests
"""

from app.domains import auth, users, collections, documents, risks, evidence, civil_code

__all__ = [
    "auth",
    "users",
    "collections",
    "documents",
    "risks",
    "evidence",
    "civil_code",
]