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
