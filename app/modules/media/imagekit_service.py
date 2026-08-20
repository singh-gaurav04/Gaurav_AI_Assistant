import httpx
from app.core.config import settings
from app.core.exceptions import AppError

class ImageKitService:
    base_url = "https://upload.imagekit.io/api/v1/files"

    async def upload(self, data: bytes, filename: str, folder: str) -> dict:
        if not settings.IMAGEKIT_PRIVATE_KEY:
            raise AppError("IMAGEKIT_NOT_CONFIGURED", "Image service is not configured", 503)
        auth = (settings.IMAGEKIT_PRIVATE_KEY, "")
        files = {"file": (filename, data)}
        form = {"fileName": filename, "folder": folder, "useUniqueFileName": "true"}
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(f"{self.base_url}/upload", auth=auth, files=files, data=form)
        if r.status_code >= 400:
            raise AppError("IMAGE_UPLOAD_FAILED", "Image upload failed", 502)
        return r.json()

    async def delete(self, file_id: str) -> None:
        auth = (settings.IMAGEKIT_PRIVATE_KEY, "")
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.delete(f"{self.base_url}/{file_id}", auth=auth)
        if r.status_code >= 400:
            raise AppError("IMAGE_DELETE_FAILED", "Image deletion failed", 502)

imagekit_service = ImageKitService()
