from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.profile.model import Profile

class ProfileRepository:
    async def get_or_none(self, db: AsyncSession) -> Profile | None:
        return await db.scalar(select(Profile).order_by(Profile.created_at.asc()).limit(1))

profile_repository = ProfileRepository()
