from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.core.exceptions import AppError
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.model import Admin
from app.modules.auth.schema import ChangePasswordRequest, LoginRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    admin = await db.scalar(select(Admin).where(Admin.email == payload.email.lower()))
    if not admin or not admin.is_active or not verify_password(payload.password, admin.password_hash):
        raise AppError("INVALID_CREDENTIALS", "Invalid email or password", 401)
    admin.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    return {
        "success": True,
        "data": {
            "access_token": create_access_token(admin.id, admin.token_version),
            "token_type": "bearer",
        },
    }


@router.get("/me")
async def me(admin: Admin = Depends(get_current_admin)):
    return {
        "success": True,
        "data": {
            "id": str(admin.id),
            "name": admin.name,
            "email": admin.email,
            "is_active": admin.is_active,
        },
    }


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(payload.current_password, admin.password_hash):
        raise AppError("INVALID_PASSWORD", "Current password is incorrect", 400)

    admin.password_hash = hash_password(payload.new_password)
    # Invalidate other sessions; keep this one valid with a fresh token
    admin.token_version += 1
    await db.commit()
    await db.refresh(admin)

    return {
        "success": True,
        "data": {
            "access_token": create_access_token(admin.id, admin.token_version),
            "token_type": "bearer",
        },
        "message": "Password updated",
    }


@router.post("/logout")
async def logout(admin: Admin = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    admin.token_version += 1
    await db.commit()
    return {"success": True, "data": None, "message": "Logged out"}
