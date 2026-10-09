from pathlib import Path

import pytest
from PIL import Image, ImageChops

from image_watermark_app.watermark import (
    DEFAULT_TEXT,
    POSITIONS,
    InvalidImageError,
    add_watermark,
)


def make_image(path: Path, size: tuple[int, int] = (300, 200)) -> Path:
    """Create a solid dark test image."""
    Image.new("RGB", size, (30, 60, 90)).save(path)
    return path


def test_output_file_exists(tmp_path: Path) -> None:
    source = make_image(tmp_path / "in.png")
    result = add_watermark(source, tmp_path / "out.png", "Crissis")
    assert result == tmp_path / "out.png"
    assert result.is_file()


def test_dimensions_are_preserved(tmp_path: Path) -> None:
    source = make_image(tmp_path / "in.png", size=(320, 140))
    result = add_watermark(source, tmp_path / "out.png", "Crissis")
    with Image.open(source) as source_img, Image.open(result) as marked:
        assert marked.size == source_img.size


def test_pixels_are_changed(tmp_path: Path) -> None:
    source = make_image(tmp_path / "in.png")
    result = add_watermark(source, tmp_path / "out.png", "Crissis")
    with Image.open(source) as original, Image.open(result) as marked:
        assert ImageChops.difference(
            original.convert("RGB"), marked.convert("RGB")
        ).getbbox()


def test_watermark_lands_in_bottom_right(tmp_path: Path) -> None:
    source = make_image(tmp_path / "in.png")
    result = add_watermark(source, tmp_path / "out.png", "Crissis")
    with Image.open(source) as original, Image.open(result) as marked:
        diff = ImageChops.difference(original, marked.convert("RGB")).getbbox()
        assert diff is not None
        left, top, right, bottom = diff
        assert left > original.width // 2
        assert top > original.height // 2
        assert right <= original.width
        assert bottom <= original.height


@pytest.mark.parametrize(
    ("position", "quadrant"),
    [
        ("top-left", "top-left"),
        ("top-right", "top-right"),
        ("bottom-left", "bottom-left"),
        ("center", "center"),
    ],
)
def test_position_moves_watermark(tmp_path: Path, position: str, quadrant: str) -> None:
    source = make_image(tmp_path / "in.png")
    result = add_watermark(source, tmp_path / "out.png", "Crissis", position=position)
    with Image.open(source) as original, Image.open(result) as marked:
        diff = ImageChops.difference(original, marked.convert("RGB")).getbbox()
        assert diff is not None
        left, top, right, bottom = diff
        center_x, center_y = original.width / 2, original.height / 2
        if quadrant == "top-left":
            assert right <= center_x and bottom <= center_y
        elif quadrant == "top-right":
            assert left >= center_x and bottom <= center_y
        elif quadrant == "bottom-left":
            assert right <= center_x and top >= center_y
        else:
            assert left < center_x < right
            assert top < center_y < bottom


def test_jpeg_output_is_rgb(tmp_path: Path) -> None:
    source = make_image(tmp_path / "in.png")
    result = add_watermark(source, tmp_path / "out.jpg", "Crissis")
    with Image.open(result) as marked:
        assert marked.format == "JPEG"
        assert marked.mode == "RGB"


def test_png_from_rgb_source_stays_rgb(tmp_path: Path) -> None:
    source = make_image(tmp_path / "in.png")
    result = add_watermark(source, tmp_path / "out.png", "Crissis")
    with Image.open(result) as marked:
        assert marked.mode == "RGB"


def test_png_from_rgba_source_keeps_alpha(tmp_path: Path) -> None:
    source = tmp_path / "in.png"
    Image.new("RGBA", (200, 100), (30, 60, 90, 200)).save(source)
    result = add_watermark(source, tmp_path / "out.png", "Crissis")
    with Image.open(result) as marked:
        assert marked.mode == "RGBA"


def test_grayscale_output_stays_grayscale(tmp_path: Path) -> None:
    source = tmp_path / "in.png"
    Image.new("L", (200, 100), 60).save(source)
    result = add_watermark(source, tmp_path / "out.png", "Crissis")
    with Image.open(result) as marked:
        assert marked.mode == "L"


def test_creates_missing_output_directory(tmp_path: Path) -> None:
    source = make_image(tmp_path / "in.png")
    destination = tmp_path / "nested" / "deeper" / "out.png"
    assert add_watermark(source, destination, "Crissis") == destination
    assert destination.is_file()


def test_empty_text_raises(tmp_path: Path) -> None:
    source = make_image(tmp_path / "in.png")
    with pytest.raises(ValueError, match="must not be empty"):
        add_watermark(source, tmp_path / "out.png", "   ")


def test_missing_input_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        add_watermark(tmp_path / "nope.png", tmp_path / "out.png", "Crissis")


def test_invalid_image_raises(tmp_path: Path) -> None:
    source = tmp_path / "broken.png"
    source.write_bytes(b"this is definitely not a png")
    with pytest.raises(InvalidImageError, match="Not a valid image"):
        add_watermark(source, tmp_path / "out.png", "Crissis")


def test_invalid_opacity_raises(tmp_path: Path) -> None:
    source = make_image(tmp_path / "in.png")
    with pytest.raises(ValueError, match="Opacity must be"):
        add_watermark(source, tmp_path / "out.png", "Crissis", opacity=1.5)


def test_invalid_position_raises(tmp_path: Path) -> None:
    source = make_image(tmp_path / "in.png")
    with pytest.raises(ValueError, match="Unknown position"):
        add_watermark(source, tmp_path / "out.png", "Crissis", position="middle")


def test_default_text_is_crissis() -> None:
    assert DEFAULT_TEXT == "Crissis"


def test_all_positions_render(tmp_path: Path) -> None:
    source = make_image(tmp_path / "in.png", size=(160, 80))
    for position in POSITIONS:
        result = add_watermark(
            source, tmp_path / f"out_{position}.png", "Crissis", position=position
        )
        assert result.is_file()
