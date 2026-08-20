from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.modules.contact.schema import ContactCreate, ContactAdminOut, ContactReply
from app.modules.contact.service import contact_service

public_router = APIRouter(tags=["Contact"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

@public_router.post("/contact", status_code=201)
async def submit(payload: ContactCreate, db: AsyncSession = Depends(get_db)):
    obj = await contact_service.create(db, payload)
    return {
        "success": True,
        "data": {"id": str(obj.id), "status": obj.status.value},
        "message": "Message saved. Confirmation emails have been sent.",
    }

@admin_router.get("/contacts")
async def contacts(db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": [ContactAdminOut.model_validate(x) for x in await contact_service.list(db)]}

@admin_router.get("/contacts/{id}")
async def contact_detail(id: UUID, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": ContactAdminOut.model_validate(await contact_service.get(db, id))}

@admin_router.patch("/contacts/{id}/reply")
async def reply_contact(id: UUID, payload: ContactReply, db: AsyncSession = Depends(get_db)):
    obj = await contact_service.reply(db, id, payload)
    return {"success": True, "data": {"status": obj.status}}

@admin_router.patch("/contacts/{id}/read")
async def mark_read(id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await contact_service.mark_read(db, id)
    return {"success": True, "data": {"status": obj.status}}

@admin_router.patch("/contacts/{id}/archive")
async def archive(id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await contact_service.archive(db, id)
    return {"success": True, "data": {"status": obj.status}}
