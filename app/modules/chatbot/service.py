from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppError
from app.modules.chatbot.embeddings import embedding_provider_label, mistral_configured
from app.modules.chatbot.vectorstore import delete_document_vectors, pinecone_configured, pinecone_ready, upsert_chunks
from app.modules.chatbot.langchain_rag import (
    generate_with_langchain,
    retrieve_with_langchain,
    sources_from_docs,
)
from app.modules.chatbot.model import ChatChunk, ChatDocument, ChatbotSettings
from app.modules.chatbot.pdf_processor import chunk_documents, extract_pdf_documents
from app.modules.chatbot.repository import chatbot_repository
from app.modules.chatbot.providers import list_provider_options, validate_provider_model
from app.modules.chatbot.schema import (
    ChatRequest,
    ChatResponseData,
    ChatSource,
    ChatbotConfigOut,
    ChatbotConfigUpdate,
    ChatDocumentOut,
    LlmProviderOption,
    QuickActionOut,
)
from app.modules.experience.service import experience_service
from app.modules.profile.service import profile_service
from app.modules.project.repository import project_repository
from app.modules.skill.service import skill_service

logger = logging.getLogger(__name__)


class ChatbotService:
    def __init__(self) -> None:
        self.storage_dir = Path(settings.CHATBOT_STORAGE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _document_out(self, document: ChatDocument) -> ChatDocumentOut:
        return ChatDocumentOut(
            id=document.id,
            original_filename=document.original_filename,
            file_size=document.file_size,
            page_count=document.page_count,
            status=document.status,
            error_message=document.error_message,
            chunk_count=document.chunk_count,
            created_at=document.created_at.isoformat(),
        )

    def _config_out(self, config: ChatbotSettings, *, include_providers: bool = False) -> ChatbotConfigOut:
        actions = config.quick_actions or []
        providers = []
        if include_providers:
            providers = [LlmProviderOption.model_validate(item) for item in list_provider_options()]
        return ChatbotConfigOut(
            bot_name=config.bot_name,
            bot_subtitle=config.bot_subtitle,
            avatar_url=config.avatar_url,
            welcome_message=config.welcome_message,
            privacy_policy_url=config.privacy_policy_url,
            privacy_policy_label=config.privacy_policy_label,
            quick_actions=[QuickActionOut.model_validate(item) for item in actions],
            llm_provider=getattr(config, "llm_provider", None) or "openai",
            llm_model=getattr(config, "llm_model", None) or "gpt-4o-mini",
            llm_temperature=float(getattr(config, "llm_temperature", None) or 0.2),
            llm_providers=providers,
            embedding_provider=embedding_provider_label(),
            mistral_embed_configured=mistral_configured(),
            pinecone_configured=pinecone_ready(),
            chunk_size=int(
                settings.CHATBOT_CHUNK_SIZE
                if getattr(config, "chunk_size", None) is None
                else config.chunk_size
            ),
            chunk_overlap=int(
                settings.CHATBOT_CHUNK_OVERLAP
                if getattr(config, "chunk_overlap", None) is None
                else config.chunk_overlap
            ),
        )

    async def get_config(self, db: AsyncSession, *, include_providers: bool = False) -> ChatbotConfigOut:
        config = await chatbot_repository.get_settings(db)
        await db.commit()
        return self._config_out(config, include_providers=include_providers)

    async def update_config(self, db: AsyncSession, payload: ChatbotConfigUpdate) -> ChatbotConfigOut:
        provider, model = validate_provider_model(payload.llm_provider, payload.llm_model)
        config = await chatbot_repository.get_settings(db)
        config.bot_name = payload.bot_name
        config.bot_subtitle = payload.bot_subtitle
        config.avatar_url = payload.avatar_url
        config.welcome_message = payload.welcome_message
        config.privacy_policy_url = payload.privacy_policy_url
        config.privacy_policy_label = payload.privacy_policy_label
        config.quick_actions = [item.model_dump() for item in payload.quick_actions]
        config.llm_provider = provider
        config.llm_model = model
        config.llm_temperature = payload.llm_temperature
        config.chunk_size = payload.chunk_size
        config.chunk_overlap = payload.chunk_overlap
        await chatbot_repository.save_settings(db, config)
        await db.commit()
        await db.refresh(config)
        return self._config_out(config, include_providers=True)

    async def list_documents(self, db: AsyncSession) -> list[ChatDocumentOut]:
        documents = await chatbot_repository.list_documents(db)
        return [self._document_out(doc) for doc in documents]

    async def ingest_pdf(self, db: AsyncSession, upload: UploadFile) -> ChatDocumentOut:
        filename = upload.filename or "document.pdf"
        if not filename.lower().endswith(".pdf"):
            raise AppError("INVALID_FILE", "Only PDF files are supported", 400)

        data = await upload.read()
        if not data:
            raise AppError("EMPTY_FILE", "Uploaded file is empty", 400)

        max_bytes = settings.CHATBOT_MAX_FILE_MB * 1024 * 1024
        if len(data) > max_bytes:
            raise AppError("FILE_TOO_LARGE", f"PDF must be under {settings.CHATBOT_MAX_FILE_MB}MB", 400)

        stored_name = f"{uuid.uuid4().hex}.pdf"
        file_path = self.storage_dir / stored_name
        file_path.write_bytes(data)

        document = ChatDocument(
            original_filename=filename,
            stored_filename=stored_name,
            file_path=str(file_path),
            file_size=len(data),
            status="processing",
        )
        document = await chatbot_repository.create_document(db, document)
        await db.commit()
        await db.refresh(document)

        try:
            page_docs, page_count = extract_pdf_documents(data, source=filename)
            if not page_docs:
                raise AppError("EMPTY_PDF", "No extractable text found in PDF", 400)

            config = await chatbot_repository.get_settings(db)
            chunk_size = (
                settings.CHATBOT_CHUNK_SIZE
                if getattr(config, "chunk_size", None) is None
                else int(config.chunk_size)
            )
            chunk_overlap = (
                settings.CHATBOT_CHUNK_OVERLAP
                if getattr(config, "chunk_overlap", None) is None
                else int(config.chunk_overlap)
            )
            if chunk_overlap >= chunk_size:
                chunk_overlap = max(0, chunk_size // 5)

            split_docs = chunk_documents(
                page_docs,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            pieces = [doc.page_content for doc in split_docs if doc.page_content.strip()]
            if not pieces:
                raise AppError("EMPTY_PDF", "No usable text chunks found in PDF", 400)

            chunks = [
                ChatChunk(
                    document_id=document.id,
                    content=piece,
                    embedding=None,
                    chunk_index=index,
                    char_count=len(piece),
                )
                for index, piece in enumerate(pieces)
            ]

            await chatbot_repository.delete_chunks_for_document(db, document.id)
            await chatbot_repository.add_chunks(db, chunks)
            await db.flush()

            await upsert_chunks(chunks, filename=filename, document_id=document.id)

            document.page_count = page_count
            document.chunk_count = len(chunks)
            document.status = "ready"
            document.error_message = None
            await db.commit()
            await db.refresh(document)
            logger.info(
                "Ingested PDF %s (%s chunks, size=%s, overlap=%s, embed=%s, store=pinecone)",
                document.id,
                document.chunk_count,
                chunk_size,
                chunk_overlap,
                embedding_provider_label(),
            )
            return self._document_out(document)
        except AppError as exc:
            document.status = "failed"
            document.error_message = exc.message
            await db.commit()
            raise
        except Exception as exc:
            document.status = "failed"
            document.error_message = str(exc)[:500]
            await db.commit()
            logger.exception("PDF ingest failed for %s", document.id)
            raise AppError("INGEST_FAILED", "Failed to process PDF", 500) from exc

    async def delete_document(self, db: AsyncSession, document_id: uuid.UUID) -> None:
        document = await chatbot_repository.get_document(db, document_id)
        if not document:
            raise AppError("DOCUMENT_NOT_FOUND", "Document not found", 404)

        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink(missing_ok=True)

        await delete_document_vectors(document_id)
        await chatbot_repository.delete_document(db, document)
        await db.commit()

    async def _portfolio_context(self, db: AsyncSession) -> str:
        profile = await profile_service.get_or_none(db)
        real_projects = await project_repository.real_projects(db)
        skills = await skill_service.list(db, True)
        experiences = await experience_service.list(db, True)

        lines: list[str] = []
        if profile:
            lines.append(
                f"Owner: {profile.name} — {profile.title}. Bio: {profile.bio[:600]}. "
                f"Email: {profile.email}. Location: {profile.location or 'N/A'}."
            )
        if real_projects:
            titles = ", ".join(p.title for p in real_projects[:8])
            lines.append(f"Real-world projects: {titles}.")
        if skills:
            skill_names = ", ".join(s.name for s in skills[:20])
            lines.append(f"Key skills: {skill_names}.")
        if experiences:
            exp = "; ".join(f"{e.title} at {e.company}" for e in experiences[:5])
            lines.append(f"Experience: {exp}.")
        return "\n".join(lines) if lines else "Portfolio profile is being updated."

    async def chat(self, db: AsyncSession, payload: ChatRequest) -> ChatResponseData:
        message = payload.message.strip()
        if not message:
            raise AppError("EMPTY_MESSAGE", "Message cannot be empty", 400)

        config = await chatbot_repository.get_settings(db)
        portfolio_context = await self._portfolio_context(db)
        chunks = await chatbot_repository.list_chunks_with_documents(db)

        retrieved = await retrieve_with_langchain(chunks, message)
        context_docs = [doc for _chunk, _score, doc in retrieved]
        source_payloads = sources_from_docs(context_docs)

        conversation = [{"role": turn.role, "content": turn.content} for turn in payload.conversation]

        try:
            response = await generate_with_langchain(
                query=message,
                conversation=conversation,
                context_docs=context_docs,
                portfolio_context=portfolio_context,
                bot_name=config.bot_name,
                bot_subtitle=config.bot_subtitle,
                llm_provider=getattr(config, "llm_provider", None),
                llm_model=getattr(config, "llm_model", None),
                llm_temperature=getattr(config, "llm_temperature", None),
            )
        except AppError:
            raise
        except Exception as exc:
            logger.exception("Unexpected chatbot error")
            raise AppError("CHAT_FAILED", "Chatbot failed to answer. Please try again.", 500) from exc

        sources = [ChatSource.model_validate(item) for item in source_payloads]
        logger.info(
            "Chat answered (chunks=%s, sources=%s, llm=%s/%s, embed=%s)",
            len(context_docs),
            len(sources),
            getattr(config, "llm_provider", "openai"),
            getattr(config, "llm_model", "gpt-4o-mini"),
            embedding_provider_label(),
        )
        return ChatResponseData(response=response, sources=sources)


chatbot_service = ChatbotService()
