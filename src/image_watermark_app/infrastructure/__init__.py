"""Infrastructure layer: concrete adapters for the application ports."""

from image_watermark_app.infrastructure.pillow_repository import PillowImageRepository

__all__ = ["PillowImageRepository"]
