from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.skill.model import Skill

class SkillRepository:
    async def list(self, db: AsyncSession, public_only=False):
        q = select(Skill)
        if public_only:
            q = q.where(Skill.is_active.is_(True))
        q = q.order_by(Skill.display_order.asc(), Skill.created_at.desc())
        return list((await db.scalars(q)).all())

    async def get(self, db: AsyncSession, id: UUID):
        return await db.get(Skill, id)

skill_repository = SkillRepository()
