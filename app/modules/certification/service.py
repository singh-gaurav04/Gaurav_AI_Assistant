from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AppError
from app.modules.certification.model import Certification
from app.modules.certification.schema import CertificationCreate, CertificationUpdate
from app.modules.certification.repository import certification_repository

class CertificationService:
    async def create(self, db: AsyncSession, data: CertificationCreate) -> Certification:
        obj = Certification(**data.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def list(self, db: AsyncSession, public_only: bool = False) -> list[Certification]:
        return await certification_repository.list(db, public_only)

    async def get(self, db: AsyncSession, id: UUID) -> Certification:
        obj = await certification_repository.get(db, id)
        if not obj:
            raise AppError("CERTIFICATION_NOT_FOUND", "Certification not found", 404)
        return obj

    async def update(self, db: AsyncSession, id: UUID, data: CertificationUpdate) -> Certification:
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

certification_service = CertificationService()
