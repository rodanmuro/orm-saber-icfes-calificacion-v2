from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

router = APIRouter(prefix="/assets", tags=["assets"])

BACKEND_DIR = Path(__file__).resolve().parents[4]
ASSETS_DIR = BACKEND_DIR / "data" / "input" / "item_assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}


@router.post("/images")
async def upload_item_image(image: UploadFile = File(...)) -> dict[str, str]:
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PNG, JPEG and WEBP images are supported",
        )

    extension = ALLOWED_CONTENT_TYPES[image.content_type]
    filename = f"{uuid4().hex}{extension}"
    destination = ASSETS_DIR / filename
    content = await image.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty image payload")
    destination.write_bytes(content)

    return {
        "filename": filename,
        "url": f"/assets/item_assets/{filename}",
    }

