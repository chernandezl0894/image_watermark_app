import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox
from types import SimpleNamespace

import pytest
from PIL import Image

from image_watermark_app.domain import WatermarkRequest
from image_watermark_app.presentation import centered_origin
from image_watermark_app.presentation.app import WatermarkApp


def make_test_image(path: Path) -> Path:
    Image.new("RGB", (300, 200), (30, 60, 90)).save(path)
    return path


@pytest.fixture
def gui(app_root: tk.Tk) -> WatermarkApp:
    return WatermarkApp(app_root)


def test_window_opens_with_defaults(gui: WatermarkApp) -> None:
    assert gui.root.title() == "Image Watermark App"
    assert gui.text_var.get() == "image_watermark_app"
    assert gui.status_var.get() == "No image loaded"
    assert gui.source is None
    assert gui.opacity_var.get() == pytest.approx(0.5)
    assert gui.position_var.get() == "bottom-right"
    assert gui.color_var.get() == "#FFFFFF"
    assert gui.font_size_var.get() == ""
    assert gui.font_path_var.get() == ""


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
    gui.text_var.set("image_watermark_app")
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


def test_choose_color_updates_color_var(
    gui: WatermarkApp, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(colorchooser, "askcolor", lambda **kwargs: (None, "#112233"))
    gui.choose_color()
    assert gui.color_var.get() == "#112233"


def test_choose_color_cancel_keeps_previous_color(
    gui: WatermarkApp, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(colorchooser, "askcolor", lambda **kwargs: (None, None))
    gui.choose_color()
    assert gui.color_var.get() == "#FFFFFF"


def test_browse_font_sets_font_path(
    gui: WatermarkApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    font = tmp_path / "custom.ttf"
    font.write_bytes(b"\0")
    monkeypatch.setattr(filedialog, "askopenfilename", lambda **kwargs: str(font))
    gui.browse_font()
    assert gui.font_path_var.get() == str(font)


def test_clear_font_resets_to_default(gui: WatermarkApp) -> None:
    gui.font_path_var.set("/tmp/custom.ttf")
    gui.clear_font()
    assert gui.font_path_var.get() == ""


def test_apply_with_invalid_font_size_warns(
    gui: WatermarkApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(
        messagebox, "showwarning", lambda title, message: warnings.append(message)
    )
    gui.load_from_path(make_test_image(tmp_path / "photo.png"))
    gui.font_size_var.set("abc")
    gui.apply_watermark()
    assert warnings == ["Font size must be a whole number, got 'abc'"]


def test_apply_with_missing_font_warns(
    gui: WatermarkApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(
        messagebox, "showwarning", lambda title, message: warnings.append(message)
    )
    gui.load_from_path(make_test_image(tmp_path / "photo.png"))
    gui.font_path_var.set(str(tmp_path / "gone.ttf"))
    gui.apply_watermark()
    assert warnings == [f"Font file not found: {tmp_path / 'gone.ttf'}"]


def test_placement_control_defaults(gui: WatermarkApp) -> None:
    assert gui.rotation_var.get() == "0"
    assert gui.tiled_var.get() is False
    assert gui.position_var.get() == "bottom-right"
    assert gui.x_var.get() == pytest.approx(0.5)
    assert gui.y_var.get() == pytest.approx(0.5)
    assert "custom" in gui.position_combo.cget("values")


def test_apply_with_invalid_rotation_warns(
    gui: WatermarkApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(
        messagebox, "showwarning", lambda title, message: warnings.append(message)
    )
    gui.load_from_path(make_test_image(tmp_path / "photo.png"))
    gui.rotation_var.set("abc")
    gui.apply_watermark()
    assert warnings == ["Rotation must be a whole number, got 'abc'"]


def test_drag_updates_position(
    gui: WatermarkApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    gui.load_from_path(make_test_image(tmp_path / "photo.png"))
    assert gui._preview_photo is not None
    photo_size = (gui._preview_photo.width(), gui._preview_photo.height())
    monkeypatch.setattr(gui.preview_label, "winfo_width", lambda: 700)
    monkeypatch.setattr(gui.preview_label, "winfo_height", lambda: 500)
    origin = centered_origin((700, 500), photo_size)
    event = SimpleNamespace(
        x=origin[0] + photo_size[0] // 4, y=origin[1] + photo_size[1] // 4
    )
    gui._on_drag_move(event)
    assert gui.position_var.get() == "custom"
    assert gui.x_var.get() == pytest.approx(0.25)
    assert gui.y_var.get() == pytest.approx(0.25)
    assert "Position" in gui.status_var.get()


def test_drag_without_image_does_nothing(gui: WatermarkApp) -> None:
    gui._on_drag_move(SimpleNamespace(x=10, y=10))
    assert gui.position_var.get() == "bottom-right"
    assert gui.source is None


def test_drag_outside_the_photo_is_ignored(
    gui: WatermarkApp, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    gui.load_from_path(make_test_image(tmp_path / "photo.png"))
    monkeypatch.setattr(gui.preview_label, "winfo_width", lambda: 700)
    monkeypatch.setattr(gui.preview_label, "winfo_height", lambda: 500)
    gui._on_drag_move(SimpleNamespace(x=0, y=0))
    assert gui.position_var.get() == "bottom-right"


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

    assert [request.text for request in service.applied] == [
        "image_watermark_app",
        "image_watermark_app",
    ]
    assert service.saved == [destination]
    assert destination.read_bytes() == b"fake"
    assert len(infos) == 1


def test_controls_reach_the_service(app_root: tk.Tk, tmp_path: Path) -> None:
    service = RecordingService()
    view = WatermarkApp(app_root, service=service)
    font = tmp_path / "custom.ttf"
    font.write_bytes(b"\0")

    view.load_from_path(tmp_path / "ignored-by-fake.png")
    view.opacity_var.set(0.8)
    view.position_var.set("top-left")
    view.color_var.set("#00FF00")
    view.font_size_var.set("48")
    view.font_path_var.set(str(font))
    view.rotation_var.set("30")
    view.tiled_var.set(True)
    view.apply_watermark()

    [request] = service.applied
    assert request.opacity == pytest.approx(0.8)
    assert request.position == "top-left"
    assert request.color == "#00FF00"
    assert request.font_size == 48
    assert request.font_path == font
    assert request.rotation == pytest.approx(30.0)
    assert request.tiled is True


def test_drag_reaches_the_service(
    app_root: tk.Tk, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = RecordingService()
    view = WatermarkApp(app_root, service=service)
    view.load_from_path(tmp_path / "ignored-by-fake.png")
    assert view._preview_photo is not None
    photo_size = (view._preview_photo.width(), view._preview_photo.height())
    monkeypatch.setattr(view.preview_label, "winfo_width", lambda: 700)
    monkeypatch.setattr(view.preview_label, "winfo_height", lambda: 500)
    origin = centered_origin((700, 500), photo_size)
    view._on_drag_move(
        SimpleNamespace(x=origin[0] + photo_size[0], y=origin[1] + photo_size[1])
    )
    view.apply_watermark()

    first, second = service.applied
    assert first.position == "custom"
    assert first.x == pytest.approx(1.0)
    assert first.y == pytest.approx(1.0)
    assert second.position == "custom"


def test_window_shows_app_icon(gui: WatermarkApp) -> None:
    assert gui.window_icon is not None
    assert gui.window_icon.width() == 256


def test_missing_icon_asset_fails_silently(
    app_root: tk.Tk, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "image_watermark_app.presentation.app.asset_path",
        lambda name: Path("/nonexistent") / name,
    )
    view = WatermarkApp(app_root)
    assert view.window_icon is None


def test_icon_load_error_fails_silently(
    app_root: tk.Tk, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken_photoimage(*args: object, **kwargs: object) -> tk.PhotoImage:
        raise tk.TclError("cannot build image")

    monkeypatch.setattr(tk, "PhotoImage", broken_photoimage)
    view = WatermarkApp(app_root)
    assert view.window_icon is None
