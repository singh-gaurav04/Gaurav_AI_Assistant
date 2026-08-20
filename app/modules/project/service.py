from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from app.core.exceptions import AppError
from app.modules.media.image_service import compress_image
from app.modules.media.imagekit_service import imagekit_service
from app.modules.project.model import Project
from app.modules.project.schema import ProjectCreate, ProjectUpdate
from app.modules.project.repository import project_repository
from app.utils.slug import slugify

MAX_GALLERY_IMAGES = 12


class ProjectService:
    async def create(self, db: AsyncSession, data: ProjectCreate):
        d = data.model_dump()
        d["github_url"] = str(d["github_url"]) if d["github_url"] else None
        d["live_url"] = str(d["live_url"]) if d["live_url"] else None
        d["gallery_images"] = d.get("gallery_images") or []
        base = slugify(d.pop("slug") or d["title"])
        d["slug"] = await project_repository.unique_slug(db, base)
        obj = Project(**d)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def get(self, db: AsyncSession, id: UUID):
        obj = await db.get(Project, id)
        if not obj:
            raise AppError("PROJECT_NOT_FOUND", "Project not found", 404)
        return obj

    async def update(self, db, id, data: ProjectUpdate):
        obj = await self.get(db, id)
        d = data.model_dump()
        d["github_url"] = str(d["github_url"]) if d["github_url"] else None
        d["live_url"] = str(d["live_url"]) if d["live_url"] else None
        d["gallery_images"] = d.get("gallery_images") if d.get("gallery_images") is not None else (obj.gallery_images or [])
        requested = d.pop("slug")
        base = slugify(requested or d["title"])
        d["slug"] = await project_repository.unique_slug(db, base, exclude_id=obj.id)
        for k, v in d.items():
            setattr(obj, k, v)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db, id):
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

    async def upload_featured_image(self, db: AsyncSession, id: UUID, file: UploadFile):
        obj = await self.get(db, id)
        data, _, _, _ = await compress_image(file)
        slug = obj.slug or "project"
        result = await imagekit_service.upload(
            data,
            f"{slug}-featured.webp",
            "/portfolio/projects/",
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

    async def add_gallery_image(self, db: AsyncSession, id: UUID, file: UploadFile):
        obj = await self.get(db, id)
        gallery = list(obj.gallery_images or [])
        if len(gallery) >= MAX_GALLERY_IMAGES:
            raise AppError("GALLERY_LIMIT", f"Maximum {MAX_GALLERY_IMAGES} gallery images allowed", 400)

        data, _, _, _ = await compress_image(file)
        slug = obj.slug or "project"
        result = await imagekit_service.upload(
            data,
            f"{slug}-gallery-{len(gallery) + 1}.webp",
            "/portfolio/projects/gallery/",
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

    async def remove_gallery_image(self, db: AsyncSession, id: UUID, file_id: str):
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


project_service = ProjectService()
