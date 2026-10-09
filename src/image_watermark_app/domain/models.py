"""Domain entities: validated data with no dependencies on I/O or the UI."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

DEFAULT_TEXT: Final = "Crissis"
DEFAULT_OPACITY: Final = 0.5
DEFAULT_POSITION: Final = "bottom-right"
DEFAULT_COLOR: Final = "#FFFFFF"
POSITIONS: Final = (
    "top-left",
    "top-right",
    "bottom-left",
    "bottom-right",
    "center",
)
MAX_MARGIN_RATIO: Final = 0.5
HEX_COLOR_PATTERN: Final = re.compile(r"^#[0-9A-Fa-f]{6}$")


class InvalidImageError(ValueError):
    """Raised when image data cannot be decoded."""


@dataclass(frozen=True, slots=True)
class WatermarkRequest:
    """A validated description of the watermark to stamp on an image.

    Raises ``ValueError`` on construction when any field is out of range,
    so a request that exists is always safe to apply.
    """

    text: str
    opacity: float = DEFAULT_OPACITY
    position: str = DEFAULT_POSITION
    margin_ratio: float = 0.03
    color: str = DEFAULT_COLOR
    font_size: int | None = None
    font_path: Path | None = None

    def __post_init__(self) -> None:
        if not self.text or not self.text.strip():
            raise ValueError("Watermark text must not be empty")
        if not 0.0 <= self.opacity <= 1.0:
            raise ValueError(f"Opacity must be between 0.0 and 1.0, got {self.opacity}")
        if self.position not in POSITIONS:
            raise ValueError(
                f"Unknown position {self.position!r}; choose one of {POSITIONS}"
            )
        if not 0.0 <= self.margin_ratio <= MAX_MARGIN_RATIO:
            raise ValueError(
                f"Margin ratio must be between 0.0 and {MAX_MARGIN_RATIO}, "
                f"got {self.margin_ratio}"
            )
        if not HEX_COLOR_PATTERN.match(self.color):
            raise ValueError(
                f"Color must be a hex string like #RRGGBB, got {self.color!r}"
            )
        if self.font_size is not None and self.font_size < 1:
            raise ValueError(f"Font size must be at least 1, got {self.font_size}")
