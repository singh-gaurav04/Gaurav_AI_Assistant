from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.visit.schema import VisitCreate
from app.modules.visit.service import visit_service

public_router = APIRouter(tags=["Portfolio"])

@public_router.post("/visits", status_code=201)
async def track_visit(payload: VisitCreate, db: AsyncSession = Depends(get_db)):
    await visit_service.create(db, payload)
    return {"success": True, "data": None}
