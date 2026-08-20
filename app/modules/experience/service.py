from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AppError
from app.modules.experience.model import Experience
from app.modules.experience.schema import ExperienceCreate, ExperienceUpdate
from app.modules.experience.repository import experience_repository

class ExperienceService:
    async def create(self, db: AsyncSession, data: ExperienceCreate) -> Experience:
        obj = Experience(**data.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def list(self, db: AsyncSession, public_only: bool = False) -> list[Experience]:
        return await experience_repository.list(db, public_only)

    async def get(self, db: AsyncSession, id: UUID) -> Experience:
        obj = await experience_repository.get(db, id)
        if not obj:
            raise AppError("EXPERIENCE_NOT_FOUND", "Experience not found", 404)
        return obj

    async def update(self, db: AsyncSession, id: UUID, data: ExperienceUpdate) -> Experience:
        obj = await self.get(db, id)
        for key, value in data.model_dump().items():
            setattr(obj, key, value)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, id: UUID) -> None:
        obj = await self.get(db, id)
        await db.delete(obj)
        await db.commit()

experience_service = ExperienceService()
