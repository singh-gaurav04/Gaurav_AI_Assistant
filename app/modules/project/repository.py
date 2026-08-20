from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.project.model import Project

class ProjectRepository:
    async def unique_slug(self, db: AsyncSession, base: str, exclude_id: UUID | None = None) -> str:
        slug, i = base, 2
        while True:
            q = select(Project.id).where(Project.slug == slug)
            if exclude_id:
                q = q.where(Project.id != exclude_id)
            if not await db.scalar(q):
                return slug
            slug = f"{base}-{i}"
            i += 1

    async def list_published(self, db: AsyncSession, *, category=None, technology=None, featured=None, page=1, limit=12):
        q = select(Project).where(Project.is_published.is_(True))
        if category:
            q = q.where(Project.category == category)
        if technology:
            q = q.where(Project.technologies.any(technology))
        if featured is not None:
            q = q.where(Project.featured.is_(featured))
        q = q.order_by(Project.display_order.asc(), Project.created_at.desc()).offset((page - 1) * limit).limit(limit)
        return list((await db.scalars(q)).all())

    async def featured(self, db: AsyncSession):
        q = select(Project).where(Project.is_published.is_(True), Project.featured.is_(True)).order_by(Project.display_order)
        return list((await db.scalars(q)).all())

    async def all_published(self, db: AsyncSession):
        q = select(Project).where(Project.is_published.is_(True)).order_by(Project.display_order.asc(), Project.created_at.desc())
        return list((await db.scalars(q)).all())

    async def real_projects(self, db: AsyncSession):
        q = (
            select(Project)
            .where(Project.is_published.is_(True), Project.is_real_project.is_(True))
            .order_by(Project.display_order.asc(), Project.created_at.desc())
        )
        return list((await db.scalars(q)).all())

    async def all_admin(self, db: AsyncSession):
        q = select(Project).order_by(Project.display_order, Project.created_at.desc())
        return list((await db.scalars(q)).all())

    async def by_slug(self, db: AsyncSession, slug: str):
        return await db.scalar(select(Project).where(Project.slug == slug, Project.is_published.is_(True)))

project_repository = ProjectRepository()
