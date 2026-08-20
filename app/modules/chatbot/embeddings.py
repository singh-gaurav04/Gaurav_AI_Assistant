"""Mistral embeddings (primary) with optional OpenAI / hash fallback."""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter

from langchain_core.embeddings import Embeddings

from app.core.config import settings

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def hash_embedding(text: str, dimensions: int = 1024) -> list[float]:
    vector = [0.0] * dimensions
    tokens = tokenize(text)
    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for i in range(0, min(len(digest), 16), 2):
            bucket = int.from_bytes(digest[i : i + 2], "big") % dimensions
            sign = 1.0 if digest[i] % 2 == 0 else -1.0
            vector[bucket] += sign

    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return vector
    return [v / norm for v in vector]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def lexical_score(query: str, text: str) -> float:
    query_tokens = tokenize(query)
    if not query_tokens:
        return 0.0
    doc_tokens = tokenize(text)
    if not doc_tokens:
        return 0.0
    query_counts = Counter(query_tokens)
    doc_counts = Counter(doc_tokens)
    score = 0.0
    for token, q_count in query_counts.items():
        if token in doc_counts:
            score += q_count * doc_counts[token]
    return score / len(query_tokens)


class HashEmbeddings(Embeddings):
    def __init__(self, dimensions: int = 1024) -> None:
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [hash_embedding(text, self.dimensions) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return hash_embedding(text, self.dimensions)

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.embed_documents(texts)

    async def aembed_query(self, text: str) -> list[float]:
        return self.embed_query(text)


def mistral_configured() -> bool:
    return bool(settings.MISTRAL_API_KEY and settings.MISTRAL_API_KEY.strip())


def openai_configured() -> bool:
    return bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())


def get_embeddings() -> Embeddings:
    """Primary: Mistral. Fallback: OpenAI, then local hash."""
    if mistral_configured():
        from langchain_mistralai import MistralAIEmbeddings

        return MistralAIEmbeddings(
            model=settings.MISTRAL_EMBEDDING_MODEL,
            api_key=settings.MISTRAL_API_KEY,
        )

    if openai_configured():
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )

    return HashEmbeddings(dimensions=settings.MISTRAL_EMBEDDING_DIMENSION)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    embeddings = get_embeddings()
    return await embeddings.aembed_documents(texts)


def embedding_provider_label() -> str:
    if mistral_configured():
        return "mistral"
    if openai_configured():
        return "openai"
    return "hash"
