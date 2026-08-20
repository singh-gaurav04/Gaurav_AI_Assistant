from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.modules.shared.model import Base, UUIDTimestampMixin

class Visit(Base, UUIDTimestampMixin):
    __tablename__ = "visits"
    page: Mapped[str] = mapped_column(String(1000), nullable=False)
    user_agent: Mapped[str | None] = mapped_column(Text)
    referrer: Mapped[str | None] = mapped_column(String(1000))
