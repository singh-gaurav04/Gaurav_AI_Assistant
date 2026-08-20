from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.modules.service.schema import ServiceCreate, ServiceUpdate, ServiceOut
from app.modules.service.service import service_service

public_router = APIRouter(tags=["Portfolio"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])


@public_router.get("/services")
async def public_services(db: AsyncSession = Depends(get_db)):
    items = await service_service.list(db, public_only=True)
    return {"success": True, "data": [ServiceOut.model_validate(x) for x in items]}


@public_router.get("/services/{slug}")
async def public_service_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    obj = await service_service.get_by_slug(db, slug)
    return {"success": True, "data": ServiceOut.model_validate(obj)}


@admin_router.post("/services", status_code=201)
async def create_service(payload: ServiceCreate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": ServiceOut.model_validate(await service_service.create(db, payload))}


@admin_router.get("/services")
async def list_services(db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": [ServiceOut.model_validate(x) for x in await service_service.list(db)]}


@admin_router.get("/services/{id}")
async def get_service(id: UUID, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": ServiceOut.model_validate(await service_service.get(db, id))}


@admin_router.put("/services/{id}")
async def update_service(id: UUID, payload: ServiceUpdate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": ServiceOut.model_validate(await service_service.update(db, id, payload))}


@admin_router.delete("/services/{id}", status_code=204)
async def delete_service(id: UUID, db: AsyncSession = Depends(get_db)):
    await service_service.delete(db, id)


@admin_router.post("/services/{id}/featured-image", status_code=200)
async def upload_service_featured_image(
    id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    obj = await service_service.upload_featured_image(db, id, file)
    return {"success": True, "data": ServiceOut.model_validate(obj)}


@admin_router.post("/services/{id}/gallery", status_code=200)
async def upload_service_gallery_image(
    id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    obj = await service_service.add_gallery_image(db, id, file)
    return {"success": True, "data": ServiceOut.model_validate(obj)}


@admin_router.delete("/services/{id}/gallery/{file_id}", status_code=200)
async def delete_service_gallery_image(
    id: UUID,
    file_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await service_service.remove_gallery_image(db, id, file_id)
    return {"success": True, "data": ServiceOut.model_validate(obj)}
