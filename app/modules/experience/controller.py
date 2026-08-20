from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.modules.experience.schema import ExperienceCreate, ExperienceUpdate, ExperienceOut
from app.modules.experience.service import experience_service

public_router = APIRouter(tags=["Portfolio"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

@public_router.get("/experiences")
async def public_experiences(db: AsyncSession = Depends(get_db)):
    items = await experience_service.list(db, public_only=True)
    return {"success": True, "data": [ExperienceOut.model_validate(x) for x in items]}

@admin_router.post("/experiences", status_code=201)
async def create_experience(payload: ExperienceCreate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": ExperienceOut.model_validate(await experience_service.create(db, payload))}

@admin_router.get("/experiences")
async def list_experiences(db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": [ExperienceOut.model_validate(x) for x in await experience_service.list(db)]}

@admin_router.put("/experiences/{id}")
async def update_experience(id: UUID, payload: ExperienceUpdate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": ExperienceOut.model_validate(await experience_service.update(db, id, payload))}

@admin_router.delete("/experiences/{id}", status_code=204)
async def delete_experience(id: UUID, db: AsyncSession = Depends(get_db)):
    await experience_service.delete(db, id)
