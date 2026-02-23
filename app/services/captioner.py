from __future__ import annotations

import logging
import os
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)


class CaptionerService:
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-large") -> None:
        self.model_name = model_name
        self.processor = None
        self.model = None
        self._enabled = False

    def load(self) -> None:
        if os.getenv("DISABLE_CAPTION_MODEL", "0") == "1":
            logger.warning("Caption model loading disabled by environment variable")
            return
        try:
            from transformers import BlipForConditionalGeneration, BlipProcessor

            self.processor = BlipProcessor.from_pretrained(self.model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)
            self._enabled = True
            logger.info("Loaded captioning model: %s", self.model_name)
        except Exception as exc:  # pragma: no cover - graceful fallback path
            logger.exception("Failed to load caption model: %s", exc)
            self._enabled = False

    def caption_from_path(self, image_path: Path) -> str:
        if not self._enabled:
            return "Caption unavailable"

        try:
            with Image.open(image_path).convert("RGB") as raw_image:
                inputs = self.processor(images=raw_image, return_tensors="pt")
                generated_ids = self.model.generate(**inputs, max_new_tokens=40)
                return self.processor.decode(generated_ids[0], skip_special_tokens=True)
        except Exception as exc:
            logger.exception("Caption generation failed for %s: %s", image_path, exc)
            return "Caption unavailable"


captioner_service = CaptionerService()
