from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import ExifTags, Image
from sqlalchemy.orm import Session

from app.models import ImageRecord
from app.services.captioner import captioner_service

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
IMAGE_ROOT = Path("storage")
ORIGINAL_DIR = IMAGE_ROOT / "originals"
THUMB_DIR = IMAGE_ROOT / "thumbnails"


class InvalidImageTypeError(Exception):
    pass


def ensure_storage() -> None:
    ORIGINAL_DIR.mkdir(parents=True, exist_ok=True)
    THUMB_DIR.mkdir(parents=True, exist_ok=True)


def create_image_record(db: Session, original_filename: str) -> ImageRecord:
    image_id = f"img_{uuid.uuid4().hex[:12]}"
    record = ImageRecord(
        image_id=image_id,
        original_filename=original_filename,
        status="processing",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _extract_exif_data(image: Image.Image) -> dict[str, str]:
    exif_data: dict[str, str] = {}
    raw_exif = image.getexif()
    if not raw_exif:
        return exif_data

    for tag_id, value in raw_exif.items():
        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
        exif_data[tag_name] = str(value)
    return exif_data


def process_image(db: Session, image_id: str, file_bytes: bytes, filename: str) -> None:
    ensure_storage()
    started = datetime.now(timezone.utc)

    record = db.query(ImageRecord).filter(ImageRecord.image_id == image_id).first()
    if record is None:
        logger.error("Image record %s missing before processing", image_id)
        return

    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        record.status = "failed"
        record.error_message = "Only JPG and PNG files are allowed"
        db.commit()
        raise InvalidImageTypeError(record.error_message)

    original_path = ORIGINAL_DIR / f"{image_id}{suffix}"
    small_path = THUMB_DIR / f"{image_id}_small.jpg"
    medium_path = THUMB_DIR / f"{image_id}_medium.jpg"

    try:
        original_path.write_bytes(file_bytes)

        with Image.open(original_path) as img:
            rgb_img = img.convert("RGB")
            width, height = rgb_img.size
            img_format = (img.format or suffix.replace(".", "")).lower()
            exif = _extract_exif_data(img)

            small = rgb_img.copy()
            small.thumbnail((128, 128))
            small.save(small_path, format="JPEG", quality=85)

            medium = rgb_img.copy()
            medium.thumbnail((512, 512))
            medium.save(medium_path, format="JPEG", quality=90)

        caption = captioner_service.caption_from_path(original_path)
        processed_at = datetime.now(timezone.utc).isoformat()
        duration = (datetime.now(timezone.utc) - started).total_seconds()

        metadata = {
            "width": width,
            "height": height,
            "format": img_format,
            "size_bytes": len(file_bytes),
            "processed_at": processed_at,
            "exif": exif,
        }

        record.status = "success"
        record.processed_at = processed_at
        record.metadata_json = json.dumps(metadata)
        record.caption = caption
        record.small_thumbnail_path = str(small_path)
        record.medium_thumbnail_path = str(medium_path)
        record.processing_time_seconds = duration
        record.error_message = None
        db.commit()

        logger.info("Processed image %s in %.4fs", image_id, duration)
    except Exception as exc:
        logger.exception("Image processing failed for %s: %s", image_id, exc)
        record.status = "failed"
        record.error_message = "Processing failed"
        record.processing_time_seconds = (datetime.now(timezone.utc) - started).total_seconds()
        db.commit()
