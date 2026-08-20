from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.visit.model import Visit
from app.modules.visit.schema import VisitCreate

class VisitService:
    async def create(self, db: AsyncSession, payload: VisitCreate):
        db.add(Visit(**payload.model_dump()))
        await db.commit()

visit_service = VisitService()
