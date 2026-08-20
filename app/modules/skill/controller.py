from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.modules.skill.schema import SkillCreate, SkillUpdate, SkillOut
from app.modules.skill.service import skill_service

public_router = APIRouter(tags=["Portfolio"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

@public_router.get("/skills")
async def public_skills(db: AsyncSession = Depends(get_db)):
    items = await skill_service.list(db, public_only=True)
    return {"success": True, "data": [SkillOut.model_validate(x) for x in items]}

@admin_router.post("/skills", status_code=201)
async def create_skill(payload: SkillCreate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": SkillOut.model_validate(await skill_service.create(db, payload))}

@admin_router.get("/skills")
async def list_skills(db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": [SkillOut.model_validate(x) for x in await skill_service.list(db)]}

@admin_router.get("/skills/{id}")
async def get_skill(id: UUID, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": SkillOut.model_validate(await skill_service.get(db, id))}

@admin_router.put("/skills/{id}")
async def update_skill(id: UUID, payload: SkillUpdate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": SkillOut.model_validate(await skill_service.update(db, id, payload))}

@admin_router.delete("/skills/{id}", status_code=204)
async def delete_skill(id: UUID, db: AsyncSession = Depends(get_db)):
    await skill_service.delete(db, id)
