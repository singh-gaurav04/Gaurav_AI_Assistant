from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.modules.profile.schema import ProfileUpdate, ProfileOut
from app.modules.profile.service import profile_service

public_router = APIRouter(tags=["Portfolio"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

@public_router.get("/profile")
async def public_profile(db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": ProfileOut.model_validate(await profile_service.get_public(db))}

@admin_router.get("/profile")
async def get_profile(db: AsyncSession = Depends(get_db)):
    obj = await profile_service.get_or_none(db)
    return {"success": True, "data": ProfileOut.model_validate(obj) if obj else None}

@admin_router.put("/profile")
async def update_profile(payload: ProfileUpdate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": ProfileOut.model_validate(await profile_service.upsert(db, payload))}
