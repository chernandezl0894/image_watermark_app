import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import pytest
from PIL import Image

from image_watermark_app.domain import WatermarkRequest
from image_watermark_app.presentation.app import WatermarkApp


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


def test_apply_reports_every_problem_at_once(
    gui: WatermarkApp, monkeypatch: pytest.MonkeyPatch
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(
        messagebox, "showwarning", lambda title, message: warnings.append(message)
    )
    gui.text_var.set("")
    gui.apply_watermark()
    assert warnings == ["Load an image first.\nEnter a watermark text."]


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


class RecordingService:
    """Fake WatermarkUseCases proving the view depends only on the protocol."""

    def __init__(self) -> None:
        self.applied: list[WatermarkRequest] = []
        self.saved: list[Path] = []

    def load(self, path: Path) -> Image.Image:
        return Image.new("RGB", (40, 20), (1, 2, 3))

    def apply(self, source: Image.Image, request: WatermarkRequest) -> Image.Image:
        self.applied.append(request)
        return source.convert("RGBA")

    def save(
        self,
        source: Image.Image,
        request: WatermarkRequest,
        output_path: Path,
    ) -> Path:
        self.applied.append(request)
        self.saved.append(output_path)
        output_path.write_bytes(b"fake")
        return output_path


def test_view_uses_injected_service(
    app_root: tk.Tk, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = RecordingService()
    view = WatermarkApp(app_root, service=service)
    infos: list[str] = []
    monkeypatch.setattr(
        messagebox, "showinfo", lambda title, message: infos.append(message)
    )
    destination = tmp_path / "out.png"
    monkeypatch.setattr(
        filedialog, "asksaveasfilename", lambda **kwargs: str(destination)
    )

    view.load_from_path(tmp_path / "ignored-by-fake.png")
    view.apply_watermark()
    view.save_image()

    assert [request.text for request in service.applied] == ["Crissis", "Crissis"]
    assert service.saved == [destination]
    assert destination.read_bytes() == b"fake"
    assert len(infos) == 1
