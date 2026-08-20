"""Multi-provider LLM catalog + LangChain chat model factory."""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)

# Admin-selectable providers and models. API keys stay in server .env.
PROVIDER_CATALOG: list[dict[str, Any]] = [
    {
        "id": "openai",
        "label": "OpenAI",
        "models": [
            {"id": "gpt-4o-mini", "label": "GPT-4o Mini"},
            {"id": "gpt-4o", "label": "GPT-4o"},
            {"id": "gpt-4.1-mini", "label": "GPT-4.1 Mini"},
            {"id": "gpt-4.1", "label": "GPT-4.1"},
            {"id": "o4-mini", "label": "o4 Mini"},
        ],
    },
    {
        "id": "anthropic",
        "label": "Anthropic",
        "models": [
            {"id": "claude-3-5-haiku-latest", "label": "Claude 3.5 Haiku"},
            {"id": "claude-3-5-sonnet-latest", "label": "Claude 3.5 Sonnet"},
            {"id": "claude-sonnet-4-0", "label": "Claude Sonnet 4"},
        ],
    },
    {
        "id": "google",
        "label": "Google Gemini",
        "models": [
            {"id": "gemini-2.0-flash", "label": "Gemini 2.0 Flash"},
            {"id": "gemini-1.5-flash", "label": "Gemini 1.5 Flash"},
            {"id": "gemini-1.5-pro", "label": "Gemini 1.5 Pro"},
        ],
    },
    {
        "id": "groq",
        "label": "Groq",
        "models": [
            {"id": "llama-3.3-70b-versatile", "label": "Llama 3.3 70B"},
            {"id": "llama-3.1-8b-instant", "label": "Llama 3.1 8B Instant"},
            {"id": "mixtral-8x7b-32768", "label": "Mixtral 8x7B"},
        ],
    },
    {
        "id": "mistral",
        "label": "Mistral AI",
        "models": [
            {"id": "mistral-small-latest", "label": "Mistral Small"},
            {"id": "mistral-large-latest", "label": "Mistral Large"},
            {"id": "open-mistral-nemo", "label": "Mistral Nemo"},
            {"id": "ministral-8b-latest", "label": "Ministral 8B"},
            {"id": "codestral-latest", "label": "Codestral"},
        ],
    },
    {
        "id": "openrouter",
        "label": "OpenRouter",
        "models": [
            {"id": "openai/gpt-4o-mini", "label": "GPT-4o Mini (via OpenRouter)"},
            {"id": "anthropic/claude-3.5-sonnet", "label": "Claude 3.5 Sonnet (via OpenRouter)"},
            {"id": "google/gemini-2.0-flash-001", "label": "Gemini 2.0 Flash (via OpenRouter)"},
            {"id": "meta-llama/llama-3.3-70b-instruct", "label": "Llama 3.3 70B (via OpenRouter)"},
            {"id": "mistralai/mistral-small", "label": "Mistral Small (via OpenRouter)"},
        ],
    },
]

DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-4o-mini"


def _provider_key(provider_id: str) -> str:
    mapping = {
        "openai": settings.OPENAI_API_KEY,
        "anthropic": settings.ANTHROPIC_API_KEY,
        "google": settings.GOOGLE_API_KEY,
        "groq": settings.GROQ_API_KEY,
        "mistral": settings.MISTRAL_API_KEY,
        "openrouter": settings.OPENROUTER_API_KEY,
    }
    return (mapping.get(provider_id) or "").strip()


def provider_is_configured(provider_id: str) -> bool:
    return bool(_provider_key(provider_id))


def list_provider_options() -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for item in PROVIDER_CATALOG:
        options.append(
            {
                "id": item["id"],
                "label": item["label"],
                "configured": provider_is_configured(item["id"]),
                "models": item["models"],
            }
        )
    return options


def validate_provider_model(provider: str, model: str) -> tuple[str, str]:
    provider = (provider or DEFAULT_PROVIDER).strip().lower()
    model = (model or DEFAULT_MODEL).strip()
    catalog = {item["id"]: item for item in PROVIDER_CATALOG}
    if provider not in catalog:
        raise AppError("INVALID_LLM_PROVIDER", f"Unsupported LLM provider: {provider}", 400)
    allowed = {m["id"] for m in catalog[provider]["models"]}
    if model not in allowed:
        # Allow custom model ids for flexibility, but warn via known list preference
        if not model:
            model = catalog[provider]["models"][0]["id"]
    return provider, model


def get_chat_llm(
    *,
    provider: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
):
    """Build a LangChain chat model for the selected provider."""
    provider, model = validate_provider_model(provider or DEFAULT_PROVIDER, model or DEFAULT_MODEL)
    temp = settings.CHATBOT_TEMPERATURE if temperature is None else float(temperature)
    api_key = _provider_key(provider)

    if not api_key:
        return None

    try:
        if provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=model, api_key=api_key, temperature=temp)

        if provider == "openrouter":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=model,
                api_key=api_key,
                temperature=temp,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": settings.FRONTEND_URL or "http://localhost:5173",
                    "X-Title": settings.APP_NAME or "Portfolio Chatbot",
                },
            )

        if provider == "groq":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=model,
                api_key=api_key,
                temperature=temp,
                base_url="https://api.groq.com/openai/v1",
            )

        if provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(model=model, api_key=api_key, temperature=temp)

        if provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=temp)

        if provider == "mistral":
            from langchain_mistralai import ChatMistralAI

            return ChatMistralAI(model=model, api_key=api_key, temperature=temp)
    except ImportError as exc:
        logger.exception("Missing package for provider %s", provider)
        raise AppError(
            "LLM_PROVIDER_UNAVAILABLE",
            f"Server is missing packages for provider '{provider}'. Install the required LangChain integration.",
            503,
        ) from exc

    raise AppError("INVALID_LLM_PROVIDER", f"Unsupported LLM provider: {provider}", 400)
