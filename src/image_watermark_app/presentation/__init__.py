"""Presentation layer: the Tkinter desktop interface."""

from image_watermark_app.presentation.app import WatermarkApp, main
from image_watermark_app.presentation.preview import (
    centered_origin,
    fit_within,
    flatten_for_preview,
    point_to_fraction,
)

__all__ = [
    "WatermarkApp",
    "centered_origin",
    "fit_within",
    "flatten_for_preview",
    "main",
    "point_to_fraction",
]
