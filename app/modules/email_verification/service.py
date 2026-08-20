import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import create_email_verification_token, decode_email_verification_token
from app.modules.email_template.service import email_service
from app.modules.email_verification.model import EmailOtpChallenge, EmailOtpPurpose, EmailVerification

logger = logging.getLogger(__name__)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _purpose_enum(purpose: str) -> EmailOtpPurpose:
    return EmailOtpPurpose.CONTACT if purpose == "contact" else EmailOtpPurpose.BOOKING


def _hash_otp(email: str, purpose: str, otp: str) -> str:
    raw = f"{email}|{purpose}|{otp}|{settings.JWT_SECRET_KEY}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _generate_otp() -> str:
    length = max(4, min(settings.OTP_LENGTH, 8))
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


class EmailVerificationService:
    async def send_otp(self, db: AsyncSession, email: str, purpose: str) -> None:
        email = _normalize_email(email)
        purpose_enum = _purpose_enum(purpose)
        otp = _generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

        await db.execute(
            delete(EmailOtpChallenge).where(
                EmailOtpChallenge.email == email,
                EmailOtpChallenge.purpose == purpose_enum,
            )
        )

        challenge = EmailOtpChallenge(
            email=email,
            purpose=purpose_enum,
            otp_hash=_hash_otp(email, purpose, otp),
            expires_at=expires_at,
            attempt_count=0,
        )
        db.add(challenge)
        await db.commit()

        sent = await email_service.send_template_safe(
            db,
            email,
            "email_otp",
            {"email": email, "otp": otp, "purpose": purpose},
        )
        if not sent:
            raise AppError(
                "EMAIL_NOT_CONFIGURED",
                "Could not send verification code. Check SMTP settings on the server.",
                503,
            )

    async def verify_otp(self, db: AsyncSession, email: str, purpose: str, otp: str) -> str:
        email = _normalize_email(email)
        purpose_enum = _purpose_enum(purpose)
        now = datetime.now(timezone.utc)

        challenge = await db.scalar(
            select(EmailOtpChallenge)
            .where(EmailOtpChallenge.email == email, EmailOtpChallenge.purpose == purpose_enum)
            .order_by(EmailOtpChallenge.created_at.desc())
        )
        if not challenge:
            raise AppError("OTP_NOT_FOUND", "No verification code found. Request a new code.", 400)

        if challenge.expires_at < now:
            await db.delete(challenge)
            await db.commit()
            raise AppError("OTP_EXPIRED", "Verification code expired. Request a new code.", 400)

        if challenge.attempt_count >= settings.OTP_MAX_ATTEMPTS:
            await db.delete(challenge)
            await db.commit()
            raise AppError("OTP_MAX_ATTEMPTS", "Too many failed attempts. Request a new code.", 400)

        if _hash_otp(email, purpose, otp.strip()) != challenge.otp_hash:
            challenge.attempt_count += 1
            await db.commit()
            remaining = settings.OTP_MAX_ATTEMPTS - challenge.attempt_count
            raise AppError(
                "OTP_INVALID",
                f"Invalid verification code. {remaining} attempt(s) remaining.",
                400,
            )

        await db.delete(challenge)
        db.add(
            EmailVerification(
                email=email,
                purpose=purpose_enum,
                verified_at=now,
            )
        )
        await db.commit()

        logger.info("Email verified in database: %s (%s)", email, purpose)
        return create_email_verification_token(email, purpose)

    async def get_pending_verification(
        self,
        db: AsyncSession,
        email: str,
        purpose: str,
    ) -> EmailVerification | None:
        email = _normalize_email(email)
        purpose_enum = _purpose_enum(purpose)
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=settings.EMAIL_VERIFICATION_TOKEN_MINUTES)

        return await db.scalar(
            select(EmailVerification)
            .where(
                EmailVerification.email == email,
                EmailVerification.purpose == purpose_enum,
                EmailVerification.consumed_at.is_(None),
                EmailVerification.verified_at >= cutoff,
            )
            .order_by(EmailVerification.verified_at.desc())
        )

    async def consume_verification(
        self,
        db: AsyncSession,
        verification: EmailVerification,
        contact_id: uuid.UUID,
    ) -> None:
        verification.consumed_at = datetime.now(timezone.utc)
        verification.contact_id = contact_id
        await db.commit()
        logger.info("Email verification consumed for contact %s", contact_id)

    def assert_verification_token(self, token: str, email: str, purpose: str) -> None:
        email = _normalize_email(email)
        try:
            payload = decode_email_verification_token(token)
        except jwt.PyJWTError:
            raise AppError("EMAIL_NOT_VERIFIED", "Email verification expired or invalid. Verify your email again.", 400)

        if payload.get("email") != email:
            raise AppError("EMAIL_NOT_VERIFIED", "Verification token does not match this email.", 400)
        if payload.get("purpose") != purpose:
            raise AppError("EMAIL_NOT_VERIFIED", "Verification token is not valid for this form.", 400)


email_verification_service = EmailVerificationService()
