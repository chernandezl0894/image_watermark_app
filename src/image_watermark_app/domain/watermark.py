"""Pure watermarking operations on in-memory images (no file or UI access)."""

from PIL import Image, ImageDraw, ImageFont

from image_watermark_app.domain.models import WatermarkRequest


def stamp_image(image: Image.Image, request: WatermarkRequest) -> Image.Image:
    """Return an RGBA copy of ``image`` with the request's text stamped on it."""
    canvas = image.convert("RGBA")
    width, height = canvas.size
    font_size = max(12, round(min(width, height) * 0.06))
    font = ImageFont.load_default(size=font_size)

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
    draw.text((x, y), request.text, font=font, fill=(255, 255, 255, alpha))

    return Image.alpha_composite(canvas, overlay)


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
