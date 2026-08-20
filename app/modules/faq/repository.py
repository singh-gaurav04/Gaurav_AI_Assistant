from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.faq.model import Faq


class FaqRepository:
    async def list(self, db: AsyncSession, public_only=False):
        q = select(Faq)
        if public_only:
            q = q.where(Faq.is_active.is_(True))
        q = q.order_by(Faq.display_order.asc(), Faq.created_at.desc())
        return list((await db.scalars(q)).all())

    async def get(self, db: AsyncSession, id: UUID):
        return await db.get(Faq, id)


faq_repository = FaqRepository()
