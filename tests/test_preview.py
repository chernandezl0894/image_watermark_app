from PIL import Image

from image_watermark_app.presentation import (
    centered_origin,
    fit_within,
    flatten_for_preview,
    point_to_fraction,
)


def test_centered_origin_places_photo_in_the_middle() -> None:
    assert centered_origin((700, 500), (300, 200)) == (200, 150)


def test_centered_origin_handles_tighter_widget() -> None:
    assert centered_origin((100, 80), (300, 200)) == (-100, -60)


def test_point_to_fraction_maps_from_widget_centre() -> None:
    assert point_to_fraction((150, 100), (0, 0), (300, 200)) == (0.5, 0.5)


def test_point_to_fraction_accounts_for_photo_origin() -> None:
    assert point_to_fraction((350, 250), (200, 150), (300, 200)) == (0.5, 0.5)


def test_point_to_fraction_clamps_outside_the_photo() -> None:
    assert point_to_fraction((-50, 999), (0, 0), (300, 200)) == (0.0, 1.0)


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
