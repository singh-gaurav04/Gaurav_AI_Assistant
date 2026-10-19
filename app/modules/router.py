from fastapi import APIRouter
from app.modules.contact.controller import public_router as contact_public
from app.modules.email_verification.controller import public_router as email_verification_public
from app.modules.chatbot.controller import public_router as chatbot_public

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(contact_public)
api_router.include_router(email_verification_public)
api_router.include_router(chatbot_public)
