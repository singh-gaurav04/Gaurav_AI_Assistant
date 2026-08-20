import asyncio

from app.core.database import SessionLocal
from app.modules.email_template.seed import ensure_default_email_templates


async def main() -> None:
    async with SessionLocal() as db:
        created = await ensure_default_email_templates(db)
        print(f"Email templates ready ({created} newly created)")


if __name__ == "__main__":
    asyncio.run(main())
