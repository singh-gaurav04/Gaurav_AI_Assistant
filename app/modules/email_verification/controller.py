from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.email_verification.schema import SendOtpRequest, VerifyOtpRequest
from app.modules.email_verification.service import email_verification_service

public_router = APIRouter(tags=["Email verification"])


@public_router.post("/email-verification/send")
async def send_email_otp(payload: SendOtpRequest, db: AsyncSession = Depends(get_db)):
    await email_verification_service.send_otp(db, payload.email, payload.purpose)
    return {"success": True, "message": "Verification code sent to your email."}


@public_router.post("/email-verification/verify")
async def verify_email_otp(payload: VerifyOtpRequest, db: AsyncSession = Depends(get_db)):
    token = await email_verification_service.verify_otp(db, payload.email, payload.purpose, payload.otp)
    return {
        "success": True,
        "data": {"verification_token": token},
        "message": "Email verified successfully.",
    }
