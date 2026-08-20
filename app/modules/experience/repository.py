from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.experience.model import Experience

class ExperienceRepository:
    async def list(self, db: AsyncSession, public_only: bool = False):
        q = select(Experience)
        if public_only:
            q = q.where(Experience.is_published.is_(True))
        q = q.order_by(Experience.display_order.asc(), Experience.created_at.desc())
        return list((await db.scalars(q)).all())

    async def get(self, db: AsyncSession, id: UUID):
        return await db.get(Experience, id)

experience_repository = ExperienceRepository()
