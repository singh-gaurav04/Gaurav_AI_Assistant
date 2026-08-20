from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.modules.shared.model import Base, UUIDTimestampMixin

class Profile(Base, UUIDTimestampMixin):
    __tablename__ = "profiles"
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    handle: Mapped[str | None] = mapped_column(String(80))
    bio: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(40))
    graduation_year: Mapped[str | None] = mapped_column(String(20))
    profile_image_url: Mapped[str | None] = mapped_column(String(1000))
    resume_url: Mapped[str | None] = mapped_column(String(1000))
    is_placed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    placement_status: Mapped[str | None] = mapped_column(String(200))
    placement_company: Mapped[str | None] = mapped_column(String(160))
    placement_role: Mapped[str | None] = mapped_column(String(160))
    github_url: Mapped[str | None] = mapped_column(String(500))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    leetcode_url: Mapped[str | None] = mapped_column(String(500))
    response_time: Mapped[str | None] = mapped_column(String(200))
