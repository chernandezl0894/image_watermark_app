import sys
from pathlib import Path

import pytest
from PIL import Image

import image_watermark_app
from image_watermark_app.presentation.assets import asset_path

ASSETS = Path(image_watermark_app.__file__).resolve().parent / "assets"
EXPECTED_ICO_SIZES = {(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)}


def test_icon_png_exists_and_is_valid() -> None:
    icon = ASSETS / "icon.png"
    assert icon.is_file()
    with Image.open(icon) as image:
        assert image.size == (256, 256)
        assert image.mode == "RGBA"
        colors = image.convert("RGBA").getcolors(maxcolors=256 * 256)
        assert colors is not None
        assert len(colors) > 32


def test_icon_ico_exists_with_standard_sizes() -> None:
    icon = ASSETS / "icon.ico"
    assert icon.is_file()
    with Image.open(icon) as image:
        assert image.info["sizes"] >= EXPECTED_ICO_SIZES


def test_asset_path_resolves_inside_the_package() -> None:
    assert asset_path("icon.png") == ASSETS / "icon.png"
    assert asset_path("icon.png").is_file()


def test_asset_path_uses_the_frozen_bundle_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundled = tmp_path / "image_watermark_app" / "assets"
    bundled.mkdir(parents=True)
    (bundled / "icon.png").write_bytes(b"fake")
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert asset_path("icon.png") == bundled / "icon.png"


def test_asset_path_falls_back_when_meipass_is_not_a_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "_MEIPASS", object(), raising=False)
    assert asset_path("icon.png") == ASSETS / "icon.png"
