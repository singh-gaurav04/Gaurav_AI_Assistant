import re
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

JUNIOR_RE = re.compile(r"\b(aspiring|enthusiast)\b", re.I)

PROFESSIONAL_TITLE = "AI Engineer | GenAI | Backend"
PROFESSIONAL_BIO = (
    "AI Engineer focused on Generative AI, RAG systems, and backend development. "
    "I build production-ready intelligent applications with Python, FastAPI, LangChain, "
    "and modern full-stack tools. Open to AI Engineer and GenAI roles."
)
PROFESSIONAL_STATUS = "Open to AI Engineer roles"


async def ensure_professional_profile_copy(db: AsyncSession) -> bool:
    """Replace junior wording (aspiring/enthusiast) in the live profile row."""
    result = await db.execute(
        text(
            """
            SELECT id, title, bio, placement_status
            FROM profiles
            ORDER BY id
            LIMIT 1
            """
        )
    )
    row = result.mappings().first()
    if not row:
        return False

    title = row["title"] or ""
    bio = row["bio"] or ""
    status = row["placement_status"] or ""
    dirty = False

    new_title = title
    new_bio = bio
    new_status = status

    if JUNIOR_RE.search(title) or "aspiring" in title.lower():
        new_title = PROFESSIONAL_TITLE
        dirty = True
    if JUNIOR_RE.search(bio):
        new_bio = PROFESSIONAL_BIO
        dirty = True
    if JUNIOR_RE.search(status) or "actively seeking" in status.lower():
        new_status = PROFESSIONAL_STATUS
        dirty = True

    if not dirty:
        return False

    await db.execute(
        text(
            """
            UPDATE profiles
            SET title = :title,
                bio = :bio,
                placement_status = :status
            WHERE id = :id
            """
        ),
        {"id": row["id"], "title": new_title, "bio": new_bio, "status": new_status},
    )
    await db.commit()
    return True
