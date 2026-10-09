"""Domain layer: entities and pure watermarking rules."""

from image_watermark_app.domain.models import (
    CUSTOM_POSITION,
    DEFAULT_COLOR,
    DEFAULT_OPACITY,
    DEFAULT_POSITION,
    DEFAULT_ROTATION,
    DEFAULT_TEXT,
    DEFAULT_TILE_GAP,
    MAX_MARGIN_RATIO,
    POSITION_CHOICES,
    POSITIONS,
    InvalidImageError,
    WatermarkRequest,
)
from image_watermark_app.domain.watermark import stamp_image

__all__ = [
    "CUSTOM_POSITION",
    "DEFAULT_COLOR",
    "DEFAULT_OPACITY",
    "DEFAULT_POSITION",
    "DEFAULT_ROTATION",
    "DEFAULT_TEXT",
    "DEFAULT_TILE_GAP",
    "MAX_MARGIN_RATIO",
    "POSITIONS",
    "POSITION_CHOICES",
    "InvalidImageError",
    "WatermarkRequest",
    "stamp_image",
]
