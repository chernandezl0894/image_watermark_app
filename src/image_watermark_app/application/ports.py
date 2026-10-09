"""Interfaces (ports) that connect the application to its outer layers."""

from pathlib import Path
from typing import Protocol

from PIL import Image

from image_watermark_app.domain.models import WatermarkRequest


class ImageRepository(Protocol):
    """Loads and persists images; adapters choose formats and encodings.

    Implementations raise ``FileNotFoundError`` for missing files and
    ``InvalidImageError`` for undecodable data on ``load``. ``save`` encodes
    ``image`` to ``path`` adopting the colour model of ``like`` (the source).
    """

    def load(self, path: Path) -> Image.Image: ...

    def save(self, image: Image.Image, path: Path, *, like: Image.Image) -> Path: ...


class WatermarkUseCases(Protocol):
    """The subset of the application the presentation layer depends on."""

    def load(self, path: Path) -> Image.Image: ...

    def apply(self, source: Image.Image, request: WatermarkRequest) -> Image.Image: ...

    def save(
        self,
        source: Image.Image,
        request: WatermarkRequest,
        output_path: Path,
    ) -> Path: ...
