"""Domain entities: validated data with no dependencies on I/O or the UI."""

from dataclasses import dataclass
from typing import Final

DEFAULT_TEXT: Final = "Crissis"
DEFAULT_OPACITY: Final = 0.5
DEFAULT_POSITION: Final = "bottom-right"
POSITIONS: Final = (
    "top-left",
    "top-right",
    "bottom-left",
    "bottom-right",
    "center",
)
MAX_MARGIN_RATIO: Final = 0.5


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
