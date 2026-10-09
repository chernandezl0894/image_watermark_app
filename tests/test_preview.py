from PIL import Image

from image_watermark_app.presentation import fit_within, flatten_for_preview


def test_fit_within_scales_down() -> None:
    image = Image.new("RGB", (1000, 800))
    fitted = fit_within(image, (640, 420))
    assert fitted.size == (525, 420)
    assert fitted.width <= 640 and fitted.height <= 420


def test_fit_within_keeps_small_images() -> None:
    image = Image.new("RGB", (100, 50))
    assert fit_within(image, (640, 420)).size == (100, 50)


def test_flatten_keeps_rgb() -> None:
    image = Image.new("RGB", (10, 10), (1, 2, 3))
    assert flatten_for_preview(image).mode == "RGB"


def test_flatten_composites_alpha_over_white() -> None:
    image = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    flattened = flatten_for_preview(image)
    assert flattened.mode == "RGB"
    assert flattened.getpixel((5, 5)) == (255, 255, 255)
