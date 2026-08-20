from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.modules.testimonial.schema import TestimonialCreate, TestimonialUpdate, TestimonialOut
from app.modules.testimonial.service import testimonial_service
from app.modules.testimonial.repository import testimonial_repository

public_router = APIRouter(tags=["Portfolio"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

@public_router.get("/testimonials")
async def testimonials(featured: bool | None = None, db: AsyncSession = Depends(get_db)):
    items = await testimonial_repository.list_public(db, featured)
    return {"success": True, "data": [TestimonialOut.model_validate(x) for x in items]}


@public_router.post("/feedback", status_code=201)
async def submit_feedback(
    name: str = Form(...),
    message: str = Form(...),
    email: str | None = Form(None),
    linkedin_url: str | None = Form(None),
    avatar: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
):
    obj = await testimonial_service.submit_feedback(
        db,
        name=name,
        message=message,
        email=email.strip() if email else None,
        linkedin_url=linkedin_url,
        avatar=avatar,
    )
    return {
        "success": True,
        "data": {"id": str(obj.id), "status": obj.status.value},
        "message": "Thank you for your feedback. It will appear after review.",
    }


@admin_router.post("/testimonials", status_code=201)
async def create_testimonial(payload: TestimonialCreate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": TestimonialOut.model_validate(await testimonial_service.create(db, payload))}

@admin_router.get("/testimonials")
async def list_testimonials(db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": [TestimonialOut.model_validate(x) for x in await testimonial_repository.list_admin(db)]}

@admin_router.patch("/testimonials/{id}/approve")
async def approve_testimonial(id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await testimonial_service.approve(db, id)
    return {"success": True, "data": {"status": obj.status}}

@admin_router.patch("/testimonials/{id}/reject")
async def reject_testimonial(id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await testimonial_service.reject(db, id)
    return {"success": True, "data": {"status": obj.status}}

@admin_router.patch("/testimonials/{id}/feature")
async def feature_testimonial(id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await testimonial_service.toggle_feature(db, id)
    return {"success": True, "data": {"is_featured": obj.is_featured}}

@admin_router.put("/testimonials/{id}")
async def update_testimonial(id: UUID, payload: TestimonialUpdate, db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": TestimonialOut.model_validate(await testimonial_service.update(db, id, payload))}

@admin_router.delete("/testimonials/{id}", status_code=204)
async def delete_testimonial(id: UUID, db: AsyncSession = Depends(get_db)):
    await testimonial_service.delete(db, id)
