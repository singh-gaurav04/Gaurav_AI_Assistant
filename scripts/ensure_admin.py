import asyncio
import sys
from pathlib import Path

from sqlalchemy import select, text

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.auth.model import Admin

DEFAULT_ADMIN_EMAIL = "gaurav26lnct@gmail.com"
DEFAULT_ADMIN_PASSWORD = "PortfolioAdmin123!"
DEFAULT_ADMIN_NAME = "Gaurav Singh"


async def main() -> None:
    async with SessionLocal() as db:
        tables = await db.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
        )
        print("tables:", [row[0] for row in tables.fetchall()])

        admin = await db.scalar(select(Admin))
        if admin:
            print(f"admin_exists: {admin.email}")
            return

        db.add(
            Admin(
                name=DEFAULT_ADMIN_NAME,
                email=DEFAULT_ADMIN_EMAIL,
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
            )
        )
        await db.commit()
        print(f"admin_created: {DEFAULT_ADMIN_EMAIL}")


if __name__ == "__main__":
    asyncio.run(main())
