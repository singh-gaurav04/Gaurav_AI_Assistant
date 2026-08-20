from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.modules.shared.model import Base, UUIDTimestampMixin

class Project(Base, UUIDTimestampMixin):
    __tablename__ = "projects"
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    short_description: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    github_url: Mapped[str | None] = mapped_column(String(500))
    live_url: Mapped[str | None] = mapped_column(String(500))
    featured_image_url: Mapped[str | None] = mapped_column(String(1000))
    imagekit_file_id: Mapped[str | None] = mapped_column(String(255))
    gallery_images: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    technologies: Mapped[list[str]] = mapped_column(ARRAY(String(80)), default=list, nullable=False)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    is_real_project: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
