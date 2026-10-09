"""Shared fixtures: the GUI tests need a display, so skip gracefully without one."""

import tkinter as tk
from collections.abc import Iterator

import pytest


@pytest.fixture
def app_root() -> Iterator[tk.Tk]:
    """Create a withdrawn Tk root and destroy it after the test."""
    try:
        root = tk.Tk()
    except tk.TclError as exc:  # pragma: no cover - depends on the machine
        pytest.skip(f"Cannot open a display: {exc}")
    root.withdraw()
    yield root
    root.destroy()
