import asyncio

from app.core.database import SessionLocal
from app.modules.email_template.seed import sync_default_email_templates


async def main() -> None:
    async with SessionLocal() as db:
        count = await sync_default_email_templates(db)
        print(f"Synced {count} email template(s) with branded HTML layouts.")


if __name__ == "__main__":
    asyncio.run(main())
