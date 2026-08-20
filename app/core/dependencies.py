from uuid import UUID
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import AppError
from app.modules.auth.model import Admin

bearer = HTTPBearer(auto_error=False)

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> Admin:
    if not credentials:
        raise AppError("UNAUTHORIZED", "Authentication required", 401)
    try:
        payload = decode_access_token(credentials.credentials)
        admin_id = UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise AppError("INVALID_TOKEN", "Invalid or expired token", 401)

    admin = await db.scalar(select(Admin).where(Admin.id == admin_id))
    if not admin or not admin.is_active:
        raise AppError("UNAUTHORIZED", "Admin access denied", 401)
    if int(payload.get("ver", -1)) != admin.token_version:
        raise AppError("TOKEN_REVOKED", "Token has been revoked", 401)
    return admin
