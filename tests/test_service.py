from pathlib import Path

import pytest
from PIL import Image, ImageChops

from image_watermark_app.application import WatermarkService
from image_watermark_app.domain import (
    DEFAULT_TEXT,
    POSITIONS,
    InvalidImageError,
    WatermarkRequest,
)
from image_watermark_app.infrastructure import PillowImageRepository

SERVICE = WatermarkService(PillowImageRepository())
REQUEST = WatermarkRequest(text=DEFAULT_TEXT)


def make_file(path: Path, size: tuple[int, int] = (300, 200)) -> Path:
    Image.new("RGB", size, (30, 60, 90)).save(path)
    return path


def test_watermark_file_writes_output(tmp_path: Path) -> None:
    source = make_file(tmp_path / "in.png")
    result = SERVICE.watermark_file(source, tmp_path / "out.png", REQUEST)
    assert result == tmp_path / "out.png"
    assert result.is_file()


def test_dimensions_are_preserved(tmp_path: Path) -> None:
    source = make_file(tmp_path / "in.png", size=(320, 140))
    result = SERVICE.watermark_file(source, tmp_path / "out.png", REQUEST)
    with Image.open(source) as original, Image.open(result) as marked:
        assert marked.size == original.size


def test_pixels_are_changed(tmp_path: Path) -> None:
    source = make_file(tmp_path / "in.png")
    result = SERVICE.watermark_file(source, tmp_path / "out.png", REQUEST)
    with Image.open(source) as original, Image.open(result) as marked:
        diff = ImageChops.difference(original, marked.convert("RGB")).getbbox()
        assert diff is not None
        assert diff[0] > original.width // 2
        assert diff[1] > original.height // 2


@pytest.mark.parametrize("position", list(POSITIONS))
def test_every_position_renders(tmp_path: Path, position: str) -> None:
    source = make_file(tmp_path / "in.png", size=(160, 80))
    request = WatermarkRequest(text=DEFAULT_TEXT, position=position)
    result = SERVICE.watermark_file(source, tmp_path / f"out_{position}.png", request)
    assert result.is_file()


def test_output_jpeg_format(tmp_path: Path) -> None:
    source = make_file(tmp_path / "in.png")
    result = SERVICE.watermark_file(source, tmp_path / "out.jpg", REQUEST)
    with Image.open(result) as marked:
        assert marked.format == "JPEG"
        assert marked.mode == "RGB"


def test_apply_returns_in_memory_copy(tmp_path: Path) -> None:
    source = make_file(tmp_path / "in.png")
    loaded = SERVICE.load(source)
    marked = SERVICE.apply(loaded, REQUEST)
    assert marked.mode == "RGBA"
    assert ImageChops.difference(loaded, marked.convert("RGB")).getbbox() is not None


def test_missing_input_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        SERVICE.watermark_file(tmp_path / "nope.png", tmp_path / "out.png", REQUEST)


def test_invalid_input_raises(tmp_path: Path) -> None:
    broken = tmp_path / "broken.png"
    broken.write_bytes(b"not an image")
    with pytest.raises(InvalidImageError, match="Not a valid image"):
        SERVICE.watermark_file(broken, tmp_path / "out.png", REQUEST)


def test_save_from_memory_writes_file(tmp_path: Path) -> None:
    source = make_file(tmp_path / "in.png")
    loaded = SERVICE.load(source)
    destination = tmp_path / "out.png"
    assert SERVICE.save(loaded, REQUEST, destination) == destination
    with Image.open(destination) as saved:
        assert saved.size == loaded.size
        assert ImageChops.difference(loaded, saved).getbbox() is not None
