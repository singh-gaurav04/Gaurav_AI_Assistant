"""Pinecone vector store for chatbot RAG (Mistral embeddings)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from langchain_core.documents import Document

from app.core.config import settings
from app.core.exceptions import AppError
from app.modules.chatbot.embeddings import embed_texts, mistral_configured
from app.modules.chatbot.model import ChatChunk

logger = logging.getLogger(__name__)

_index = None
_index_handle_name: str | None = None
_resolved_index_name: str | None = None


def pinecone_configured() -> bool:
    return bool(
        settings.PINECONE_API_KEY
        and settings.PINECONE_API_KEY.strip()
        and settings.PINECONE_INDEX_NAME
        and settings.PINECONE_INDEX_NAME.strip()
    )


def _pinecone_client():
    if not pinecone_configured():
        raise AppError(
            "PINECONE_NOT_CONFIGURED",
            "Pinecone is not configured. Set PINECONE_API_KEY and PINECONE_INDEX_NAME in .env",
            503,
        )
    from pinecone import Pinecone

    return Pinecone(api_key=settings.PINECONE_API_KEY)


def _list_index_summaries(pc) -> list[Any]:
    return list(pc.list_indexes())


def _find_compatible_index(pc) -> str | None:
    target_dim = settings.MISTRAL_EMBEDDING_DIMENSION
    for idx in _list_index_summaries(pc):
        dimension = getattr(idx, "dimension", None)
        if dimension == target_dim:
            return str(idx.name)
    return None


def pinecone_ready() -> bool:
    """True when Pinecone is configured and a usable index is resolved."""
    if not pinecone_configured():
        return False
    if _resolved_index_name:
        return True
    try:
        ensure_pinecone_index()
    except Exception:
        logger.exception("Pinecone index resolution failed")
        return False
    return bool(_resolved_index_name)


def ensure_pinecone_index() -> None:
    """Resolve a Pinecone index without blocking app startup."""
    global _resolved_index_name

    if not pinecone_configured():
        return

    if _resolved_index_name:
        return

    pc = _pinecone_client()
    configured_name = settings.PINECONE_INDEX_NAME.strip()
    existing = {str(idx.name) for idx in _list_index_summaries(pc)}

    if configured_name in existing:
        _resolved_index_name = configured_name
        return

    try:
        from pinecone import ServerlessSpec

        pc.create_index(
            name=configured_name,
            dimension=settings.MISTRAL_EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=settings.PINECONE_CLOUD,
                region=settings.PINECONE_REGION,
            ),
        )
        _resolved_index_name = configured_name
        logger.info(
            "Created Pinecone index %s (dim=%s)",
            configured_name,
            settings.MISTRAL_EMBEDDING_DIMENSION,
        )
        return
    except Exception as exc:
        logger.warning(
            "Could not create Pinecone index %s (%s). Will try an existing index.",
            configured_name,
            exc,
        )

    fallback = _find_compatible_index(pc)
    if fallback:
        _resolved_index_name = fallback
        logger.warning(
            "Using existing Pinecone index %s (namespace=%s). "
            "Set PINECONE_INDEX_NAME=%s in .env to use it explicitly.",
            fallback,
            _namespace(),
            fallback,
        )
        return

    names = sorted(existing)
    logger.error(
        "No Pinecone index available for dim=%s. Existing indexes: %s. "
        "Delete an unused index in the Pinecone console or set PINECONE_INDEX_NAME "
        "to one with matching dimensions.",
        settings.MISTRAL_EMBEDDING_DIMENSION,
        names or "(none)",
    )


def _index_name() -> str:
    ensure_pinecone_index()
    if not _resolved_index_name:
        raise AppError(
            "PINECONE_INDEX_UNAVAILABLE",
            "Pinecone index is not available. Set PINECONE_INDEX_NAME to an existing "
            f"{settings.MISTRAL_EMBEDDING_DIMENSION}-dimension index or free a slot in Pinecone.",
            503,
        )
    return _resolved_index_name


def _get_index():
    global _index, _index_handle_name
    name = _index_name()
    if _index is not None and _index_handle_name == name:
        return _index
    pc = _pinecone_client()
    _index = pc.Index(name)
    _index_handle_name = name
    return _index


def _namespace() -> str:
    return (settings.PINECONE_NAMESPACE or "chatbot").strip()


def _require_rag_backend() -> None:
    if not mistral_configured():
        raise AppError(
            "MISTRAL_NOT_CONFIGURED",
            "MISTRAL_API_KEY is required for Mistral embeddings.",
            503,
        )
    if not pinecone_configured():
        raise AppError(
            "PINECONE_NOT_CONFIGURED",
            "PINECONE_API_KEY and PINECONE_INDEX_NAME are required for vector storage.",
            503,
        )


async def upsert_chunks(
    chunks: list[ChatChunk],
    *,
    filename: str,
    document_id: uuid.UUID,
) -> None:
    if not chunks:
        return
    _require_rag_backend()

    texts = [chunk.content for chunk in chunks]
    vectors = await embed_texts(texts)
    index = _get_index()

    payload = [
        {
            "id": str(chunk.id),
            "values": vector,
            "metadata": {
                "text": chunk.content[:8000],
                "document_id": str(document_id),
                "filename": filename,
                "chunk_index": chunk.chunk_index,
                "chunk_id": str(chunk.id),
            },
        }
        for chunk, vector in zip(chunks, vectors)
    ]

    # Pinecone upsert batches (max 100 vectors per request for safety)
    batch_size = 100
    for start in range(0, len(payload), batch_size):
        index.upsert(vectors=payload[start : start + batch_size], namespace=_namespace())

    logger.info("Upserted %s vectors to Pinecone for document %s", len(payload), document_id)


async def delete_document_vectors(document_id: uuid.UUID) -> None:
    if not pinecone_configured():
        return
    index = _get_index()
    index.delete(
        filter={"document_id": {"$eq": str(document_id)}},
        namespace=_namespace(),
    )
    logger.info("Deleted Pinecone vectors for document %s", document_id)


async def similarity_search(
    query: str,
    *,
    top_k: int | None = None,
) -> list[tuple[Document, float]]:
    if not pinecone_configured() or not mistral_configured():
        return []

    from app.modules.chatbot.embeddings import get_embeddings

    k = top_k or settings.CHATBOT_TOP_K
    embeddings = get_embeddings()
    query_vector = await embeddings.aembed_query(query)
    index = _get_index()

    try:
        response = index.query(
            vector=query_vector,
            top_k=k,
            namespace=_namespace(),
            include_metadata=True,
        )
    except Exception as exc:
        logger.exception("Pinecone similarity search failed")
        raise AppError("PINECONE_SEARCH_FAILED", f"Vector search failed: {exc}", 503) from exc

    matches = getattr(response, "matches", None) or response.get("matches", [])
    results: list[tuple[Document, float]] = []
    for match in matches:
        metadata = dict(getattr(match, "metadata", None) or match.get("metadata") or {})
        text = str(metadata.pop("text", "") or "")
        score = float(getattr(match, "score", None) or match.get("score") or 0.0)
        results.append((Document(page_content=text, metadata=metadata), score))
    return results


def pinecone_results_to_retrieval(
    scored_docs: list[tuple[Document, float]],
) -> list[tuple[Any, float, Document]]:
    return [(None, score, doc) for doc, score in scored_docs]
