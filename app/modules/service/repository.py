from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.service.model import Service


class ServiceRepository:
    async def list(self, db: AsyncSession, public_only: bool = False):
        q = select(Service)
        if public_only:
            q = q.where(Service.is_published.is_(True))
        q = q.order_by(Service.display_order.asc(), Service.created_at.desc())
        return list((await db.scalars(q)).all())

    async def get(self, db: AsyncSession, id: UUID):
        return await db.get(Service, id)

    async def by_slug(self, db: AsyncSession, slug: str, public_only: bool = True):
        q = select(Service).where(Service.slug == slug)
        if public_only:
            q = q.where(Service.is_published.is_(True))
        return await db.scalar(q)

    async def unique_slug(self, db: AsyncSession, base: str, exclude_id: UUID | None = None) -> str:
        slug = base
        counter = 2
        while True:
            q = select(Service).where(Service.slug == slug)
            if exclude_id:
                q = q.where(Service.id != exclude_id)
            exists = await db.scalar(q)
            if not exists:
                return slug
            slug = f"{base}-{counter}"
            counter += 1


service_repository = ServiceRepository()
