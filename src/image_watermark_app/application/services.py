"""Use cases: load an image, apply a watermark, save the result."""

from pathlib import Path

from PIL import Image

from image_watermark_app.application.ports import ImageRepository
from image_watermark_app.domain.models import WatermarkRequest
from image_watermark_app.domain.watermark import stamp_image


class WatermarkService:
    """Orchestrates the domain and the image repository (SOLID: single job)."""

    def __init__(self, repository: ImageRepository) -> None:
        self._repository = repository

    def load(self, path: Path) -> Image.Image:
        return self._repository.load(path)

    def apply(self, source: Image.Image, request: WatermarkRequest) -> Image.Image:
        return stamp_image(source, request)

    def save(
        self,
        source: Image.Image,
        request: WatermarkRequest,
        output_path: Path,
    ) -> Path:
        marked = stamp_image(source, request)
        return self._repository.save(marked, output_path, like=source)

    def watermark_file(
        self,
        input_path: Path,
        output_path: Path,
        request: WatermarkRequest,
    ) -> Path:
        return self.save(self.load(input_path), request, output_path)
