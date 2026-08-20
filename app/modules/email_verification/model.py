import enum
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from app.modules.shared.model import Base, UUIDTimestampMixin


class EmailOtpPurpose(str, enum.Enum):
    CONTACT = "contact"
    BOOKING = "booking"


email_otp_purpose_enum = Enum(
    EmailOtpPurpose,
    name="emailotppurpose",
    values_callable=lambda choices: [choice.value for choice in choices],
    native_enum=True,
)


class EmailOtpChallenge(Base, UUIDTimestampMixin):
    __tablename__ = "email_otp_challenges"

    email: Mapped[str] = mapped_column(String(320), index=True, nullable=False)
    purpose: Mapped[EmailOtpPurpose] = mapped_column(email_otp_purpose_enum, index=True, nullable=False)
    otp_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class EmailVerification(Base, UUIDTimestampMixin):
    """OTP confirmed in DB — must exist before contact/booking confirmation emails send."""

    __tablename__ = "email_verifications"

    email: Mapped[str] = mapped_column(String(320), index=True, nullable=False)
    purpose: Mapped[EmailOtpPurpose] = mapped_column(email_otp_purpose_enum, index=True, nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    contact_id: Mapped[uuid.UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
