from pathlib import Path

import pytest
from PIL import Image, ImageChops

from image_watermark_app.domain import (
    DEFAULT_COLOR,
    DEFAULT_OPACITY,
    DEFAULT_POSITION,
    DEFAULT_TEXT,
    POSITIONS,
    InvalidImageError,
    WatermarkRequest,
    stamp_image,
)

QUADRANT_ASSERTIONS = {
    "top-left": lambda box, img: box[2] <= img.width // 2 and box[3] <= img.height // 2,
    "top-right": lambda box, img: (
        box[0] >= img.width // 2 and box[3] <= img.height // 2
    ),
    "bottom-left": lambda box, img: (
        box[2] <= img.width // 2 and box[1] >= img.height // 2
    ),
    "center": lambda box, img: (
        box[0] < img.width // 2 < box[2] and box[1] < img.height // 2 < box[3]
    ),
    "bottom-right": lambda box, img: (
        box[0] > img.width // 2 and box[1] > img.height // 2
    ),
}


def make_image(size: tuple[int, int] = (300, 200)) -> Image.Image:
    return Image.new("RGB", size, (30, 60, 90))


def test_request_defaults() -> None:
    request = WatermarkRequest(text=DEFAULT_TEXT)
    assert request.text == "Crissis"
    assert request.opacity == DEFAULT_OPACITY
    assert request.position == DEFAULT_POSITION
    assert request.margin_ratio == 0.03
    assert request.color == DEFAULT_COLOR == "#FFFFFF"
    assert request.font_size is None
    assert request.font_path is None


@pytest.mark.parametrize("text", ["", "   "])
def test_request_rejects_empty_text(text: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        WatermarkRequest(text=text)


@pytest.mark.parametrize("opacity", [-0.1, 1.5])
def test_request_rejects_out_of_range_opacity(opacity: float) -> None:
    with pytest.raises(ValueError, match="Opacity must be"):
        WatermarkRequest(text="Crissis", opacity=opacity)


def test_request_rejects_unknown_position() -> None:
    with pytest.raises(ValueError, match="Unknown position"):
        WatermarkRequest(text="Crissis", position="middle")


@pytest.mark.parametrize("margin", [-0.01, 0.9])
def test_request_rejects_out_of_range_margin(margin: float) -> None:
    with pytest.raises(ValueError, match="Margin ratio must be"):
        WatermarkRequest(text="Crissis", margin_ratio=margin)


@pytest.mark.parametrize("color", ["red", "#FFF", "#GGGGGG", "ffffff", "#1234567", ""])
def test_request_rejects_invalid_color(color: str) -> None:
    with pytest.raises(ValueError, match="Color must be"):
        WatermarkRequest(text="Crissis", color=color)


@pytest.mark.parametrize("font_size", [0, -5])
def test_request_rejects_non_positive_font_size(font_size: int) -> None:
    with pytest.raises(ValueError, match="Font size must be"):
        WatermarkRequest(text="Crissis", font_size=font_size)


def test_request_accepts_minimal_font_size() -> None:
    assert WatermarkRequest(text="Crissis", font_size=1).font_size == 1


def test_invalid_image_error_is_a_value_error() -> None:
    assert issubclass(InvalidImageError, ValueError)


def test_stamp_returns_marked_rgba_copy() -> None:
    original = make_image()
    marked = stamp_image(original, WatermarkRequest(text=DEFAULT_TEXT))
    assert marked.mode == "RGBA"
    assert marked.size == original.size
    assert ImageChops.difference(original, marked.convert("RGB")).getbbox() is not None


def test_stamp_does_not_mutate_original() -> None:
    original = make_image()
    pristine = make_image()
    stamp_image(original, WatermarkRequest(text=DEFAULT_TEXT))
    assert ImageChops.difference(original, pristine).getbbox() is None


@pytest.mark.parametrize("position", list(POSITIONS))
def test_stamp_places_text_in_expected_area(position: str) -> None:
    original = make_image()
    marked = stamp_image(
        original, WatermarkRequest(text=DEFAULT_TEXT, position=position)
    )
    diff = ImageChops.difference(original, marked.convert("RGB")).getbbox()
    assert diff is not None
    assert QUADRANT_ASSERTIONS[position](diff, original)


def test_stamp_applies_requested_color() -> None:
    original = make_image()
    marked = stamp_image(
        original,
        WatermarkRequest(text="X", opacity=1.0, color="#FF0000", font_size=60),
    )
    colors = marked.getcolors(maxcolors=marked.width * marked.height)
    assert colors is not None
    assert any(pixel == (255, 0, 0, 255) for _, pixel in colors)


def test_stamp_font_size_controls_text_scale() -> None:
    original = make_image()
    small = stamp_image(original, WatermarkRequest(text=DEFAULT_TEXT, font_size=12))
    large = stamp_image(original, WatermarkRequest(text=DEFAULT_TEXT, font_size=60))
    small_diff = ImageChops.difference(original, small.convert("RGB")).getbbox()
    large_diff = ImageChops.difference(original, large.convert("RGB")).getbbox()
    assert small_diff is not None
    assert large_diff is not None
    small_area = (small_diff[2] - small_diff[0]) * (small_diff[3] - small_diff[1])
    large_area = (large_diff[2] - large_diff[0]) * (large_diff[3] - large_diff[1])
    assert large_area > small_area


def test_stamp_falls_back_when_font_file_missing(tmp_path: Path) -> None:
    original = make_image()
    request = WatermarkRequest(text=DEFAULT_TEXT, font_path=tmp_path / "nope.ttf")
    marked = stamp_image(original, request)
    assert marked.mode == "RGBA"
    diff = ImageChops.difference(original, marked.convert("RGB")).getbbox()
    assert diff is not None


DEJAVU_FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


@pytest.mark.skipif(not DEJAVU_FONT.is_file(), reason="DejaVu font not installed")
def test_stamp_renders_with_custom_ttf() -> None:
    original = make_image()
    with_font = stamp_image(
        original,
        WatermarkRequest(text=DEFAULT_TEXT, font_size=40, font_path=DEJAVU_FONT),
    )
    default_font = stamp_image(
        original, WatermarkRequest(text=DEFAULT_TEXT, font_size=40)
    )
    diff = ImageChops.difference(with_font.convert("RGB"), default_font.convert("RGB"))
    assert diff.getbbox() is not None


def test_stamp_honours_opacity_extremes() -> None:
    original = make_image()
    invisible = stamp_image(original, WatermarkRequest(text=DEFAULT_TEXT, opacity=0.0))
    assert ImageChops.difference(original, invisible.convert("RGB")).getbbox() is None

    strong = stamp_image(original, WatermarkRequest(text=DEFAULT_TEXT, opacity=1.0))
    assert ImageChops.difference(original, strong.convert("RGB")).getbbox() is not None
