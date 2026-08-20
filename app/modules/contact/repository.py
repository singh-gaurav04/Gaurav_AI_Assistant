from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.contact.model import Contact

class ContactRepository:
    async def list(self, db: AsyncSession):
        q = select(Contact).order_by(Contact.created_at.desc())
        return list((await db.scalars(q)).all())

    async def get(self, db: AsyncSession, id: UUID):
        return await db.get(Contact, id)

contact_repository = ContactRepository()
