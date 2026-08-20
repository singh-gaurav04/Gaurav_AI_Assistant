from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.modules.faq.schema import FaqCreate, FaqOut, FaqUpdate
from app.modules.faq.service import faq_service

public_router = APIRouter(tags=["Portfolio"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])


@public_router.get("/faqs")
async def public_faqs(db: AsyncSession = Depends(get_db)):
    items = await faq_service.list(db, public_only=True)
    return {"success": True, "data": [FaqOut.model_validate(x) for x in items]}


@admin_router.post("/faqs", status_code=201)
async def create_faq(payload: FaqCreate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": FaqOut.model_validate(await faq_service.create(db, payload))}


@admin_router.get("/faqs")
async def list_faqs(db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": [FaqOut.model_validate(x) for x in await faq_service.list(db)]}


@admin_router.get("/faqs/{id}")
async def get_faq(id: UUID, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": FaqOut.model_validate(await faq_service.get(db, id))}


@admin_router.put("/faqs/{id}")
async def update_faq(id: UUID, payload: FaqUpdate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": FaqOut.model_validate(await faq_service.update(db, id, payload))}


@admin_router.delete("/faqs/{id}", status_code=204)
async def delete_faq(id: UUID, db: AsyncSession = Depends(get_db)):
    await faq_service.delete(db, id)
