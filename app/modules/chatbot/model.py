import uuid
from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.modules.shared.model import Base, UUIDTimestampMixin


class ChatDocument(UUIDTimestampMixin, Base):
    __tablename__ = "chat_documents"

    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="processing")
    error_message: Mapped[str | None] = mapped_column(Text)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    chunks: Mapped[list["ChatChunk"]] = relationship(
        "ChatChunk", back_populates="document", cascade="all, delete-orphan"
    )


class ChatChunk(UUIDTimestampMixin, Base):
    __tablename__ = "chat_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list | None] = mapped_column(JSONB)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    document: Mapped["ChatDocument"] = relationship("ChatDocument", back_populates="chunks")


class ChatbotSettings(Base):
    __tablename__ = "chatbot_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    bot_name: Mapped[str] = mapped_column(String(120), nullable=False, default="Gaurav's Assistant")
    bot_subtitle: Mapped[str] = mapped_column(String(200), nullable=False, default="Personal AI Assistant")
    avatar_url: Mapped[str | None] = mapped_column(String(1000))
    welcome_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=(
            "Hello! I'm Gaurav's personal assistant. I can help you explore his real-world projects, "
            "technical skills, experience, and the best way to collaborate. How can I assist you today?"
        ),
    )
    privacy_policy_url: Mapped[str] = mapped_column(String(500), nullable=False, default="#")
    privacy_policy_label: Mapped[str] = mapped_column(String(200), nullable=False, default="Privacy Policy")
    quick_actions: Mapped[list | None] = mapped_column(JSONB)
    llm_provider: Mapped[str] = mapped_column(String(40), nullable=False, default="openai")
    llm_model: Mapped[str] = mapped_column(String(120), nullable=False, default="gpt-4o-mini")
    llm_temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0.2)
    chunk_size: Mapped[int] = mapped_column(Integer, nullable=False, default=800)
    chunk_overlap: Mapped[int] = mapped_column(Integer, nullable=False, default=120)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
