import asyncio, getpass
from sqlalchemy import select
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.auth.model import Admin

async def main():
    email=input("Admin email: ").strip().lower()
    name=input("Admin name: ").strip()
    password=getpass.getpass("Password: ")
    if len(password)<12:
        raise SystemExit("Use at least 12 characters")
    async with SessionLocal() as db:
        if await db.scalar(select(Admin).where(Admin.email==email)):
            raise SystemExit("Admin already exists")
        db.add(Admin(name=name,email=email,password_hash=hash_password(password)))
        await db.commit()
        print("Admin created")

if __name__=="__main__":
    asyncio.run(main())
