from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.core.exceptions import AppError
from app.modules.chatbot.schema import ChatRequest, ChatbotConfigUpdate
from app.modules.chatbot.service import chatbot_service

public_router = APIRouter(tags=["Chatbot"])
admin_router = APIRouter(
    prefix="/admin/chatbot",
    tags=["Admin Chatbot"],
    dependencies=[Depends(get_current_admin)],
)


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


@admin_router.get("/documents")
async def list_documents(db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": await chatbot_service.list_documents(db)}


@admin_router.post("/documents", status_code=201)
async def upload_document(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    data = await chatbot_service.ingest_pdf(db, file)
    return {"success": True, "data": data, "message": "PDF ingested successfully"}


@admin_router.delete("/documents/{document_id}", status_code=204)
async def delete_document(document_id: UUID, db: AsyncSession = Depends(get_db)):
    await chatbot_service.delete_document(db, document_id)


@admin_router.get("/config")
async def get_admin_chatbot_config(db: AsyncSession = Depends(get_db)):
    return {"success": True, "data": await chatbot_service.get_config(db, include_providers=True)}


@admin_router.put("/config")
async def update_chatbot_config(payload: ChatbotConfigUpdate, db: AsyncSession = Depends(get_db)):
    data = await chatbot_service.update_config(db, payload)
    return {"success": True, "data": data, "message": "Chatbot settings updated"}
