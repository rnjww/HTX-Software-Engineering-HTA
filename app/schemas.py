from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class MetadataSchema(BaseModel):
    width: int
    height: int
    format: str
    size_bytes: int

class ThumbnailSchema(BaseModel):
    small: str
    medium: str

class ImageDataSchema(BaseModel):
    image_id: str
    original_name: str
    processed_at: str | None
    metadata: MetadataSchema | None
    thumbnails: ThumbnailSchema | None
    caption: str | None

class ImageDetailResponse(BaseModel):
    status: str
    data: ImageDataSchema | None
    error: str | None

class ImageListItem(BaseModel):
    image_id: str
    original_filename: str
    status: str
    processed_at: str | None

class ImageListResponse(BaseModel):
    status: str
    data: list[ImageListItem]
    error: str | None

class UploadResponse(BaseModel):
    status: str
    data: dict[str, Any]
    error: str | None

class StatsResponse(BaseModel):
    status: str
    data: dict[str, Any]
    error: str | None
