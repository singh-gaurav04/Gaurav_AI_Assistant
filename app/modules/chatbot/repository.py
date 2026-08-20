from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.chatbot.model import ChatChunk, ChatDocument, ChatbotSettings


class ChatbotRepository:
    async def list_documents(self, db: AsyncSession) -> list[ChatDocument]:
        result = await db.execute(select(ChatDocument).order_by(ChatDocument.created_at.desc()))
        return list(result.scalars().all())

    async def get_document(self, db: AsyncSession, document_id: UUID) -> ChatDocument | None:
        return await db.get(ChatDocument, document_id)

    async def create_document(self, db: AsyncSession, document: ChatDocument) -> ChatDocument:
        db.add(document)
        await db.flush()
        return document

    async def delete_document(self, db: AsyncSession, document: ChatDocument) -> None:
        await db.delete(document)

    async def add_chunks(self, db: AsyncSession, chunks: list[ChatChunk]) -> None:
        db.add_all(chunks)

    async def delete_chunks_for_document(self, db: AsyncSession, document_id: UUID) -> None:
        await db.execute(delete(ChatChunk).where(ChatChunk.document_id == document_id))

    async def list_chunks_with_documents(self, db: AsyncSession) -> list[ChatChunk]:
        result = await db.execute(
            select(ChatChunk).options(selectinload(ChatChunk.document)).order_by(ChatChunk.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_settings(self, db: AsyncSession) -> ChatbotSettings:
        settings = await db.get(ChatbotSettings, 1)
        if settings:
            return settings

        settings = ChatbotSettings(
            id=1,
            quick_actions=[],
            llm_provider="openai",
            llm_model="gpt-4o-mini",
            llm_temperature=0.2,
        )
        db.add(settings)
        await db.flush()
        return settings

    async def save_settings(self, db: AsyncSession, settings: ChatbotSettings) -> ChatbotSettings:
        db.add(settings)
        await db.flush()
        return settings


chatbot_repository = ChatbotRepository()
