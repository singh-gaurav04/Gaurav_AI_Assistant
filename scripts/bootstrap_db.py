"""Reset public schema and run all migrations, seed data, and ensure admin exists."""
import asyncio
import subprocess
import sys
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.auth.model import Admin
from sqlalchemy import select

DEFAULT_ADMIN_EMAIL = "gaurav26lnct@gmail.com"
DEFAULT_ADMIN_PASSWORD = "PortfolioAdmin123!"
DEFAULT_ADMIN_NAME = "Gaurav Singh"


async def reset_schema() -> None:
    async with SessionLocal() as db:
        await db.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await db.execute(text("CREATE SCHEMA public"))
        await db.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
        await db.execute(text("GRANT ALL ON SCHEMA public TO public"))
        await db.commit()
    print("Database schema reset")


async def ensure_admin() -> None:
    async with SessionLocal() as db:
        existing = await db.scalar(select(Admin).where(Admin.email == DEFAULT_ADMIN_EMAIL))
        if existing:
            print(f"Admin already exists: {DEFAULT_ADMIN_EMAIL}")
            return

        db.add(
            Admin(
                name=DEFAULT_ADMIN_NAME,
                email=DEFAULT_ADMIN_EMAIL,
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
            )
        )
        await db.commit()
        print(f"Admin created: {DEFAULT_ADMIN_EMAIL}")


def run_migrations() -> None:
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit("Migration failed")
    print("Migrations applied")


def run_seed() -> None:
    result = subprocess.run([sys.executable, "scripts/seed_portfolio.py"], cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit("Seed failed")
    print("Portfolio seed complete")


async def main() -> None:
    await reset_schema()
    run_migrations()
    run_seed()
    await ensure_admin()
    print("\nAdmin login:")
    print(f"  Email:    {DEFAULT_ADMIN_EMAIL}")
    print(f"  Password: {DEFAULT_ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
