from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.modules.certification.schema import CertificationCreate, CertificationUpdate, CertificationOut
from app.modules.certification.service import certification_service

public_router = APIRouter(tags=["Portfolio"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

@public_router.get("/certifications")
async def public_certifications(db: AsyncSession = Depends(get_db)):
    items = await certification_service.list(db, public_only=True)
    return {"success": True, "data": [CertificationOut.model_validate(x) for x in items]}

@admin_router.post("/certifications", status_code=201)
async def create_certification(payload: CertificationCreate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": CertificationOut.model_validate(await certification_service.create(db, payload))}

@admin_router.get("/certifications")
async def list_certifications(db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": [CertificationOut.model_validate(x) for x in await certification_service.list(db)]}

@admin_router.put("/certifications/{id}")
async def update_certification(id: UUID, payload: CertificationUpdate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": CertificationOut.model_validate(await certification_service.update(db, id, payload))}

@admin_router.delete("/certifications/{id}", status_code=204)
async def delete_certification(id: UUID, db: AsyncSession = Depends(get_db)):
    await certification_service.delete(db, id)
