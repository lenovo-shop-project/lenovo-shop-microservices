import asyncio
from io import BytesIO
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status
from app.config import settings


MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def _configure_cloudinary() -> None:
    if (
        not settings.cloudinary_cloud_name
        or not settings.cloudinary_api_key
        or not settings.cloudinary_api_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cloudinary не налаштований",
        )

    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


async def upload_image_to_cloudinary(
    file: UploadFile,
    folder: str,
) -> str:
    _configure_cloudinary()

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можна завантажувати лише зображення JPG, PNG або WEBP",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл порожній",
        )

    if len(content) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл занадто великий. Максимальний розмір – 5 MB",
        )

    file_data = BytesIO(content)
    file_data.name = file.filename or "image"

    try:
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            file_data,
            folder=f"lenovo-shop/{folder}",
            resource_type="image",
            use_filename=False,
            unique_filename=True,
            overwrite=False,
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Неможливо завантажити зображення",
        ) from error

    image_url = result.get("secure_url")

    if not image_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cloudinary не повернув посилання на зображення",
        )

    return image_url