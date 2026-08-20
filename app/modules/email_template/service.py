import logging
from abc import ABC, abstractmethod
from email.message import EmailMessage
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

class SMTPProvider(EmailProvider):
    async def send(self, to: str, subject: str, html: str, text: str | None = None):
        if not settings.SMTP_HOST:
            raise AppError("EMAIL_NOT_CONFIGURED", "Email provider is not configured", 503)
        try:
            import aiosmtplib
        except ImportError as exc:
            raise AppError("EMAIL_NOT_CONFIGURED", "aiosmtplib is not installed", 503) from exc

        msg = EmailMessage()
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(text or "Please view this email in an HTML-capable client.")
        msg.add_alternative(html, subtype="html")

        username = settings.SMTP_USERNAME or None
        password = settings.SMTP_PASSWORD or None

        try:
            smtp = aiosmtplib.SMTP(
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                use_tls=False,
                start_tls=settings.SMTP_USE_TLS,
            )
            await smtp.connect()
            if username and password:
                await smtp.login(username, password)
            await smtp.send_message(msg)
            await smtp.quit()
        except Exception as exc:
            logger.exception("SMTP send failed to %s", to)
            raise AppError("EMAIL_SEND_FAILED", f"Could not send email: {exc}", 503) from exc

class EmailService:
    def __init__(self):
        self.provider = SMTPProvider()

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
        if not settings.SMTP_HOST:
            logger.warning("Email skipped (%s): SMTP_HOST is not configured", slug)
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
