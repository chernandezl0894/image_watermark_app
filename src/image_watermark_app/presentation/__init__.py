"""Presentation layer: the Tkinter desktop interface."""

from image_watermark_app.presentation.app import WatermarkApp, main
from image_watermark_app.presentation.preview import fit_within, flatten_for_preview

__all__ = ["WatermarkApp", "fit_within", "flatten_for_preview", "main"]
