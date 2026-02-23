from __future__ import annotations
from sqlalchemy import Column, Float, String, Text
from app.database import Base


class ImageRecord(Base):
    __tablename__ = "images"

    image_id = Column(String, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    status = Column(String, nullable=False, default="processing")
    processed_at = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    small_thumbnail_path = Column(String, nullable=True)
    medium_thumbnail_path = Column(String, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
