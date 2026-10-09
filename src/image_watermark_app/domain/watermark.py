"""Pure watermarking operations on in-memory images (no file or UI access)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from image_watermark_app.domain.models import CUSTOM_POSITION, WatermarkRequest

FILL = tuple[int, int, int, int]


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
    alpha = round(request.opacity * 255)
    red, green, blue = _parse_hex_color(request.color)
    tile = _render_tile(request.text, font, (red, green, blue, alpha), request.rotation)

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    if request.tiled:
        _stamp_tiled(overlay, tile, request, width, height)
    else:
        x, y = _placement(request, width, height, tile.size)
        _paste_tile(overlay, tile, x, y)

    return Image.alpha_composite(canvas, overlay)


def _render_tile(
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: FILL,
    rotation: float,
) -> Image.Image:
    """Render ``text`` into a tight RGBA tile, rotated counter-clockwise if asked."""
    scratch = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    left, top, right, bottom = (
        int(value) for value in scratch.textbbox((0, 0), text, font=font)
    )
    tile = Image.new("RGBA", (max(1, right - left), max(1, bottom - top)), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((-left, -top), text, font=font, fill=fill)
    if rotation:
        tile = tile.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=True)
    return tile


def _placement(
    request: WatermarkRequest,
    width: int,
    height: int,
    tile_size: tuple[int, int],
) -> tuple[int, int]:
    tile_width, tile_height = tile_size
    if request.position == CUSTOM_POSITION:
        assert request.x is not None and request.y is not None  # domain invariant
        return (
            round(request.x * width) - tile_width // 2,
            round(request.y * height) - tile_height // 2,
        )
    margin = round(min(width, height) * request.margin_ratio)
    return _coordinates(
        request.position, width, height, tile_width, tile_height, margin
    )


def _stamp_tiled(
    overlay: Image.Image,
    tile: Image.Image,
    request: WatermarkRequest,
    width: int,
    height: int,
) -> None:
    """Repeat ``tile`` in a grid across the whole canvas, panned by custom x/y."""
    gap = round(min(width, height) * request.tile_gap)
    stride_x = tile.width + gap
    stride_y = tile.height + gap
    origin_x = origin_y = 0
    if request.position == CUSTOM_POSITION:
        assert request.x is not None and request.y is not None  # domain invariant
        origin_x = round(request.x * width)
        origin_y = round(request.y * height)
    start_x = origin_x % stride_x - stride_x
    start_y = origin_y % stride_y - stride_y
    y = start_y
    while y < height:
        x = start_x
        while x < width:
            _paste_tile(overlay, tile, x, y)
            x += stride_x
        y += stride_y


def _paste_tile(overlay: Image.Image, tile: Image.Image, x: int, y: int) -> None:
    """Composite ``tile`` at ``(x, y)``, clipping anything outside the canvas."""
    left = max(0, -x)
    top = max(0, -y)
    right = min(tile.width, overlay.width - x)
    bottom = min(tile.height, overlay.height - y)
    if left >= right or top >= bottom:
        return
    piece = tile.crop((left, top, right, bottom))
    overlay.alpha_composite(piece, dest=(x + left, y + top))


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
) -> tuple[int, int]:
    if position == "top-left":
        return margin, margin
    if position == "top-right":
        return width - text_width - margin, margin
    if position == "bottom-left":
        return margin, height - text_height - margin
    if position == "bottom-right":
        return width - text_width - margin, height - text_height - margin
    return (width - text_width) // 2, (height - text_height) // 2
