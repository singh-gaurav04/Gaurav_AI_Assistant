import asyncio
import subprocess
import sys
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal


async def cleanup_orphan_enums() -> None:
    async with SessionLocal() as db:
        await db.execute(text("DROP TYPE IF EXISTS testimonialstatus CASCADE"))
        await db.execute(text("DROP TYPE IF EXISTS contactstatus CASCADE"))
        await db.commit()
        print("Ensured enum types are reset before migration")


def main() -> None:
    asyncio.run(cleanup_orphan_enums())
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    print("Migrations applied successfully")


if __name__ == "__main__":
    main()
