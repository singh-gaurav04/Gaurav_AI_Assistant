from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.modules.shared.model import Base, UUIDTimestampMixin

class Certification(Base, UUIDTimestampMixin):
    __tablename__ = "certifications"
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    issuer: Mapped[str] = mapped_column(String(160), nullable=False)
    date: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    credential_id: Mapped[str | None] = mapped_column(String(160))
    link: Mapped[str | None] = mapped_column(String(500))
    icon: Mapped[str | None] = mapped_column(String(32))
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
