from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AppError
from app.modules.profile.model import Profile
from app.modules.profile.schema import ProfileUpdate
from app.modules.profile.repository import profile_repository

class ProfileService:
    async def get_or_none(self, db: AsyncSession) -> Profile | None:
        return await profile_repository.get_or_none(db)

    async def get_public(self, db: AsyncSession) -> Profile:
        obj = await self.get_or_none(db)
        if not obj:
            raise AppError("PROFILE_NOT_FOUND", "Profile is not configured", 404)
        return obj

    async def upsert(self, db: AsyncSession, data: ProfileUpdate) -> Profile:
        obj = await self.get_or_none(db)
        payload = data.model_dump()
        if obj is None:
            obj = Profile(**payload)
            db.add(obj)
        else:
            for key, value in payload.items():
                setattr(obj, key, value)
        await db.commit()
        await db.refresh(obj)
        return obj

profile_service = ProfileService()
