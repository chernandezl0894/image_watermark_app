"""Pure watermarking operations on in-memory images (no file or UI access)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from image_watermark_app.domain.models import WatermarkRequest


def stamp_image(image: Image.Image, request: WatermarkRequest) -> Image.Image:
    """Return an RGBA copy of ``image`` with the request's text stamped on it."""
    canvas = image.convert("RGBA")
    width, height = canvas.size
    font_size = (
        request.font_size
        if request.font_size is not None
        else max(12, round(min(width, height) * 0.06))
    )
    font = _load_font(font_size, request.font_path)

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    left, top, right, bottom = (
        int(value) for value in draw.textbbox((0, 0), request.text, font=font)
    )
    text_width = right - left
    text_height = bottom - top
    margin = round(min(width, height) * request.margin_ratio)

    x, y = _coordinates(
        request.position,
        width,
        height,
        text_width,
        text_height,
        margin,
        (left, top),
    )
    alpha = round(request.opacity * 255)
    red, green, blue = _parse_hex_color(request.color)
    draw.text((x, y), request.text, font=font, fill=(red, green, blue, alpha))

    return Image.alpha_composite(canvas, overlay)


def _load_font(
    font_size: int, font_path: Path | None
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if font_path is not None:
        try:
            return ImageFont.truetype(str(font_path), font_size)
        except OSError:
            pass
    return ImageFont.load_default(size=font_size)


def _parse_hex_color(color: str) -> tuple[int, int, int]:
    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)


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
    return (width - text_width) // 2 - offset_x, (height - text_height) // 2 - offset_y
