from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.testimonial.model import Testimonial, TestimonialStatus

class TestimonialRepository:
    async def list_public(self, db: AsyncSession, featured: bool | None = None):
        q = select(Testimonial).where(Testimonial.status == TestimonialStatus.APPROVED)
        if featured is not None:
            q = q.where(Testimonial.is_featured.is_(featured))
        q = q.order_by(Testimonial.display_order)
        return list((await db.scalars(q)).all())

    async def list_admin(self, db: AsyncSession):
        q = select(Testimonial).order_by(Testimonial.created_at.desc())
        return list((await db.scalars(q)).all())

    async def get(self, db: AsyncSession, id: UUID):
        return await db.get(Testimonial, id)

testimonial_repository = TestimonialRepository()
