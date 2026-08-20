import asyncio
from sqlalchemy import text
from app.core.database import SessionLocal


async def main():
    async with SessionLocal() as db:
        try:
            result = await db.execute(text("SELECT version_num FROM alembic_version"))
            print("alembic_version:", result.scalar())
        except Exception as exc:
            print("alembic_version error:", exc)

        result = await db.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
        )
        print("tables:", [row[0] for row in result.fetchall()])


if __name__ == "__main__":
    asyncio.run(main())
