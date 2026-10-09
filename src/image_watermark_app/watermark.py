"""Core watermarking logic built on Pillow."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

DEFAULT_TEXT = "Crissis"
DEFAULT_OPACITY = 0.5
DEFAULT_POSITION = "bottom-right"

POSITIONS = ("top-left", "top-right", "bottom-left", "bottom-right", "center")

_ALPHA_FORMATS = {".png", ".webp", ".tif", ".tiff"}


class InvalidImageError(ValueError):
    """Raised when the input file cannot be decoded as an image."""


def add_watermark(
    input_path: str | Path,
    output_path: str | Path,
    text: str,
    *,
    opacity: float = DEFAULT_OPACITY,
    position: str = DEFAULT_POSITION,
    margin_ratio: float = 0.03,
) -> Path:
    """Stamp ``text`` over the image at ``input_path`` and save it to ``output_path``.

    The text is rendered semi-transparent white using ``opacity`` (0.0 to 1.0)
    and placed at ``position``. Returns the path where the image was written.
    """
    _validate_text(text)
    _validate_opacity(opacity)
    _validate_position(position)

    source = Path(input_path)
    if not source.is_file():
        raise FileNotFoundError(f"Input image not found: {source}")

    try:
        with Image.open(source) as opened:
            image = opened.copy()
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidImageError(f"Not a valid image file: {source}") from exc

    return save_stamped(
        image,
        output_path,
        text,
        opacity=opacity,
        position=position,
        margin_ratio=margin_ratio,
    )


def stamp_image(
    image: Image.Image,
    text: str,
    *,
    opacity: float = DEFAULT_OPACITY,
    position: str = DEFAULT_POSITION,
    margin_ratio: float = 0.03,
) -> Image.Image:
    """Return an RGBA copy of ``image`` with ``text`` stamped on it."""
    _validate_text(text)
    _validate_opacity(opacity)
    _validate_position(position)
    return _stamp(
        image.convert("RGBA"),
        text,
        opacity=opacity,
        position=position,
        margin_ratio=margin_ratio,
    )


def save_stamped(
    image: Image.Image,
    output_path: str | Path,
    text: str,
    *,
    opacity: float = DEFAULT_OPACITY,
    position: str = DEFAULT_POSITION,
    margin_ratio: float = 0.03,
) -> Path:
    """Stamp ``text`` on an in-memory ``image`` and save it to ``output_path``.

    Returns the path where the image was written.
    """
    source_mode = image.mode
    has_alpha = source_mode in {"RGBA", "LA", "PA"} or "transparency" in image.info
    marked = stamp_image(
        image,
        text,
        opacity=opacity,
        position=position,
        margin_ratio=margin_ratio,
    )

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    marked = _match_output_mode(
        marked,
        source_mode=source_mode,
        has_alpha=has_alpha,
        suffix=destination.suffix.lower(),
    )
    marked.save(destination)
    return destination


def _validate_text(text: str) -> None:
    if not text or not text.strip():
        raise ValueError("Watermark text must not be empty")


def _validate_opacity(opacity: float) -> None:
    if not 0.0 <= opacity <= 1.0:
        raise ValueError(f"Opacity must be between 0.0 and 1.0, got {opacity}")


def _validate_position(position: str) -> None:
    if position not in POSITIONS:
        raise ValueError(f"Unknown position {position!r}; choose one of {POSITIONS}")


def _match_output_mode(
    marked: Image.Image,
    *,
    source_mode: str,
    has_alpha: bool,
    suffix: str,
) -> Image.Image:
    """Keep the source colorspace, dropping alpha when the format cannot store it."""
    if not has_alpha:
        return marked.convert("L" if source_mode == "L" else "RGB")
    if suffix not in _ALPHA_FORMATS:
        return marked.convert("RGB")
    return marked


def _stamp(
    image: Image.Image,
    text: str,
    *,
    opacity: float,
    position: str,
    margin_ratio: float,
) -> Image.Image:
    width, height = image.size
    font_size = max(12, round(min(width, height) * 0.06))
    font = ImageFont.load_default(size=font_size)

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    left, top, right, bottom = (
        int(value) for value in draw.textbbox((0, 0), text, font=font)
    )
    text_width = right - left
    text_height = bottom - top
    margin = round(min(width, height) * margin_ratio)

    x, y = _coordinates(
        position, width, height, text_width, text_height, margin, (left, top)
    )
    alpha = round(opacity * 255)
    draw.text((x, y), text, font=font, fill=(255, 255, 255, alpha))

    return Image.alpha_composite(image, overlay)


def _coordinates(
    position: str,
    width: int,
    height: int,
    text_width: int,
    text_height: int,
    margin: int,
    text_origin: tuple[int, int],
) -> tuple[int, int]:
    offset_x, offset_y = text_origin
    if position == "top-left":
        return margin - offset_x, margin - offset_y
    if position == "top-right":
        return width - text_width - margin - offset_x, margin - offset_y
    if position == "bottom-left":
        return margin - offset_x, height - text_height - margin - offset_y
    if position == "bottom-right":
        return (
            width - text_width - margin - offset_x,
            height - text_height - margin - offset_y,
        )
    # center
    return (width - text_width) // 2 - offset_x, (height - text_height) // 2 - offset_y
