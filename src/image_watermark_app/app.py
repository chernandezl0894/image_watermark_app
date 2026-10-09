"""Tkinter desktop interface for the Image Watermarking App."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk, UnidentifiedImageError

from image_watermark_app.watermark import DEFAULT_TEXT, save_stamped, stamp_image

PREVIEW_MAX = (640, 420)
IMAGE_FILETYPES = [
    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tif *.tiff"),
    ("All files", "*.*"),
]


def fit_within(image: Image.Image, bounds: tuple[int, int]) -> Image.Image:
    """Return a copy of ``image`` scaled down to fit inside ``bounds``."""
    fitted = image.copy()
    fitted.thumbnail(bounds, Image.Resampling.LANCZOS)
    return fitted


def flatten_for_preview(image: Image.Image) -> Image.Image:
    """Convert any image to RGB for display, compositing alpha over white."""
    if image.mode == "RGB":
        return image
    rgba = image.convert("RGBA")
    background = Image.new("RGB", rgba.size, (255, 255, 255))
    background.paste(rgba, mask=rgba.getchannel("A"))
    return background


class WatermarkApp:
    """Main application window: load an image, stamp text, save the result."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
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
        ttk.Entry(controls, textvariable=self.text_var, width=24).pack(side=tk.LEFT)

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
            with Image.open(path) as opened:
                image = opened.copy()
        except UnidentifiedImageError, OSError:
            messagebox.showerror("Invalid image", f"Could not open this file:\n{path}")
            return
        self.source = image
        self.source_path = path
        self._show_preview(image)
        self.status_var.set(f"Loaded: {path.name}")

    def apply_watermark(self) -> None:
        """Render the watermark over the loaded image and refresh the preview."""
        if self.source is None:
            messagebox.showwarning("No image", "Load an image first.")
            return
        text = self.text_var.get()
        if not text.strip():
            messagebox.showwarning("Empty text", "Enter a watermark text.")
            return
        marked = stamp_image(self.source, text)
        self._show_preview(marked)
        self.status_var.set("Watermark applied — use Save As to export")

    def save_image(self) -> None:
        """Stamp with the current text and write the result to a file."""
        if self.source is None:
            messagebox.showwarning("No image", "Load an image first.")
            return
        text = self.text_var.get()
        if not text.strip():
            messagebox.showwarning("Empty text", "Enter a watermark text.")
            return

        suggested = "watermarked.png"
        if self.source_path is not None:
            suggested = f"{self.source_path.stem}_watermarked{self.source_path.suffix or '.png'}"
        path = filedialog.asksaveasfilename(
            title="Save image as",
            defaultextension=".png",
            initialfile=suggested,
            filetypes=IMAGE_FILETYPES,
        )
        if not path:
            return

        try:
            saved = save_stamped(self.source, path, text)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Save failed", str(exc))
            return
        messagebox.showinfo("Saved", f"Image saved to:\n{saved}")
        self.status_var.set(f"Saved: {saved.name}")

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
