from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def ensure_chatbot_schema(db: AsyncSession) -> None:
    """Add chatbot settings columns if missing (safe for existing DBs)."""
    await db.execute(
        text(
            """
            ALTER TABLE chatbot_settings
            ADD COLUMN IF NOT EXISTS llm_provider VARCHAR(40) NOT NULL DEFAULT 'openai';
            """
        )
    )
    await db.execute(
        text(
            """
            ALTER TABLE chatbot_settings
            ADD COLUMN IF NOT EXISTS llm_model VARCHAR(120) NOT NULL DEFAULT 'gpt-4o-mini';
            """
        )
    )
    await db.execute(
        text(
            """
            ALTER TABLE chatbot_settings
            ADD COLUMN IF NOT EXISTS llm_temperature DOUBLE PRECISION NOT NULL DEFAULT 0.2;
            """
        )
    )
    await db.execute(
        text(
            """
            ALTER TABLE chatbot_settings
            ADD COLUMN IF NOT EXISTS chunk_size INTEGER NOT NULL DEFAULT 800;
            """
        )
    )
    await db.execute(
        text(
            """
            ALTER TABLE chatbot_settings
            ADD COLUMN IF NOT EXISTS chunk_overlap INTEGER NOT NULL DEFAULT 120;
            """
        )
    )
    await db.commit()
