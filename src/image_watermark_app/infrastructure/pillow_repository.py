"""Pillow-backed implementation of the image repository port."""

from pathlib import Path

from PIL import Image, UnidentifiedImageError

from image_watermark_app.domain.models import InvalidImageError

_ALPHA_FORMATS = frozenset({".png", ".webp", ".tif", ".tiff"})


class PillowImageRepository:
    """Reads and writes images with Pillow, preserving the source colour model."""

    def load(self, path: Path) -> Image.Image:
        if not path.is_file():
            raise FileNotFoundError(f"Input image not found: {path}")
        try:
            with Image.open(path) as opened:
                return opened.copy()
        except (UnidentifiedImageError, OSError) as exc:
            raise InvalidImageError(f"Not a valid image file: {path}") from exc

    def save(self, image: Image.Image, path: Path, *, like: Image.Image) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        has_alpha = like.mode in {"RGBA", "LA", "PA"} or "transparency" in like.info
        _encode(image, path=path, source_mode=like.mode, has_alpha=has_alpha).save(path)
        return path


def _encode(
    image: Image.Image,
    *,
    path: Path,
    source_mode: str,
    has_alpha: bool,
) -> Image.Image:
    if not has_alpha:
        return image.convert("L" if source_mode == "L" else "RGB")
    if path.suffix.lower() not in _ALPHA_FORMATS:
        return image.convert("RGB")
    return image
