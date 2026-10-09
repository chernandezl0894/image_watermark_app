"""Domain layer: entities and pure watermarking rules."""

from image_watermark_app.domain.models import (
    DEFAULT_OPACITY,
    DEFAULT_POSITION,
    DEFAULT_TEXT,
    MAX_MARGIN_RATIO,
    POSITIONS,
    InvalidImageError,
    WatermarkRequest,
)
from image_watermark_app.domain.watermark import stamp_image

__all__ = [
    "DEFAULT_OPACITY",
    "DEFAULT_POSITION",
    "DEFAULT_TEXT",
    "MAX_MARGIN_RATIO",
    "POSITIONS",
    "InvalidImageError",
    "WatermarkRequest",
    "stamp_image",
]
