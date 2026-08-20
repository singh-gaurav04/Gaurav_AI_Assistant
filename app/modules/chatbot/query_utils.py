"""Typo-tolerant query normalization for chatbot retrieval and intent checks."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

COMMON_TYPOS: dict[str, str] = {
    "contat": "contact",
    "conact": "contact",
    "contcat": "contact",
    "contct": "contact",
    "emial": "email",
    "emal": "email",
    "emai": "email",
    "phon": "phone",
    "phne": "phone",
    "phoen": "phone",
    "moblie": "mobile",
    "mobil": "mobile",
    "porfolio": "portfolio",
    "portfoilo": "portfolio",
    "portfilio": "portfolio",
    "projct": "project",
    "projet": "project",
    "projec": "project",
    "skils": "skills",
    "skil": "skill",
    "experince": "experience",
    "expereince": "experience",
    "experence": "experience",
    "certifcation": "certification",
    "certificaton": "certification",
    "gaurv": "gaurav",
    "garav": "gaurav",
    "gauarv": "gaurav",
    "collabrate": "collaborate",
    "collborate": "collaborate",
    "hir": "hire",
    "hiringg": "hiring",
    "resum": "resume",
    "resuem": "resume",
    "develper": "developer",
    "developr": "developer",
    "enginer": "engineer",
    "enginering": "engineering",
    "backround": "background",
    "qualifcation": "qualification",
    "techstack": "stack",
    "servce": "service",
    "servic": "service",
    "bookng": "booking",
    "messge": "message",
    "messag": "message",
    "numbr": "number",
    "nmber": "number",
    "detials": "details",
    "detailss": "details",
}

PORTFOLIO_KEYWORDS: tuple[str, ...] = (
    "gaurav",
    "portfolio",
    "project",
    "projects",
    "skill",
    "skills",
    "experience",
    "resume",
    "cv",
    "work",
    "job",
    "hire",
    "hiring",
    "contact",
    "email",
    "phone",
    "mobile",
    "number",
    "certification",
    "service",
    "services",
    "book",
    "booking",
    "collaborate",
    "about",
    "bio",
    "developer",
    "engineer",
    "background",
    "qualification",
    "stack",
)

CONTACT_INTENTS: tuple[str, ...] = (
    "contact",
    "email",
    "phone",
    "mobile",
    "reach",
    "call",
    "message",
    "number",
)

PROFILE_INTENTS: tuple[str, ...] = (
    "skill",
    "project",
    "experience",
    "bio",
    "about",
    "who",
    "resume",
    "background",
    "certification",
    "service",
)


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall((text or "").lower())


def _similar(a: str, b: str, *, threshold: float) -> bool:
    if a == b:
        return True
    if len(a) < 3 or len(b) < 3:
        return False
    return SequenceMatcher(None, a, b).ratio() >= threshold


def _best_keyword_match(token: str) -> str | None:
    if token in COMMON_TYPOS:
        return COMMON_TYPOS[token]

    best: tuple[str, float] | None = None
    for keyword in PORTFOLIO_KEYWORDS:
        ratio = SequenceMatcher(None, token, keyword).ratio()
        if ratio >= 0.84 and (best is None or ratio > best[1]):
            best = (keyword, ratio)

    return best[0] if best else None


def normalize_query(query: str) -> str:
    """Fix common typos and fuzzy-match portfolio keywords for retrieval."""
    if not query:
        return query

    result = query
    seen: set[str] = set()
    for token in tokenize(query):
        if token in seen:
            continue
        seen.add(token)
        replacement = COMMON_TYPOS.get(token) or _best_keyword_match(token)
        if replacement and replacement != token:
            result = re.sub(rf"\b{re.escape(token)}\b", replacement, result, flags=re.IGNORECASE)
    return result


def is_portfolio_related(query: str) -> bool:
    tokens = tokenize(normalize_query(query))
    if not tokens:
        return False

    for token in tokens:
        if token in PORTFOLIO_KEYWORDS:
            return True
        if token in COMMON_TYPOS.values():
            return True
        for keyword in PORTFOLIO_KEYWORDS:
            if _similar(token, keyword, threshold=0.84):
                return True
    return False


def matches_intent(query: str, intents: tuple[str, ...]) -> bool:
    tokens = tokenize(normalize_query(query))
    for token in tokens:
        for intent in intents:
            if token == intent or _similar(token, intent, threshold=0.84):
                return True
    return False


def fuzzy_lexical_score(query: str, text: str) -> float:
    query_tokens = tokenize(normalize_query(query))
    if not query_tokens:
        return 0.0

    doc_tokens = tokenize(text)
    if not doc_tokens:
        return 0.0

    score = 0.0
    for q_token in query_tokens:
        if q_token in doc_tokens:
            score += 1.0
            continue
        for d_token in doc_tokens:
            if _similar(q_token, d_token, threshold=0.86):
                score += 0.75
                break

    return score / len(query_tokens)
