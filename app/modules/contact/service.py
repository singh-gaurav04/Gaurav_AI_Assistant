import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.modules.contact.model import Contact, ContactStatus
from app.modules.contact.repository import contact_repository
from app.modules.contact.schema import ContactCreate, ContactReply
from app.modules.email_template.service import email_service
from app.modules.email_verification.service import email_verification_service

logger = logging.getLogger(__name__)

SERVICE_BOOKING_PREFIX = "book:"


def _contact_purpose(subject: str) -> str:
    return "booking" if subject.strip().lower().startswith(SERVICE_BOOKING_PREFIX) else "contact"


def _normalize_submission_email(email: str) -> str:
    return email.strip().lower()


class ContactService:
    async def create(self, db: AsyncSession, payload: ContactCreate) -> Contact:
        purpose = _contact_purpose(payload.subject)
        normalized_email = _normalize_submission_email(payload.email)

        email_verification_service.assert_verification_token(
            payload.verification_token,
            normalized_email,
            purpose,
        )

        pending_verification = await email_verification_service.get_pending_verification(
            db,
            normalized_email,
            purpose,
        )
        if not pending_verification:
            raise AppError(
                "EMAIL_NOT_VERIFIED",
                "Email verification not found in database. Please verify your email again.",
                400,
            )

        data = payload.model_dump(exclude={"website", "verification_token"})
        data["email"] = normalized_email
        obj = Contact(**data)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)

        if not obj.id:
            raise AppError("CONTACT_SAVE_FAILED", "Could not save your message. Please try again.", 500)

        logger.info("Contact saved in database: %s (%s)", obj.id, obj.subject)

        await email_verification_service.consume_verification(db, pending_verification, obj.id)

        await self._send_submission_emails(db, obj)
        return obj

    async def _send_submission_emails(self, db: AsyncSession, obj: Contact) -> None:
        values = {
            "name": obj.name,
            "email": obj.email,
            "subject": obj.subject,
            "message": obj.message,
        }

        if obj.subject.strip().lower().startswith(SERVICE_BOOKING_PREFIX):
            service_name = obj.subject.split(":", 1)[1].strip() if ":" in obj.subject else obj.subject
            booking_values = {**values, "service_name": service_name}
            user_sent = await email_service.send_template_safe(db, obj.email, "service_booking_user", booking_values)
            admin_sent = await email_service.notify_admin_safe(db, "service_booking_admin", booking_values)
            logger.info(
                "Booking confirmation emails for contact %s — user: %s, admin: %s",
                obj.id,
                user_sent,
                admin_sent,
            )
            return

        user_sent = await email_service.send_template_safe(db, obj.email, "contact_user_ack", values)
        admin_sent = await email_service.notify_admin_safe(db, "contact_admin_notify", values)
        logger.info(
            "Contact confirmation emails for contact %s — user: %s, admin: %s",
            obj.id,
            user_sent,
            admin_sent,
        )

    async def list(self, db: AsyncSession):
        return await contact_repository.list(db)

    async def get(self, db: AsyncSession, id: UUID) -> Contact:
        obj = await contact_repository.get(db, id)
        if not obj:
            raise AppError("CONTACT_NOT_FOUND", "Contact not found", 404)
        return obj

    async def mark_read(self, db: AsyncSession, id: UUID) -> Contact:
        obj = await self.get(db, id)
        obj.status = ContactStatus.READ
        obj.read_at = datetime.now(timezone.utc)
        await db.commit()
        return obj

    async def archive(self, db: AsyncSession, id: UUID) -> Contact:
        obj = await self.get(db, id)
        obj.status = ContactStatus.ARCHIVED
        await db.commit()
        return obj

    async def reply(self, db: AsyncSession, id: UUID, payload: ContactReply) -> Contact:
        obj = await self.get(db, id)
        await email_service.send_template(db, obj.email, "contact_reply", {
            "name": obj.name, "email": obj.email, "subject": obj.subject, "message": payload.message,
        })
        obj.status = ContactStatus.REPLIED
        obj.replied_at = datetime.now(timezone.utc)
        await db.commit()
        return obj


contact_service = ContactService()
