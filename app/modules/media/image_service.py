from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError
from fastapi import UploadFile
from app.core.config import settings
from app.core.exceptions import AppError

ALLOWED = {"image/jpeg", "image/png", "image/webp"}

async def compress_image(file: UploadFile) -> tuple[bytes, str, int, int]:
    raw = await file.read()
    if len(raw) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise AppError("IMAGE_TOO_LARGE", "Image exceeds upload size limit", 413)
    if file.content_type not in ALLOWED:
        raise AppError("INVALID_IMAGE_TYPE", "Unsupported image type", 415)
    try:
        Image.MAX_IMAGE_PIXELS = settings.MAX_IMAGE_WIDTH * settings.MAX_IMAGE_HEIGHT * 4
        with Image.open(BytesIO(raw)) as img:
            img.verify()
        with Image.open(BytesIO(raw)) as img:
            img = ImageOps.exif_transpose(img)
            img.thumbnail((settings.MAX_IMAGE_WIDTH, settings.MAX_IMAGE_HEIGHT))
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            out = BytesIO()
            img.save(out, "WEBP", quality=settings.IMAGE_QUALITY, method=6)
            return out.getvalue(), "image/webp", img.width, img.height
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise AppError("INVALID_IMAGE", "Invalid or corrupted image", 400)
