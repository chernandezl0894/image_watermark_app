"""Generate the application icon assets (icon.png and icon.ico).

Usage::

    uv run python scripts/generate_icon.py

The design is fully deterministic: a blue rounded square with a photo glyph
(sun + mountains) under a translucent diagonal band, like a watermark.
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent / "src" / "image_watermark_app" / "assets"
)
ICON_SIZE = 256
ICO_SIZES = [
    (16, 16),
    (24, 24),
    (32, 32),
    (48, 48),
    (64, 64),
    (128, 128),
    (256, 256),
]
GRADIENT_TOP = (30, 64, 179)
GRADIENT_BOTTOM = (59, 130, 246)
WHITE = (255, 255, 255, 255)
FRAME = (255, 255, 255, 70)
BAND = (255, 255, 255, 45)


def _rounded_gradient() -> Image.Image:
    """Vertical gradient clipped to a rounded square."""
    gradient = Image.new("RGBA", (ICON_SIZE, ICON_SIZE))
    for y in range(ICON_SIZE):
        t = y / (ICON_SIZE - 1)
        red = int(GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * t)
        green = int(GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * t)
        blue = int(GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * t)
        gradient.paste((red, green, blue, 255), (0, y, ICON_SIZE, y + 1))
    mask = Image.new("L", (ICON_SIZE, ICON_SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle((6, 6, 250, 250), radius=54, fill=255)
    gradient.putalpha(mask)
    return gradient


def build_icon() -> Image.Image:
    """Draw the 256x256 RGBA icon."""
    canvas = _rounded_gradient()

    glyph = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    glyph_draw = ImageDraw.Draw(glyph)
    glyph_draw.rounded_rectangle((26, 26, 230, 230), radius=38, outline=FRAME, width=5)
    glyph_draw.ellipse((54, 52, 106, 104), fill=WHITE)
    glyph_draw.polygon((40, 214, 108, 118, 152, 168, 190, 108, 222, 214), fill=WHITE)
    canvas = Image.alpha_composite(canvas, glyph)

    band = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(band).polygon((0, 158, 256, 66, 256, 118, 0, 210), fill=BAND)
    band.putalpha(ImageChops.multiply(band.getchannel("A"), canvas.getchannel("A")))
    return Image.alpha_composite(canvas, band)


def main() -> None:
    """Write icon.png and icon.ico into the package assets directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    icon = build_icon()
    icon.save(OUTPUT_DIR / "icon.png", format="PNG")
    icon.save(OUTPUT_DIR / "icon.ico", format="ICO", sizes=ICO_SIZES)
    print(f"Icons written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
