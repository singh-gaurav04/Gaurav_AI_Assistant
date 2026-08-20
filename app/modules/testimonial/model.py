import enum
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.modules.shared.model import Base, UUIDTimestampMixin

class TestimonialStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Testimonial(Base, UUIDTimestampMixin):
    __tablename__ = "testimonials"
    __table_args__ = (CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 5)", name="ck_testimonial_rating"),)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str | None] = mapped_column(String(150))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(1000))
    imagekit_file_id: Mapped[str | None] = mapped_column(String(255))
    rating: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[TestimonialStatus] = mapped_column(Enum(TestimonialStatus), default=TestimonialStatus.PENDING, index=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
