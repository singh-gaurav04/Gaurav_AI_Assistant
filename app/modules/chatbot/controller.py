from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppError
from app.modules.chatbot.schema import ChatRequest
from app.modules.chatbot.service import chatbot_service

public_router = APIRouter(tags=["Chatbot"])


@public_router.get("/chatbot/config")
async def get_chatbot_config(db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": await chatbot_service.get_config(db)}


@public_router.post("/chat")
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        data = await chatbot_service.chat(db, payload)
        return {"success": True, "data": data}
    except AppError:
        raise
    except Exception as exc:
        raise AppError("CHAT_FAILED", "Unexpected chatbot error", 500) from exc
