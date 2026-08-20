from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.core.exceptions import AppError
from app.modules.email_template.seed import ensure_default_email_templates
from app.modules.email_template.model import EmailTemplate
from app.modules.email_template.schema import EmailTemplateUpdate, EmailTemplateOut

admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

@admin_router.get("/email-templates")
async def list_templates(db: AsyncSession = Depends(get_db)):
    await ensure_default_email_templates(db)
    items = (await db.scalars(select(EmailTemplate).order_by(EmailTemplate.name))).all()
    return {"success": True, "data": [EmailTemplateOut.model_validate(x) for x in items]}

@admin_router.put("/email-templates/{id}")
async def update_template(id: UUID, payload: EmailTemplateUpdate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(EmailTemplate, id)
    if not obj:
        raise AppError("EMAIL_TEMPLATE_NOT_FOUND", "Email template not found", 404)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return {"success": True, "data": EmailTemplateOut.model_validate(obj)}
