from datetime import datetime, timezone
from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from app.core.exceptions import AppError
from app.modules.media.image_service import compress_image
from app.modules.media.imagekit_service import imagekit_service
from app.modules.testimonial.model import Testimonial, TestimonialStatus
from app.modules.testimonial.schema import TestimonialCreate, TestimonialUpdate
from app.modules.testimonial.repository import testimonial_repository

logger = logging.getLogger(__name__)

class TestimonialService:
    async def submit_feedback(
        self,
        db: AsyncSession,
        *,
        name: str,
        message: str,
        email: str | None = None,
        linkedin_url: str | None = None,
        avatar: UploadFile | None = None,
    ) -> Testimonial:
        name = name.strip()
        message = message.strip()
        if len(name) < 1:
            raise AppError("INVALID_NAME", "Name is required", 400)
        if len(message) < 5:
            raise AppError("INVALID_MESSAGE", "Message must be at least 5 characters", 400)

        avatar_url = None
        imagekit_file_id = None
        if avatar and avatar.filename:
            data, _, _, _ = await compress_image(avatar)
            result = await imagekit_service.upload(data, f"{name.replace(' ', '-').lower()}-avatar.webp", "/portfolio/feedback/")
            avatar_url = result["url"]
            imagekit_file_id = result["fileId"]

        obj = Testimonial(
            name=name,
            message=message,
            linkedin_url=linkedin_url.strip() if linkedin_url else None,
            avatar_url=avatar_url,
            imagekit_file_id=imagekit_file_id,
            status=TestimonialStatus.PENDING,
        )
        db.add(obj)
        await db.commit()
        await db.refresh(obj)

        if not obj.id:
            raise AppError("FEEDBACK_SAVE_FAILED", "Could not save your feedback. Please try again.", 500)

        logger.info("Feedback saved in database: %s", obj.id)
        await self._send_feedback_emails(db, name=name, message=message, email=email, linkedin_url=linkedin_url)
        return obj

    async def _send_feedback_emails(
        self,
        db: AsyncSession,
        *,
        name: str,
        message: str,
        email: str | None,
        linkedin_url: str | None,
    ) -> None:
        from app.modules.email_template.service import email_service

        notify_values = {
            "name": name,
            "email": email or "Not provided",
            "linkedin_url": linkedin_url or "Not provided",
            "message": message,
        }
        admin_sent = await email_service.notify_admin_safe(db, "feedback_admin_notify", notify_values)
        user_sent = False
        if email:
            user_sent = await email_service.send_template_safe(
                db,
                email,
                "feedback_user_ack",
                {"name": name, "message": message},
            )
        logger.info("Feedback confirmation emails — user: %s, admin: %s", user_sent, admin_sent)

    async def create(self, db: AsyncSession, payload: TestimonialCreate):
        d = payload.model_dump()
        d["linkedin_url"] = d["linkedin_url"] if d["linkedin_url"] else None
        obj = Testimonial(**d, status=TestimonialStatus.PENDING)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def get(self, db: AsyncSession, id: UUID) -> Testimonial:
        obj = await testimonial_repository.get(db, id)
        if not obj:
            raise AppError("TESTIMONIAL_NOT_FOUND", "Testimonial not found", 404)
        return obj

    async def update(self, db: AsyncSession, id: UUID, payload: TestimonialUpdate):
        obj = await self.get(db, id)
        data = payload.model_dump(exclude_unset=True)
        if "linkedin_url" in data:
            data["linkedin_url"] = str(data["linkedin_url"]) if data["linkedin_url"] else None
        for k, v in data.items():
            setattr(obj, k, v)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, id: UUID):
        obj = await self.get(db, id)
        await db.delete(obj)
        await db.commit()

    async def approve(self, db: AsyncSession, id: UUID):
        obj = await self.get(db, id)
        obj.status = TestimonialStatus.APPROVED
        obj.approved_at = datetime.now(timezone.utc)
        obj.rejected_at = None
        await db.commit()
        return obj

    async def reject(self, db: AsyncSession, id: UUID):
        obj = await self.get(db, id)
        obj.status = TestimonialStatus.REJECTED
        obj.rejected_at = datetime.now(timezone.utc)
        obj.approved_at = None
        obj.is_featured = False
        await db.commit()
        return obj

    async def toggle_feature(self, db: AsyncSession, id: UUID):
        obj = await self.get(db, id)
        if obj.status != TestimonialStatus.APPROVED:
            raise AppError("TESTIMONIAL_NOT_APPROVED", "Only approved testimonials can be featured", 409)
        obj.is_featured = not obj.is_featured
        await db.commit()
        return obj

testimonial_service = TestimonialService()
