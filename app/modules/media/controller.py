from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.core.exceptions import AppError
from app.modules.media.model import Media
from app.modules.media.image_service import compress_image
from app.modules.media.imagekit_service import imagekit_service

admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

@admin_router.post("/media/upload", status_code=201)
async def upload_media(folder: str = "/portfolio/general/", file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    data, mime, w, h = await compress_image(file)
    result = await imagekit_service.upload(data, (file.filename or "image") + ".webp", folder)
    media = Media(
        file_id=result["fileId"], url=result["url"], file_name=result["name"], mime_type=mime,
        size=int(result.get("size", len(data))), width=w, height=h, folder=folder,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return {"success": True, "data": {"id": str(media.id), "url": media.url, "file_id": media.file_id}}


@admin_router.post("/media/upload-file", status_code=201)
async def upload_raw_file(folder: str = "/portfolio/documents/", file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    raw = await file.read()
    if not raw:
        raise AppError("EMPTY_FILE", "File is empty", 400)
    if len(raw) > 15 * 1024 * 1024:
        raise AppError("FILE_TOO_LARGE", "File exceeds 15MB limit", 413)

    allowed = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    content_type = file.content_type or "application/octet-stream"
    if content_type not in allowed and not (file.filename or "").lower().endswith((".pdf", ".doc", ".docx")):
        raise AppError("INVALID_FILE_TYPE", "Only PDF/DOC/DOCX files are allowed", 415)

    filename = file.filename or "resume.pdf"
    result = await imagekit_service.upload(raw, filename, folder)
    media = Media(
        file_id=result["fileId"],
        url=result["url"],
        file_name=result["name"],
        mime_type=content_type,
        size=int(result.get("size", len(raw))),
        width=None,
        height=None,
        folder=folder,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return {"success": True, "data": {"id": str(media.id), "url": media.url, "file_id": media.file_id}}

@admin_router.delete("/media/{id}", status_code=204)
async def delete_media(id: UUID, db: AsyncSession = Depends(get_db)):
    media = await db.get(Media, id)
    if not media:
        raise AppError("MEDIA_NOT_FOUND", "Media not found", 404)
    await imagekit_service.delete(media.file_id)
    await db.delete(media)
    await db.commit()
