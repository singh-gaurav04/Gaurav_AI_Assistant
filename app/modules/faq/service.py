from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.modules.faq.model import Faq
from app.modules.faq.repository import faq_repository
from app.modules.faq.schema import FaqCreate, FaqUpdate


class FaqService:
    async def create(self, db: AsyncSession, data: FaqCreate):
        obj = Faq(**data.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def list(self, db: AsyncSession, public_only=False):
        return await faq_repository.list(db, public_only)

    async def get(self, db: AsyncSession, id: UUID):
        obj = await faq_repository.get(db, id)
        if not obj:
            raise AppError("FAQ_NOT_FOUND", "FAQ not found", 404)
        return obj

    async def update(self, db, id, data: FaqUpdate):
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


faq_service = FaqService()
