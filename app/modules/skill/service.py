from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AppError
from app.modules.skill.model import Skill
from app.modules.skill.schema import SkillCreate, SkillUpdate
from app.modules.skill.repository import skill_repository

class SkillService:
    async def create(self, db: AsyncSession, data: SkillCreate):
        obj = Skill(**data.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def list(self, db: AsyncSession, public_only=False):
        return await skill_repository.list(db, public_only)

    async def get(self, db: AsyncSession, id: UUID):
        obj = await skill_repository.get(db, id)
        if not obj:
            raise AppError("SKILL_NOT_FOUND", "Skill not found", 404)
        return obj

    async def update(self, db, id, data: SkillUpdate):
        obj = await self.get(db, id)
        for k, v in data.model_dump().items():
            setattr(obj, k, v)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db, id):
        obj = await self.get(db, id)
        await db.delete(obj)
        await db.commit()

skill_service = SkillService()
