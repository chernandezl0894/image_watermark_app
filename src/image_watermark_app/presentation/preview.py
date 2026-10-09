"""Pure helpers that prepare images for on-screen preview."""

from PIL import Image


def fit_within(image: Image.Image, bounds: tuple[int, int]) -> Image.Image:
    """Return a copy of ``image`` scaled down to fit inside ``bounds``."""
    fitted = image.copy()
    fitted.thumbnail(bounds, Image.Resampling.LANCZOS)
    return fitted


def flatten_for_preview(image: Image.Image) -> Image.Image:
    """Convert any image to RGB for display, compositing alpha over white."""
    if image.mode == "RGB":
        return image
    rgba = image.convert("RGBA")
    background = Image.new("RGB", rgba.size, (255, 255, 255))
    background.paste(rgba, mask=rgba.getchannel("A"))
    return background


def centered_origin(
    widget_size: tuple[int, int], photo_size: tuple[int, int]
) -> tuple[int, int]:
    """Return the upper-left corner of ``photo_size`` centered in ``widget_size``."""
    return (
        (widget_size[0] - photo_size[0]) // 2,
        (widget_size[1] - photo_size[1]) // 2,
    )


def point_to_fraction(
    point: tuple[int, int],
    origin: tuple[int, int],
    photo_size: tuple[int, int],
) -> tuple[float, float]:
    """Map a widget point to image fractions in ``[0, 1]``, clamped at the edges.

    The preview keeps the source aspect ratio, so the fraction along each axis
    is the same on the photo as on the full-size image.
    """
    px, py = point
    ox, oy = origin
    width, height = photo_size
    fx = 0.0 if width <= 0 else min(1.0, max(0.0, (px - ox) / width))
    fy = 0.0 if height <= 0 else min(1.0, max(0.0, (py - oy) / height))
    return fx, fy
