from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.contact.schema import ContactCreate
from app.modules.contact.service import contact_service

public_router = APIRouter(tags=["Contact"])

@public_router.post("/contact", status_code=201)
async def submit(payload: ContactCreate, db: AsyncSession = Depends(get_db)):
    obj = await contact_service.create(db, payload)
    return {
        "success": True,
        "data": {"id": str(obj.id), "status": obj.status.value},
        "message": "Message saved. Confirmation emails have been sent.",
    }
