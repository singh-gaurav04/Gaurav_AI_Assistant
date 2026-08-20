from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from app.core.exceptions import AppError
from app.modules.media.image_service import compress_image
from app.modules.media.imagekit_service import imagekit_service
from app.modules.service.model import Service
from app.modules.service.schema import ServiceCreate, ServiceUpdate
from app.modules.service.repository import service_repository
from app.utils.slug import slugify

MAX_GALLERY_IMAGES = 12


class ServiceService:
    async def create(self, db: AsyncSession, data: ServiceCreate) -> Service:
        payload = data.model_dump()
        base = slugify(payload.pop("slug") or payload["title"])
        payload["slug"] = await service_repository.unique_slug(db, base)
        payload["gallery_images"] = payload.get("gallery_images") or []
        if payload.get("tag") == "":
            payload["tag"] = None
        if payload.get("icon") == "":
            payload["icon"] = None
        obj = Service(**payload)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def list(self, db: AsyncSession, public_only: bool = False) -> list[Service]:
        return await service_repository.list(db, public_only)

    async def get(self, db: AsyncSession, id: UUID) -> Service:
        obj = await service_repository.get(db, id)
        if not obj:
            raise AppError("SERVICE_NOT_FOUND", "Service not found", 404)
        return obj

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Service:
        obj = await service_repository.by_slug(db, slug, public_only=True)
        if not obj:
            raise AppError("SERVICE_NOT_FOUND", "Service not found", 404)
        return obj

    async def update(self, db: AsyncSession, id: UUID, data: ServiceUpdate) -> Service:
        obj = await self.get(db, id)
        payload = data.model_dump()
        requested = payload.pop("slug")
        base = slugify(requested or payload["title"])
        payload["slug"] = await service_repository.unique_slug(db, base, exclude_id=obj.id)
        payload["gallery_images"] = (
            payload.get("gallery_images") if payload.get("gallery_images") is not None else (obj.gallery_images or [])
        )
        if payload.get("tag") == "":
            payload["tag"] = None
        if payload.get("icon") == "":
            payload["icon"] = None
        for key, value in payload.items():
            setattr(obj, key, value)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, id: UUID) -> None:
        obj = await self.get(db, id)
        file_ids = []
        if obj.imagekit_file_id:
            file_ids.append(obj.imagekit_file_id)
        for item in obj.gallery_images or []:
            fid = item.get("file_id") if isinstance(item, dict) else None
            if fid:
                file_ids.append(fid)
        for fid in set(file_ids):
            try:
                await imagekit_service.delete(fid)
            except AppError:
                pass
        await db.delete(obj)
        await db.commit()

    async def upload_featured_image(self, db: AsyncSession, id: UUID, file: UploadFile) -> Service:
        obj = await self.get(db, id)
        data, _, _, _ = await compress_image(file)
        slug = obj.slug or "service"
        result = await imagekit_service.upload(
            data,
            f"{slug}-featured.webp",
            "/portfolio/services/",
        )

        if obj.imagekit_file_id:
            try:
                await imagekit_service.delete(obj.imagekit_file_id)
            except AppError:
                pass

        obj.featured_image_url = result["url"]
        obj.imagekit_file_id = result["fileId"]
        await db.commit()
        await db.refresh(obj)
        return obj

    async def add_gallery_image(self, db: AsyncSession, id: UUID, file: UploadFile) -> Service:
        obj = await self.get(db, id)
        gallery = list(obj.gallery_images or [])
        if len(gallery) >= MAX_GALLERY_IMAGES:
            raise AppError("GALLERY_LIMIT", f"Maximum {MAX_GALLERY_IMAGES} gallery images allowed", 400)

        data, _, _, _ = await compress_image(file)
        slug = obj.slug or "service"
        result = await imagekit_service.upload(
            data,
            f"{slug}-gallery-{len(gallery) + 1}.webp",
            "/portfolio/services/gallery/",
        )
        gallery.append({"url": result["url"], "file_id": result["fileId"]})
        obj.gallery_images = gallery
        flag_modified(obj, "gallery_images")

        if not obj.featured_image_url:
            obj.featured_image_url = result["url"]
            obj.imagekit_file_id = result["fileId"]

        await db.commit()
        await db.refresh(obj)
        return obj

    async def remove_gallery_image(self, db: AsyncSession, id: UUID, file_id: str) -> Service:
        obj = await self.get(db, id)
        gallery = list(obj.gallery_images or [])
        match = next((item for item in gallery if isinstance(item, dict) and item.get("file_id") == file_id), None)
        if not match:
            raise AppError("GALLERY_IMAGE_NOT_FOUND", "Gallery image not found", 404)

        try:
            await imagekit_service.delete(file_id)
        except AppError:
            pass

        obj.gallery_images = [item for item in gallery if not (isinstance(item, dict) and item.get("file_id") == file_id)]
        flag_modified(obj, "gallery_images")

        if obj.imagekit_file_id == file_id:
            next_image = obj.gallery_images[0] if obj.gallery_images else None
            obj.featured_image_url = next_image.get("url") if next_image else None
            obj.imagekit_file_id = next_image.get("file_id") if next_image else None

        await db.commit()
        await db.refresh(obj)
        return obj


service_service = ServiceService()
