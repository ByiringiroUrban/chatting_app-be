import os
import aiofiles
import asyncio
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import cloudinary
import cloudinary.uploader
from app.config import settings

# Initialize Cloudinary SDK
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

router = APIRouter(prefix="/upload", tags=["Media & File Uploads"])

def _upload_to_cloudinary(content: bytes, filename: str, content_type: str) -> dict:
    """
    Synchronous Cloudinary uploader invoked via asyncio.to_thread.
    Automatically assigns appropriate resource_type (image, video, raw).
    """
    ext = os.path.splitext(filename)[1].lower() if filename else ""
    timestamp = int(datetime.utcnow().timestamp() * 1000)
    base_name = os.path.splitext(filename)[0].replace(" ", "_") if filename else "upload"
    public_id = f"muraho_{timestamp}_{base_name}"

    # Determine resource_type for Cloudinary
    if content_type.startswith("image/") or ext in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"]:
        resource_type = "image"
    elif content_type.startswith("video/") or ext in [".mp4", ".mov", ".avi", ".mkv"]:
        resource_type = "video"
    else:
        # Audio voice notes (.webm, .ogg, .mp3, .wav) and documents (.pdf, .docx, .zip)
        resource_type = "raw"

    try:
        return cloudinary.uploader.upload(
            content,
            resource_type=resource_type,
            public_id=public_id,
            folder="muraho_chat_media",
            overwrite=True
        )
    except Exception as e:
        # If specific type fails, try 'raw' as universal binary storage
        if resource_type != "raw":
            return cloudinary.uploader.upload(
                content,
                resource_type="raw",
                public_id=public_id,
                folder="muraho_chat_media",
                overwrite=True
            )
        raise e

from app.models.user import User
from app.core.dependencies import get_current_user

@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Handles authenticated upload of photos, audio voice notes, videos, documents to Cloudinary."""
    try:
        content = await file.read()
        clean_name = file.filename.replace(" ", "_") if file.filename else "file"
        content_type = file.content_type or "application/octet-stream"

        # 1. Primary: Upload to Cloudinary
        try:
            cloud_res = await asyncio.to_thread(_upload_to_cloudinary, content, clean_name, content_type)
            secure_url = cloud_res.get("secure_url") or cloud_res.get("url")

            return {
                "success": True,
                "filename": clean_name,
                "url": secure_url,
                "publicId": cloud_res.get("public_id"),
                "size": cloud_res.get("bytes", len(content)),
                "contentType": content_type,
                "storage": "cloudinary",
                "format": cloud_res.get("format")
            }
        except Exception as cloud_err:
            print(f"[Muraho Cloudinary] Warning: Cloud upload failed ({cloud_err}), saving local backup.")
            
            # 2. Resilient Fallback: Local upload directory
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            timestamp = int(datetime.utcnow().timestamp() * 1000)
            filename = f"{timestamp}_{clean_name}"
            file_path = os.path.join(settings.UPLOAD_DIR, filename)

            async with aiofiles.open(file_path, "wb") as out_file:
                await out_file.write(content)

            return {
                "success": True,
                "filename": clean_name,
                "url": f"/uploads/{filename}",
                "size": len(content),
                "contentType": content_type,
                "storage": "local"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

