from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ImageRecord
from app.schemas import ImageDetailResponse, ImageListItem, ImageListResponse, UploadResponse
from app.services.image_processor import InvalidImageTypeError, create_image_record, process_image

router = APIRouter(prefix="/api/images", tags=["images"])
logger = logging.getLogger(__name__)


@router.post("", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info("Received upload: %s", file.filename)
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    payload = await file.read()
    record = create_image_record(db, file.filename)

    try:
        process_image(db, record.image_id, payload, file.filename)
    except InvalidImageTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "success",
        "data": {
            "image_id": record.image_id,
            "status": db.query(ImageRecord).filter(ImageRecord.image_id == record.image_id).first().status,
        },
        "error": None,
    }


@router.get("", response_model=ImageListResponse)
def list_images(db: Session = Depends(get_db)):
    records = db.query(ImageRecord).order_by(ImageRecord.image_id.desc()).all()
    return {
        "status": "success",
        "data": [
            ImageListItem(
                image_id=r.image_id,
                original_filename=r.original_filename,
                status=r.status,
                processed_at=r.processed_at,
            )
            for r in records
        ],
        "error": None,
    }


@router.get("/{image_id}", response_model=ImageDetailResponse)
def get_image(image_id: str, request: Request, db: Session = Depends(get_db)):
    record = db.query(ImageRecord).filter(ImageRecord.image_id == image_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Image not found")

    if record.status != "success":
        return {"status": record.status, "data": None, "error": record.error_message}

    metadata = json.loads(record.metadata_json or "{}")
    base = str(request.base_url).rstrip("/")
    return {
        "status": "success",
        "data": {
            "image_id": record.image_id,
            "original_name": record.original_filename,
            "processed_at": record.processed_at,
            "metadata": {
                "width": metadata.get("width"),
                "height": metadata.get("height"),
                "format": metadata.get("format"),
                "size_bytes": metadata.get("size_bytes"),
            },
            "thumbnails": {
                "small": f"{base}/api/images/{record.image_id}/thumbnails/small",
                "medium": f"{base}/api/images/{record.image_id}/thumbnails/medium",
            },
            "caption": record.caption,
        },
        "error": None,
    }


@router.get("/{image_id}/thumbnails/{size}")
def get_thumbnail(image_id: str, size: str, db: Session = Depends(get_db)):
    record = db.query(ImageRecord).filter(ImageRecord.image_id == image_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Image not found")
    if size not in {"small", "medium"}:
        raise HTTPException(status_code=400, detail="size must be small or medium")

    thumb_path = record.small_thumbnail_path if size == "small" else record.medium_thumbnail_path
    if not thumb_path or not Path(thumb_path).exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    return FileResponse(thumb_path, media_type="image/jpeg")
