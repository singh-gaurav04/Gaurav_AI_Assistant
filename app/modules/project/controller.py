from uuid import UUID
from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.core.exceptions import AppError
from app.modules.project.schema import ProjectCreate, ProjectUpdate, ProjectOut
from app.modules.project.service import project_service
from app.modules.project.repository import project_repository

public_router = APIRouter(tags=["Portfolio"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

@public_router.get("/projects")
async def projects(
    page: int = Query(1, ge=1), limit: int = Query(12, ge=1, le=100),
    category: str | None = None, technology: str | None = None, featured: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    items = await project_repository.list_published(db, category=category, technology=technology, featured=featured, page=page, limit=limit)
    return {"success": True, "data": [ProjectOut.model_validate(x) for x in items]}

@public_router.get("/projects/featured")
async def featured_projects(db: AsyncSession = Depends(get_db)):
    items = await project_repository.featured(db)
    return {"success": True, "data": [ProjectOut.model_validate(x) for x in items]}

@public_router.get("/projects/{slug}")
async def project_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    obj = await project_repository.by_slug(db, slug)
    if not obj:
        raise AppError("PROJECT_NOT_FOUND", "Project not found", 404)
    return {"success": True, "data": ProjectOut.model_validate(obj)}

@public_router.get("/my_real_projects")
async def my_real_projects(db: AsyncSession = Depends(get_db)):
    items = await project_repository.real_projects(db)
    return {"success": True, "data": [ProjectOut.model_validate(x) for x in items]}

@admin_router.post("/projects", status_code=201)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": ProjectOut.model_validate(await project_service.create(db, payload))}

@admin_router.get("/projects")
async def admin_projects(db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": [ProjectOut.model_validate(x) for x in await project_repository.all_admin(db)]}

@admin_router.get("/projects/{id}")
async def admin_project(id: UUID, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": ProjectOut.model_validate(await project_service.get(db, id))}

@admin_router.put("/projects/{id}")
async def admin_update_project(id: UUID, payload: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": ProjectOut.model_validate(await project_service.update(db, id, payload))}

@admin_router.delete("/projects/{id}", status_code=204)
async def admin_delete_project(id: UUID, db: AsyncSession = Depends(get_db)):
    await project_service.delete(db, id)

@admin_router.patch("/projects/{id}/publish")
async def toggle_publish(id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await project_service.get(db, id)
    obj.is_published = not obj.is_published
    await db.commit()
    return {"success": True, "data": {"is_published": obj.is_published}}

@admin_router.patch("/projects/{id}/feature")
async def toggle_feature(id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await project_service.get(db, id)
    obj.featured = not obj.featured
    await db.commit()
    return {"success": True, "data": {"featured": obj.featured}}

@admin_router.post("/projects/{id}/featured-image", status_code=200)
async def upload_project_featured_image(
    id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    obj = await project_service.upload_featured_image(db, id, file)
    return {"success": True, "data": ProjectOut.model_validate(obj)}


@admin_router.post("/projects/{id}/gallery", status_code=200)
async def upload_project_gallery_image(
    id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    obj = await project_service.add_gallery_image(db, id, file)
    return {"success": True, "data": ProjectOut.model_validate(obj)}


@admin_router.delete("/projects/{id}/gallery/{file_id}", status_code=200)
async def delete_project_gallery_image(
    id: UUID,
    file_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await project_service.remove_gallery_image(db, id, file_id)
    return {"success": True, "data": ProjectOut.model_validate(obj)}
