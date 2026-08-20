"""Create the first admin from env when none exists (Render-friendly, no shell needed)."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.modules.auth.model import Admin

logger = logging.getLogger(__name__)


async def ensure_bootstrap_admin(db: AsyncSession) -> bool:
    """
    If ADMIN_PASSWORD is set and no admin with ADMIN_EMAIL exists, create one.
    Never overwrites an existing admin password (change it from the admin UI).
    Returns True if a new admin was created.
    """
    email = (settings.ADMIN_EMAIL or "").strip().lower()
    password = (settings.ADMIN_PASSWORD or "").strip()
    name = (settings.ADMIN_NAME or "").strip() or "Admin"

    if not email or not password:
        logger.info(
            "Admin bootstrap skipped (set ADMIN_EMAIL and ADMIN_PASSWORD to auto-create the first admin)"
        )
        return False

    if len(password) < 8:
        logger.warning("Admin bootstrap skipped: ADMIN_PASSWORD must be at least 8 characters")
        return False

    existing = await db.scalar(select(Admin).where(Admin.email == email))
    if existing:
        logger.info("Admin bootstrap skipped: admin already exists (%s)", email)
        return False

    any_admin = await db.scalar(select(Admin).limit(1))
    if any_admin:
        logger.info(
            "Admin bootstrap skipped: an admin already exists (%s). "
            "Use change-password in the admin UI or create another user manually.",
            any_admin.email,
        )
        return False

    db.add(
        Admin(
            name=name,
            email=email,
            password_hash=hash_password(password),
            is_active=True,
        )
    )
    await db.commit()
    logger.info("Bootstrap admin created for %s — change the password after first login", email)
    return True
