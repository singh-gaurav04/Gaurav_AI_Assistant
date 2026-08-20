import logging
from abc import ABC, abstractmethod

import httpx
from jinja2 import Environment, StrictUndefined
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppError
from app.modules.email_template.model import EmailTemplate

logger = logging.getLogger(__name__)
env = Environment(autoescape=True, undefined=StrictUndefined)


class EmailProvider(ABC):
    @abstractmethod
    async def send(self, to: str, subject: str, html: str, text: str | None = None): ...


class MailgunProvider(EmailProvider):
    """Send email via Mailgun HTTP API (HTTPS — works on Render free tier)."""

    def _api_key(self) -> str:
        return (settings.MAILGUN_API_KEY or settings.EMAIL_API_KEY or "").strip()

    def _domain(self) -> str:
        return (settings.MAILGUN_DOMAIN or "").strip()

    def _base_url(self) -> str:
        region = (settings.MAILGUN_REGION or "us").strip().lower()
        if region in {"eu", "europe"}:
            return "https://api.eu.mailgun.net"
        return (settings.MAILGUN_API_BASE or "https://api.mailgun.net").rstrip("/")

    def _from_address(self) -> str:
        configured = (settings.EMAIL_FROM or "").strip()
        if configured:
            return configured
        domain = self._domain()
        return f"Portfolio <mailgun@{domain}>" if domain else ""

    async def send(self, to: str, subject: str, html: str, text: str | None = None):
        api_key = self._api_key()
        domain = self._domain()
        from_address = self._from_address()

        if not api_key or api_key in {"key-xxxxxxxx", "xxxxxxxx", "your-mailgun-api-key"}:
            raise AppError(
                "EMAIL_NOT_CONFIGURED",
                "Mailgun API key is missing. Set MAILGUN_API_KEY (or EMAIL_API_KEY) in your environment.",
                503,
            )
        if not domain or domain in {"sandboxXXXX.mailgun.org", "your-domain.mailgun.org"}:
            raise AppError(
                "EMAIL_NOT_CONFIGURED",
                "Mailgun domain is missing. Set MAILGUN_DOMAIN (e.g. sandbox….mailgun.org or your verified domain).",
                503,
            )
        if not from_address:
            raise AppError("EMAIL_NOT_CONFIGURED", "EMAIL_FROM is not configured", 503)

        data = {
            "from": from_address,
            "to": to,
            "subject": subject,
            "html": html,
            "text": text or "Please view this email in an HTML-capable client.",
        }
        if settings.ADMIN_EMAIL and settings.ADMIN_EMAIL.lower() != to.lower():
            data["h:Reply-To"] = settings.ADMIN_EMAIL

        url = f"{self._base_url()}/v3/{domain}/messages"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, data=data, auth=("api", api_key))
            if response.status_code >= 400:
                detail = response.text[:500]
                logger.error("Mailgun send failed to %s: %s %s", to, response.status_code, detail)
                raise AppError(
                    "EMAIL_SEND_FAILED",
                    f"Could not send email via Mailgun ({response.status_code}): {detail}",
                    503,
                )
            payload = response.json() if response.content else {}
            logger.info("Mailgun email sent to %s (id=%s)", to, payload.get("id") or payload.get("message"))
        except AppError:
            raise
        except Exception as exc:
            logger.exception("Mailgun send failed to %s", to)
            raise AppError("EMAIL_SEND_FAILED", f"Could not send email: {exc}", 503) from exc


def _build_provider() -> EmailProvider:
    provider = (settings.EMAIL_PROVIDER or "mailgun").strip().lower()
    if provider in {"mailgun", "http", "api"}:
        return MailgunProvider()
    # Legacy values now map to Mailgun
    logger.warning("EMAIL_PROVIDER=%s is deprecated; using Mailgun", provider)
    return MailgunProvider()


class EmailService:
    def __init__(self):
        self.provider = _build_provider()

    def _is_configured(self) -> bool:
        key = (settings.MAILGUN_API_KEY or settings.EMAIL_API_KEY or "").strip()
        domain = (settings.MAILGUN_DOMAIN or "").strip()
        if not key or key in {"key-xxxxxxxx", "xxxxxxxx", "your-mailgun-api-key"}:
            return False
        if not domain or domain in {"sandboxXXXX.mailgun.org", "your-domain.mailgun.org"}:
            return False
        return True

    async def render(self, db: AsyncSession, slug: str, values: dict) -> tuple[str, str, str | None]:
        tpl = await db.scalar(select(EmailTemplate).where(EmailTemplate.slug == slug, EmailTemplate.is_active.is_(True)))
        if not tpl:
            raise AppError("EMAIL_TEMPLATE_NOT_FOUND", "Email template is unavailable", 404)
        missing = [x for x in tpl.variables if x not in values]
        if missing:
            raise AppError("EMAIL_TEMPLATE_VARIABLES_MISSING", f"Missing template variables: {', '.join(missing)}", 400)
        subject = env.from_string(tpl.subject).render(**values)
        html = env.from_string(tpl.html_body).render(**values)
        text = env.from_string(tpl.text_body).render(**values) if tpl.text_body else None
        return subject, html, text

    async def send_template(self, db: AsyncSession, to: str, slug: str, values: dict):
        subject, html, text = await self.render(db, slug, values)
        await self.provider.send(to, subject, html, text)

    async def send_template_safe(self, db: AsyncSession, to: str | None, slug: str, values: dict) -> bool:
        if not to or not to.strip():
            return False
        if not self._is_configured():
            logger.warning(
                "Email skipped (%s): set MAILGUN_API_KEY and MAILGUN_DOMAIN in the environment",
                slug,
            )
            return False
        try:
            await self.send_template(db, to.strip(), slug, values)
            return True
        except AppError as exc:
            logger.warning("Email failed (%s → %s): %s", slug, to, exc.message)
            return False
        except Exception as exc:
            logger.exception("Email failed (%s → %s): %s", slug, to, exc)
            return False

    async def notify_admin_safe(self, db: AsyncSession, slug: str, values: dict) -> bool:
        if not settings.ADMIN_EMAIL:
            logger.warning("Admin email skipped (%s): ADMIN_EMAIL is not configured", slug)
            return False
        return await self.send_template_safe(db, settings.ADMIN_EMAIL, slug, values)


email_service = EmailService()
