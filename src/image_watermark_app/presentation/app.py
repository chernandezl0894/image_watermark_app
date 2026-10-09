"""Tkinter view: widgets and event handlers only; logic lives in other layers."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from image_watermark_app.application.ports import WatermarkUseCases
from image_watermark_app.application.services import WatermarkService
from image_watermark_app.application.validation import validate_request
from image_watermark_app.domain.models import DEFAULT_TEXT, WatermarkRequest
from image_watermark_app.infrastructure.pillow_repository import PillowImageRepository
from image_watermark_app.presentation.preview import fit_within, flatten_for_preview

PREVIEW_MAX = (640, 420)
IMAGE_FILETYPES = [
    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tif *.tiff"),
    ("All files", "*.*"),
]


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

        controls = ttk.Frame(root, padding=8)
        controls.pack(fill=tk.X, side=tk.TOP)
        ttk.Button(controls, text="Load Image...", command=self.load_image).pack(
            side=tk.LEFT
        )
        ttk.Label(controls, text="Watermark:").pack(side=tk.LEFT, padx=(12, 4))
        self.text_var = tk.StringVar(value=DEFAULT_TEXT)
        entry = ttk.Entry(controls, textvariable=self.text_var, width=24)
        entry.pack(side=tk.LEFT)
        entry.bind("<Return>", self._on_return)

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
        text = self.text_var.get()
        errors = validate_request(text, has_image=self.source is not None)
        if errors:
            messagebox.showwarning("Cannot apply watermark", "\n".join(errors))
            return
        assert self.source is not None  # guaranteed by validate_request above
        request = WatermarkRequest(text=text)
        marked = self._service.apply(self.source, request)
        self._show_preview(marked)
        self.status_var.set("Watermark applied — use Save As to export")

    def save_image(self) -> None:
        """Stamp with the current text and write the result to a file."""
        text = self.text_var.get()
        errors = validate_request(text, has_image=self.source is not None)
        if errors:
            messagebox.showwarning("Cannot save", "\n".join(errors))
            return
        assert self.source is not None  # guaranteed by validate_request above

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
            saved = self._service.save(
                self.source, WatermarkRequest(text=text), Path(path)
            )
        except (OSError, ValueError) as exc:
            messagebox.showerror("Save failed", str(exc))
            return
        messagebox.showinfo("Saved", f"Image saved to:\n{saved}")
        self.status_var.set(f"Saved: {Path(saved).name}")

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
