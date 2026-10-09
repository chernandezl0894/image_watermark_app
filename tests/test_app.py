import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import pytest
from PIL import Image

from image_watermark_app.app import (
    WatermarkApp,
    fit_within,
    flatten_for_preview,
)


def make_test_image(path: Path) -> Path:
    Image.new("RGB", (300, 200), (30, 60, 90)).save(path)
    return path


@pytest.fixture
def gui(app_root: tk.Tk) -> WatermarkApp:
    return WatermarkApp(app_root)


def test_window_opens_with_defaults(gui: WatermarkApp) -> None:
    assert gui.root.title() == "Image Watermark App"
    assert gui.text_var.get() == "Crissis"
    assert gui.status_var.get() == "No image loaded"
    assert gui.source is None


def test_load_from_path_shows_preview(gui: WatermarkApp, tmp_path: Path) -> None:
    source = make_test_image(tmp_path / "photo.png")
    gui.load_from_path(source)
    assert gui.source is not None
    assert gui.source_path == source
    assert gui._preview_photo is not None
    assert "photo.png" in gui.status_var.get()


def test_load_invalid_file_reports_error(
    gui: WatermarkApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    errors: list[str] = []
    monkeypatch.setattr(
        messagebox, "showerror", lambda title, message: errors.append(message)
    )
    broken = tmp_path / "broken.png"
    broken.write_bytes(b"not an image")
    gui.load_from_path(broken)
    assert gui.source is None
    assert len(errors) == 1


def test_load_missing_file_reports_error(
    gui: WatermarkApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    errors: list[str] = []
    monkeypatch.setattr(
        messagebox, "showerror", lambda title, message: errors.append(message)
    )
    gui.load_from_path(tmp_path / "missing.png")
    assert gui.source is None
    assert len(errors) == 1


def test_apply_without_image_warns(
    gui: WatermarkApp, monkeypatch: pytest.MonkeyPatch
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(
        messagebox, "showwarning", lambda title, message: warnings.append(message)
    )
    gui.apply_watermark()
    assert warnings == ["Load an image first."]


def test_apply_with_empty_text_warns(
    gui: WatermarkApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(
        messagebox, "showwarning", lambda title, message: warnings.append(message)
    )
    gui.load_from_path(make_test_image(tmp_path / "photo.png"))
    gui.text_var.set("   ")
    gui.apply_watermark()
    assert warnings == ["Enter a watermark text."]


def test_apply_refreshes_preview(gui: WatermarkApp, tmp_path: Path) -> None:
    gui.load_from_path(make_test_image(tmp_path / "photo.png"))
    gui.text_var.set("Crissis")
    gui.apply_watermark()
    assert gui._preview_photo is not None
    assert "Watermark applied" in gui.status_var.get()


def test_save_writes_file(
    gui: WatermarkApp,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infos: list[str] = []
    monkeypatch.setattr(
        messagebox, "showinfo", lambda title, message: infos.append(message)
    )
    destination = tmp_path / "saved.png"
    monkeypatch.setattr(
        filedialog, "asksaveasfilename", lambda **kwargs: str(destination)
    )

    gui.load_from_path(make_test_image(tmp_path / "photo.png"))
    gui.save_image()

    assert destination.is_file()
    assert len(infos) == 1
    assert "Saved" in gui.status_var.get()


def test_save_suggested_name_follows_source(
    gui: WatermarkApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        filedialog, "asksaveasfilename", lambda **kwargs: captured.update(kwargs) or ""
    )
    gui.load_from_path(make_test_image(tmp_path / "holiday.png"))
    gui.save_image()
    assert captured["initialfile"] == "holiday_watermarked.png"


def test_save_without_image_warns(
    gui: WatermarkApp, monkeypatch: pytest.MonkeyPatch
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(
        messagebox, "showwarning", lambda title, message: warnings.append(message)
    )
    gui.save_image()
    assert warnings == ["Load an image first."]


def test_save_empty_text_warns(
    gui: WatermarkApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(
        messagebox, "showwarning", lambda title, message: warnings.append(message)
    )
    gui.load_from_path(make_test_image(tmp_path / "photo.png"))
    gui.text_var.set("")
    gui.save_image()
    assert warnings == ["Enter a watermark text."]


def test_save_cancel_writes_nothing(
    gui: WatermarkApp,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(filedialog, "asksaveasfilename", lambda **kwargs: "")
    gui.load_from_path(make_test_image(tmp_path / "photo.png"))
    gui.save_image()
    assert list(tmp_path.glob("*_watermarked.*")) == []


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
