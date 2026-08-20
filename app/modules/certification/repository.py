from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.certification.model import Certification

class CertificationRepository:
    async def list(self, db: AsyncSession, public_only: bool = False):
        q = select(Certification)
        if public_only:
            q = q.where(Certification.is_published.is_(True))
        q = q.order_by(Certification.display_order.asc(), Certification.created_at.desc())
        return list((await db.scalars(q)).all())

    async def get(self, db: AsyncSession, id: UUID):
        return await db.get(Certification, id)

certification_repository = CertificationRepository()
