"""Tkinter view: widgets and event handlers only; logic lives in other layers."""

import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, ttk
from typing import Protocol

from PIL import Image, ImageTk

from image_watermark_app.application.ports import WatermarkUseCases
from image_watermark_app.application.services import WatermarkService
from image_watermark_app.application.validation import validate_request
from image_watermark_app.domain.models import (
    CUSTOM_POSITION,
    DEFAULT_COLOR,
    DEFAULT_OPACITY,
    DEFAULT_POSITION,
    DEFAULT_TEXT,
    POSITION_CHOICES,
    WatermarkRequest,
)
from image_watermark_app.infrastructure.pillow_repository import PillowImageRepository
from image_watermark_app.presentation.assets import asset_path
from image_watermark_app.presentation.preview import (
    centered_origin,
    fit_within,
    flatten_for_preview,
    point_to_fraction,
)

PREVIEW_MAX = (640, 420)
IMAGE_FILETYPES = [
    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tif *.tiff"),
    ("All files", "*.*"),
]
FONT_FILETYPES = [
    ("Font files", "*.ttf *.otf *.ttc"),
    ("All files", "*.*"),
]


def apply_window_icon(root: tk.Tk) -> tk.PhotoImage | None:
    """Give the window the app icon, or do nothing if it cannot be loaded."""
    icon_file = asset_path("icon.png")
    if not icon_file.is_file():
        return None
    try:
        photo = tk.PhotoImage(file=str(icon_file))
        root.iconphoto(True, photo)
    except tk.TclError:
        return None
    return photo


class PointerEvent(Protocol):
    """Anything that carries pointer coordinates (a Tk event or a test stub)."""

    x: int
    y: int


class WatermarkApp:
    """Main window: load an image, stamp text, save the result."""

    def __init__(
        self,
        root: tk.Tk,
        service: WatermarkUseCases | None = None,
    ) -> None:
        self.root = root
        self._service = (
            service
            if service is not None
            else WatermarkService(PillowImageRepository())
        )
        self.source: Image.Image | None = None
        self.source_path: Path | None = None
        self._preview_photo: ImageTk.PhotoImage | None = None

        root.title("Image Watermark App")
        root.minsize(700, 540)
        # Keeps the PhotoImage alive for as long as the window lives.
        self.window_icon: tk.PhotoImage | None = apply_window_icon(root)

        controls = ttk.Frame(root, padding=(8, 8, 8, 0))
        controls.pack(fill=tk.X, side=tk.TOP)
        ttk.Button(controls, text="Load Image...", command=self.load_image).pack(
            side=tk.LEFT
        )
        ttk.Label(controls, text="Watermark:").pack(side=tk.LEFT, padx=(12, 4))
        self.text_var = tk.StringVar(value=DEFAULT_TEXT)
        entry = ttk.Entry(controls, textvariable=self.text_var, width=24)
        entry.pack(side=tk.LEFT)
        entry.bind("<Return>", self._on_return)

        self.opacity_var = tk.DoubleVar(value=DEFAULT_OPACITY)
        self.position_var = tk.StringVar(value=DEFAULT_POSITION)
        self.color_var = tk.StringVar(value=DEFAULT_COLOR)
        self.font_size_var = tk.StringVar(value="")
        self.font_path_var = tk.StringVar(value="")
        self.rotation_var = tk.StringVar(value="0")
        self.tiled_var = tk.BooleanVar(value=False)
        self.x_var = tk.DoubleVar(value=0.5)
        self.y_var = tk.DoubleVar(value=0.5)

        options = ttk.LabelFrame(root, text="Watermark options", padding=8)
        options.pack(fill=tk.X, side=tk.TOP, padx=8, pady=4)

        position_row = ttk.Frame(options)
        position_row.pack(fill=tk.X)
        ttk.Label(position_row, text="Opacity:").pack(side=tk.LEFT)
        ttk.Scale(
            position_row,
            from_=0.0,
            to=1.0,
            variable=self.opacity_var,
            orient=tk.HORIZONTAL,
            command=self._on_opacity,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 6))
        self.opacity_label = ttk.Label(
            position_row, text=f"{DEFAULT_OPACITY:.0%}", width=5, anchor=tk.E
        )
        self.opacity_label.pack(side=tk.LEFT)
        ttk.Label(position_row, text="Position:").pack(side=tk.LEFT, padx=(12, 4))
        self.position_combo = ttk.Combobox(
            position_row,
            textvariable=self.position_var,
            values=POSITION_CHOICES,
            state="readonly",
            width=14,
        )
        self.position_combo.pack(side=tk.LEFT)

        style_row = ttk.Frame(options)
        style_row.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(style_row, text="Text colour:").pack(side=tk.LEFT)
        self.color_swatch = tk.Label(
            style_row, text="", width=4, relief=tk.SUNKEN, bg=DEFAULT_COLOR
        )
        self.color_swatch.pack(side=tk.LEFT, padx=(4, 4))
        ttk.Button(style_row, text="Choose...", command=self.choose_color).pack(
            side=tk.LEFT
        )
        ttk.Label(style_row, text="Font size:").pack(side=tk.LEFT, padx=(12, 4))
        ttk.Spinbox(
            style_row,
            from_=1,
            to=500,
            width=6,
            textvariable=self.font_size_var,
        ).pack(side=tk.LEFT)
        ttk.Label(style_row, text="(auto)").pack(side=tk.LEFT, padx=(4, 0))
        ttk.Label(style_row, text="Font:").pack(side=tk.LEFT, padx=(12, 4))
        ttk.Entry(
            style_row,
            textvariable=self.font_path_var,
            width=22,
            state="readonly",
        ).pack(side=tk.LEFT)
        ttk.Button(style_row, text="Browse...", command=self.browse_font).pack(
            side=tk.LEFT, padx=(4, 0)
        )
        ttk.Button(style_row, text="Clear", command=self.clear_font).pack(
            side=tk.LEFT, padx=(4, 0)
        )

        placement_row = ttk.Frame(options)
        placement_row.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(placement_row, text="Rotation:").pack(side=tk.LEFT)
        ttk.Spinbox(
            placement_row,
            from_=-180,
            to=180,
            width=5,
            textvariable=self.rotation_var,
        ).pack(side=tk.LEFT)
        ttk.Label(placement_row, text="°").pack(side=tk.LEFT, padx=(2, 12))
        ttk.Checkbutton(
            placement_row, text="Tile (repeat)", variable=self.tiled_var
        ).pack(side=tk.LEFT)
        ttk.Label(
            placement_row,
            text="Drag on the preview to place the watermark",
            font=("TkDefaultFont", 9, "italic"),
        ).pack(side=tk.LEFT, padx=(12, 0))

        self.status_var = tk.StringVar(value="No image loaded")
        ttk.Label(
            root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        ).pack(fill=tk.X, side=tk.BOTTOM)

        actions = ttk.Frame(root, padding=8)
        actions.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(actions, text="Apply Watermark", command=self.apply_watermark).pack(
            side=tk.LEFT
        )
        ttk.Button(actions, text="Save As...", command=self.save_image).pack(
            side=tk.RIGHT
        )

        preview_frame = ttk.Frame(root, padding=8)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        self.preview_label = ttk.Label(
            preview_frame, anchor=tk.CENTER, text="Load an image to begin"
        )
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        self.preview_label.bind("<Button-1>", self._on_drag_move)
        self.preview_label.bind("<B1-Motion>", self._on_drag_move)

    def load_image(self) -> None:
        """Ask for an image file and load it."""
        path = filedialog.askopenfilename(
            title="Choose an image", filetypes=IMAGE_FILETYPES
        )
        if path:
            self.load_from_path(Path(path))

    def load_from_path(self, path: Path) -> None:
        """Load ``path`` into the preview, reporting errors to the user."""
        try:
            image = self._service.load(path)
        except OSError, ValueError:
            messagebox.showerror("Invalid image", f"Could not open this file:\n{path}")
            return
        self.source = image
        self.source_path = path
        self._show_preview(image)
        self.status_var.set(f"Loaded: {path.name}")

    def apply_watermark(self) -> None:
        """Render the watermark over the loaded image and refresh the preview."""
        if not self._validate("Cannot apply watermark"):
            return
        assert self.source is not None  # guaranteed by _validate above
        try:
            request = self._current_request()
        except ValueError as exc:
            messagebox.showwarning("Cannot apply watermark", str(exc))
            return
        marked = self._service.apply(self.source, request)
        self._show_preview(marked)
        self.status_var.set("Watermark applied — use Save As to export")

    def save_image(self) -> None:
        """Stamp with the current controls and write the result to a file."""
        if not self._validate("Cannot save"):
            return
        assert self.source is not None  # guaranteed by _validate above
        try:
            request = self._current_request()
        except ValueError as exc:
            messagebox.showwarning("Cannot save", str(exc))
            return

        suggested = "watermarked.png"
        if self.source_path is not None:
            suffix = self.source_path.suffix or ".png"
            suggested = f"{self.source_path.stem}_watermarked{suffix}"
        path = filedialog.asksaveasfilename(
            title="Save image as",
            defaultextension=".png",
            initialfile=suggested,
            filetypes=IMAGE_FILETYPES,
        )
        if not path:
            return

        try:
            saved = self._service.save(self.source, request, Path(path))
        except (OSError, ValueError) as exc:
            messagebox.showerror("Save failed", str(exc))
            return
        messagebox.showinfo("Saved", f"Image saved to:\n{saved}")
        self.status_var.set(f"Saved: {Path(saved).name}")

    def choose_color(self) -> None:
        """Open the system colour picker and store the chosen text colour."""
        result = colorchooser.askcolor(
            color=self.color_var.get(), title="Choose text colour"
        )
        _rgb, hex_color = result
        if hex_color:
            self.color_var.set(hex_color)
            self.color_swatch.configure(bg=hex_color)

    def browse_font(self) -> None:
        """Pick a custom TTF/OTF font file for the watermark text."""
        path = filedialog.askopenfilename(
            title="Choose a font", filetypes=FONT_FILETYPES
        )
        if path:
            self.font_path_var.set(path)

    def clear_font(self) -> None:
        """Fall back to the default built-in font."""
        self.font_path_var.set("")

    def _validate(self, title: str) -> bool:
        """Run the application validation and warn the user on failure."""
        errors = validate_request(
            self.text_var.get(),
            has_image=self.source is not None,
            font_path=self._selected_font_path(),
        )
        if errors:
            messagebox.showwarning(title, "\n".join(errors))
            return False
        return True

    def _selected_font_path(self) -> Path | None:
        font_path = self.font_path_var.get().strip()
        return Path(font_path) if font_path else None

    def _current_request(self) -> WatermarkRequest:
        """Read every control into a validated WatermarkRequest."""
        font_size_text = self.font_size_var.get().strip()
        font_size: int | None = None
        if font_size_text:
            font_size = self._parse_whole_number("Font size", font_size_text)
        rotation = self._parse_whole_number("Rotation", self.rotation_var.get().strip())
        return WatermarkRequest(
            text=self.text_var.get(),
            opacity=self.opacity_var.get(),
            position=self.position_var.get(),
            color=self.color_var.get().strip(),
            font_size=font_size,
            font_path=self._selected_font_path(),
            rotation=rotation,
            tiled=self.tiled_var.get(),
            x=self.x_var.get(),
            y=self.y_var.get(),
        )

    @staticmethod
    def _parse_whole_number(name: str, value: str) -> int:
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"{name} must be a whole number, got {value!r}") from None

    def _on_drag_move(self, event: PointerEvent) -> None:
        """Follow the pointer over the preview, placing the watermark under it."""
        if self.source is None or self._preview_photo is None:
            return
        photo_size = (self._preview_photo.width(), self._preview_photo.height())
        label_size = (
            self.preview_label.winfo_width(),
            self.preview_label.winfo_height(),
        )
        if label_size[0] < photo_size[0] or label_size[1] < photo_size[1]:
            return
        origin = centered_origin(label_size, photo_size)
        local_x = event.x - origin[0]
        local_y = event.y - origin[1]
        if not (0 <= local_x <= photo_size[0] and 0 <= local_y <= photo_size[1]):
            return
        fraction = point_to_fraction((event.x, event.y), origin, photo_size)
        self.position_var.set(CUSTOM_POSITION)
        self.x_var.set(fraction[0])
        self.y_var.set(fraction[1])
        self._refresh_preview_quietly()

    def _refresh_preview_quietly(self) -> None:
        """Re-render during a drag without raising any dialog."""
        if self.source is None:
            return
        if validate_request(
            self.text_var.get(),
            has_image=True,
            font_path=self._selected_font_path(),
        ):
            return
        try:
            request = self._current_request()
        except ValueError:
            return
        marked = self._service.apply(self.source, request)
        self._show_preview(marked)
        self.status_var.set(f"Position: {self.x_var.get():.0%}, {self.y_var.get():.0%}")

    def _on_opacity(self, value: str) -> None:
        """Keep the percentage label in sync with the opacity slider."""
        self.opacity_label.configure(text=f"{float(value):.0%}")

    def _on_return(self, event: tk.Event[tk.Entry]) -> str:
        """Enter in the text field applies the watermark."""
        self.apply_watermark()
        return "break"

    def _show_preview(self, image: Image.Image) -> None:
        preview = flatten_for_preview(fit_within(image, PREVIEW_MAX))
        photo = ImageTk.PhotoImage(preview)
        self.preview_label.configure(image=photo, text="")
        self._preview_photo = photo


def main() -> None:
    """Launch the desktop application."""
    root = tk.Tk()
    WatermarkApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
