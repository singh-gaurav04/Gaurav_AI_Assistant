"""PDF text extraction + LangChain RecursiveCharacterTextSplitter chunking."""

from __future__ import annotations

import re
from io import BytesIO

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.core.config import settings


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(data: bytes) -> tuple[str, int]:
    reader = PdfReader(BytesIO(data))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text.strip())
    page_count = len(reader.pages)
    full_text = "\n\n".join(p for p in pages if p)
    return normalize_text(full_text), page_count


def extract_pdf_documents(data: bytes, *, source: str = "document.pdf") -> tuple[list[Document], int]:
    """One LangChain Document per PDF page (empty pages skipped)."""
    reader = PdfReader(BytesIO(data))
    documents: list[Document] = []
    for index, page in enumerate(reader.pages, start=1):
        text = normalize_text(page.extract_text() or "")
        if not text:
            continue
        documents.append(
            Document(
                page_content=text,
                metadata={"source": source, "page": index},
            )
        )
    return documents, len(reader.pages)


def get_text_splitter(
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> RecursiveCharacterTextSplitter:
    size = settings.CHATBOT_CHUNK_SIZE if chunk_size is None else chunk_size
    overlap = settings.CHATBOT_CHUNK_OVERLAP if chunk_overlap is None else chunk_overlap
    return RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )


def chunk_documents(
    documents: list[Document],
    *,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Document]:
    if not documents:
        return []
    return get_text_splitter(chunk_size, chunk_overlap).split_documents(documents)


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """Backward-compatible helper used by ingest when only raw text is available."""
    text = normalize_text(text)
    if not text:
        return []
    docs = get_text_splitter(chunk_size, overlap).create_documents([text])
    return [doc.page_content for doc in docs if doc.page_content.strip()]
