from pathlib import Path

import pytest
from PIL import Image

from image_watermark_app.domain import InvalidImageError
from image_watermark_app.infrastructure import PillowImageRepository

REPO = PillowImageRepository()


def make_file(path: Path, mode: str = "RGB") -> Path:
    color = (30, 60, 90) if mode == "RGB" else 60 if mode == "L" else (30, 60, 90, 200)
    Image.new(mode, (200, 100), color).save(path)
    return path


def test_load_returns_image(tmp_path: Path) -> None:
    source = make_file(tmp_path / "in.png")
    loaded = REPO.load(source)
    assert loaded.size == (200, 100)
    assert loaded.mode == "RGB"


def test_load_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        REPO.load(tmp_path / "missing.png")


def test_load_invalid_image_raises(tmp_path: Path) -> None:
    broken = tmp_path / "broken.png"
    broken.write_bytes(b"definitely not a png")
    with pytest.raises(InvalidImageError, match="Not a valid image"):
        REPO.load(broken)


def test_save_creates_missing_directories(tmp_path: Path) -> None:
    image = REPO.load(make_file(tmp_path / "in.png"))
    destination = tmp_path / "nested" / "deeper" / "out.png"
    result = REPO.save(image, destination, like=image)
    assert result == destination
    assert destination.is_file()


def test_save_keeps_rgb_for_png(tmp_path: Path) -> None:
    image = REPO.load(make_file(tmp_path / "in.png"))
    result = REPO.save(image.convert("RGBA"), tmp_path / "out.png", like=image)
    with Image.open(result) as saved:
        assert saved.mode == "RGB"


def test_save_keeps_alpha_for_rgba_source(tmp_path: Path) -> None:
    image = REPO.load(make_file(tmp_path / "in.png", mode="RGBA"))
    result = REPO.save(image, tmp_path / "out.png", like=image)
    with Image.open(result) as saved:
        assert saved.mode == "RGBA"


def test_save_keeps_grayscale(tmp_path: Path) -> None:
    image = REPO.load(make_file(tmp_path / "in.png", mode="L"))
    result = REPO.save(image.convert("RGBA"), tmp_path / "out.png", like=image)
    with Image.open(result) as saved:
        assert saved.mode == "L"


def test_save_as_jpeg_converts_to_rgb(tmp_path: Path) -> None:
    image = REPO.load(make_file(tmp_path / "in.png", mode="RGBA"))
    result = REPO.save(image, tmp_path / "out.jpg", like=image)
    with Image.open(result) as saved:
        assert saved.format == "JPEG"
        assert saved.mode == "RGB"
