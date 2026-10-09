"""Locate bundled assets both in development and in a frozen (PyInstaller) build."""

import sys
from pathlib import Path

PACKAGE_NAME = "image_watermark_app"


def asset_path(name: str) -> Path:
    """Return the path of a packaged asset file.

    In development the assets live inside the package directory; in a frozen
    one-file build they are extracted under ``sys._MEIPASS`` together with the
    package tree (see ``image_watermark_app.spec``).
    """
    frozen_root = getattr(sys, "_MEIPASS", None)
    if isinstance(frozen_root, str):
        base = Path(frozen_root) / PACKAGE_NAME
    else:
        base = Path(__file__).resolve().parent.parent
    return base / "assets" / name
