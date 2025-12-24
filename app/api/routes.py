from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
import json
from typing import List

from app.database import get_db
from app.models import User, DocumentTemplate, RiskScenario, EvidenceList, CivilCodeArticle, Enterprise, SystemConfig, CustomPoster, ContactQRCode
from app.schemas import (
    UserCreate, UserUpdate, User as UserSchema, LoginRequest, Token,
    DocumentTemplateCreate, DocumentTemplate as DocumentTemplateSchema,
    RiskScenarioCreate, RiskScenario as RiskScenarioSchema,
    EvidenceListCreate, EvidenceList as EvidenceListSchema,
    CivilCodeArticleCreate, CivilCodeArticle as CivilCodeArticleSchema,
    EnterpriseCreate, Enterprise as EnterpriseSchema,
    SystemConfigUpdate, SystemConfig as SystemConfigSchema,
    CustomPosterCreate, CustomPoster as CustomPosterSchema,
    ContactQRCodeCreate, ContactQRCode as ContactQRCodeSchema
)
from app.auth import create_access_token, get_current_user, get_current_admin

router = APIRouter()

# 认证相关
@router.post("/auth/login", response_model=Token)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username, User.password == request.password).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user.approval_status != "APPROVED" and user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="账号未通过审批")

    token_data = {"sub": user.id, "role": user.role}
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserSchema.from_orm(user)
    }

@router.post("/auth/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查手机号是否存在
    if user_data.phone_number and db.query(User).filter(User.phone_number == user_data.phone_number).first():
        raise HTTPException(status_code=400, detail="手机号已被注册")

    # 创建新用户
    new_user = User(
        username=user_data.username,
        password=user_data.password,
        phone_number=user_data.phone_number,
        enterprise_name=user_data.enterprise_name,
        role="USER",
        approval_status="PENDING"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "注册成功，等待管理员审批"}

@router.post("/auth/send-sms")
async def send_sms(phone: str):
    # 模拟短信发送
    return {"message": "验证码已发送"}

# 用户管理
@router.get("/users", response_model=List[UserSchema])
async def get_users(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.put("/users/{user_id}/approve")
async def approve_user(user_id: str, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.approval_status = "APPROVED"
    db.commit()

    return {"message": "用户审批成功"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    db.delete(user)
    db.commit()

    return {"message": "用户删除成功"}

# 文档模板管理
@router.get("/documents", response_model=List[DocumentTemplateSchema])
async def get_documents(db: Session = Depends(get_db)):
    documents = db.query(DocumentTemplate).all()
    return documents

@router.post("/documents", response_model=DocumentTemplateSchema)
async def create_document(doc_data: DocumentTemplateCreate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    new_doc = DocumentTemplate(**doc_data.dict())
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@router.put("/documents/{doc_id}", response_model=DocumentTemplateSchema)
async def update_document(doc_id: str, doc_data: DocumentTemplateCreate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    doc = db.query(DocumentTemplate).filter(DocumentTemplate.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    for key, value in doc_data.dict().items():
        setattr(doc, key, value)

    db.commit()
    db.refresh(doc)
    return doc

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    doc = db.query(DocumentTemplate).filter(DocumentTemplate.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    db.delete(doc)
    db.commit()
    return {"message": "文档删除成功"}

# 风险场景管理
@router.get("/risks", response_model=List[RiskScenarioSchema])
async def get_risks(db: Session = Depends(get_db)):
    risks = db.query(RiskScenario).all()
    return [RiskScenarioSchema(id=r.id, title=r.title, risk_level=r.risk_level, content=r.content, questions=json.loads(r.questions or "[]")) for r in risks]

@router.post("/risks", response_model=RiskScenarioSchema)
async def create_risk(risk_data: RiskScenarioCreate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    new_risk = RiskScenario(
        title=risk_data.title,
        risk_level=risk_data.risk_level,
        content=risk_data.content,
        questions=json.dumps(risk_data.questions or [])
    )
    db.add(new_risk)
    db.commit()
    db.refresh(new_risk)
    return RiskScenarioSchema(id=new_risk.id, title=new_risk.title, risk_level=new_risk.risk_level, content=new_risk.content, questions=json.loads(new_risk.questions or "[]"))

@router.put("/risks/{risk_id}", response_model=RiskScenarioSchema)
async def update_risk(risk_id: str, risk_data: RiskScenarioCreate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    risk = db.query(RiskScenario).filter(RiskScenario.id == risk_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="风险场景不存在")

    risk.title = risk_data.title
    risk.risk_level = risk_data.risk_level
    risk.content = risk_data.content
    risk.questions = json.dumps(risk_data.questions or [])

    db.commit()
    db.refresh(risk)
    return RiskScenarioSchema(id=risk.id, title=risk.title, risk_level=risk.risk_level, content=risk.content, questions=json.loads(risk.questions or "[]"))

@router.delete("/risks/{risk_id}")
async def delete_risk(risk_id: str, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    risk = db.query(RiskScenario).filter(RiskScenario.id == risk_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="风险场景不存在")

    db.delete(risk)
    db.commit()
    return {"message": "风险场景删除成功"}

# 证据清单管理
@router.get("/evidence", response_model=List[EvidenceListSchema])
async def get_evidence(db: Session = Depends(get_db)):
    evidence = db.query(EvidenceList).all()
    return [EvidenceListSchema(id=e.id, title=e.title, items=json.loads(e.items or "[]")) for e in evidence]

@router.post("/evidence", response_model=EvidenceListSchema)
async def create_evidence(evidence_data: EvidenceListCreate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    new_evidence = EvidenceList(
        title=evidence_data.title,
        items=json.dumps(evidence_data.items or [])
    )
    db.add(new_evidence)
    db.commit()
    db.refresh(new_evidence)
    return EvidenceListSchema(id=new_evidence.id, title=new_evidence.title, items=json.loads(new_evidence.items or "[]"))

@router.put("/evidence/{evidence_id}", response_model=EvidenceListSchema)
async def update_evidence(evidence_id: str, evidence_data: EvidenceListCreate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    evidence = db.query(EvidenceList).filter(EvidenceList.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="证据清单不存在")

    evidence.title = evidence_data.title
    evidence.items = json.dumps(evidence_data.items or [])

    db.commit()
    db.refresh(evidence)
    return EvidenceListSchema(id=evidence.id, title=evidence.title, items=json.loads(evidence.items or "[]"))

@router.delete("/evidence/{evidence_id}")
async def delete_evidence(evidence_id: str, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    evidence = db.query(EvidenceList).filter(EvidenceList.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="证据清单不存在")

    db.delete(evidence)
    db.commit()
    return {"message": "证据清单删除成功"}

# 民法典管理
@router.get("/civil-code", response_model=List[CivilCodeArticleSchema])
async def get_civil_code(db: Session = Depends(get_db)):
    articles = db.query(CivilCodeArticle).all()
    return articles

@router.post("/civil-code", response_model=CivilCodeArticleSchema)
async def create_civil_code(article_data: CivilCodeArticleCreate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    new_article = CivilCodeArticle(**article_data.dict())
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    return new_article

@router.put("/civil-code/{article_id}", response_model=CivilCodeArticleSchema)
async def update_civil_code(article_id: str, article_data: CivilCodeArticleCreate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    article = db.query(CivilCodeArticle).filter(CivilCodeArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="民法典条文不存在")

    for key, value in article_data.dict().items():
        setattr(article, key, value)

    db.commit()
    db.refresh(article)
    return article

@router.delete("/civil-code/{article_id}")
async def delete_civil_code(article_id: str, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    article = db.query(CivilCodeArticle).filter(CivilCodeArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="民法典条文不存在")

    db.delete(article)
    db.commit()
    return {"message": "民法典条文删除成功"}

# 物业公司管理
@router.get("/enterprises", response_model=List[str])
async def get_enterprises(db: Session = Depends(get_db)):
    enterprises = db.query(Enterprise).all()
    return [e.name for e in enterprises]

@router.post("/enterprises")
async def create_enterprise(name: str, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    if db.query(Enterprise).filter(Enterprise.name == name).first():
        raise HTTPException(status_code=400, detail="物业公司已存在")

    new_enterprise = Enterprise(name=name)
    db.add(new_enterprise)
    db.commit()
    return {"message": "物业公司添加成功"}

@router.delete("/enterprises/{name}")
async def delete_enterprise(name: str, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    enterprise = db.query(Enterprise).filter(Enterprise.name == name).first()
    if not enterprise:
        raise HTTPException(status_code=404, detail="物业公司不存在")

    db.delete(enterprise)
    db.commit()
    return {"message": "物业公司删除成功"}

# 系统配置管理
@router.get("/config", response_model=SystemConfigSchema)
async def get_config(db: Session = Depends(get_db)):
    config = db.query(SystemConfig).first()
    if not config:
        config = SystemConfig(
            enable_phone_login=True,
            welcome_message="您好！我是东元物业法务助手。我可以为您提供《民法典》咨询、文书草拟及风险建议。（回答仅供参考）"
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

@router.put("/config")
async def update_config(config_data: SystemConfigUpdate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    config = db.query(SystemConfig).first()
    if not config:
        config = SystemConfig()
        db.add(config)

    for key, value in config_data.dict(exclude_unset=True).items():
        setattr(config, key, value)

    db.commit()
    return {"message": "系统配置更新成功"}

# 海报管理
@router.get("/posters", response_model=List[CustomPosterSchema])
async def get_posters(db: Session = Depends(get_db)):
    posters = db.query(CustomPoster).all()
    return posters

@router.post("/posters", response_model=CustomPosterSchema)
async def create_poster(poster_data: CustomPosterCreate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    new_poster = CustomPoster(**poster_data.dict())
    db.add(new_poster)
    db.commit()
    db.refresh(new_poster)
    return new_poster

@router.delete("/posters/{poster_id}")
async def delete_poster(poster_id: str, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    poster = db.query(CustomPoster).filter(CustomPoster.id == poster_id).first()
    if not poster:
        raise HTTPException(status_code=404, detail="海报不存在")

    db.delete(poster)
    db.commit()
    return {"message": "海报删除成功"}

# 联系二维码管理
@router.get("/contact-qr", response_model=List[ContactQRCodeSchema])
async def get_contact_qr(db: Session = Depends(get_db)):
    qr_codes = db.query(ContactQRCode).all()
    return qr_codes

@router.post("/contact-qr", response_model=ContactQRCodeSchema)
async def create_contact_qr(qr_data: ContactQRCodeCreate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    new_qr = ContactQRCode(**qr_data.dict())
    db.add(new_qr)
    db.commit()
    db.refresh(new_qr)
    return new_qr

@router.delete("/contact-qr/{qr_id}")
async def delete_contact_qr(qr_id: str, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    qr = db.query(ContactQRCode).filter(ContactQRCode.id == qr_id).first()
    if not qr:
        raise HTTPException(status_code=404, detail="二维码不存在")

    db.delete(qr)
    db.commit()
    return {"message": "二维码删除成功"}