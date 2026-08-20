from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.modules.shared.model import Base, UUIDTimestampMixin

class Experience(Base, UUIDTimestampMixin):
    __tablename__ = "experiences"
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    company: Mapped[str] = mapped_column(String(180), nullable=False)
    location: Mapped[str | None] = mapped_column(String(160))
    period: Mapped[str] = mapped_column(String(80), nullable=False)
    type: Mapped[str] = mapped_column(String(80), default="Experience", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    achievements: Mapped[list[str]] = mapped_column(ARRAY(String(500)), default=list, nullable=False)
    technologies: Mapped[list[str]] = mapped_column(ARRAY(String(80)), default=list, nullable=False)
    link: Mapped[str | None] = mapped_column(String(500))
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
