from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.modules.shared.model import Base, UUIDTimestampMixin


class Service(Base, UUIDTimestampMixin):
    __tablename__ = "services"

    title: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    short_description: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    features: Mapped[list[str]] = mapped_column(ARRAY(String(500)), default=list, nullable=False)
    duration: Mapped[list[str]] = mapped_column(ARRAY(String(500)), default=list, nullable=False)
    how_it_works: Mapped[list[str]] = mapped_column(ARRAY(String(500)), default=list, nullable=False)
    deliverables: Mapped[list[str]] = mapped_column(ARRAY(String(500)), default=list, nullable=False)
    tag: Mapped[str | None] = mapped_column(String(80))
    recommended: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    featured_image_url: Mapped[str | None] = mapped_column(String(1000))
    imagekit_file_id: Mapped[str | None] = mapped_column(String(255))
    gallery_images: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(80))
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
