from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.email_template.defaults import DEFAULT_EMAIL_TEMPLATES
from app.modules.email_template.model import EmailTemplate


async def ensure_default_email_templates(db: AsyncSession) -> int:
    """Insert missing default templates. Does not overwrite admin-edited templates."""
    created = 0
    for tpl in DEFAULT_EMAIL_TEMPLATES:
        exists = await db.scalar(select(EmailTemplate.id).where(EmailTemplate.slug == tpl["slug"]))
        if exists:
            continue
        db.add(
            EmailTemplate(
                name=tpl["name"],
                slug=tpl["slug"],
                subject=tpl["subject"],
                html_body=tpl["html_body"],
                text_body=tpl.get("text_body"),
                variables=tpl["variables"],
                is_active=True,
            )
        )
        created += 1
    if created:
        await db.commit()
    return created


async def sync_default_email_templates(db: AsyncSession) -> int:
    """Upsert subject, HTML, text, and variables for all built-in templates."""
    changed = 0
    for tpl in DEFAULT_EMAIL_TEMPLATES:
        obj = await db.scalar(select(EmailTemplate).where(EmailTemplate.slug == tpl["slug"]))
        if not obj:
            db.add(
                EmailTemplate(
                    name=tpl["name"],
                    slug=tpl["slug"],
                    subject=tpl["subject"],
                    html_body=tpl["html_body"],
                    text_body=tpl.get("text_body"),
                    variables=tpl["variables"],
                    is_active=True,
                )
            )
            changed += 1
            continue

        obj.name = tpl["name"]
        obj.subject = tpl["subject"]
        obj.html_body = tpl["html_body"]
        obj.text_body = tpl.get("text_body")
        obj.variables = tpl["variables"]
        changed += 1

    if changed:
        await db.commit()
    return changed
