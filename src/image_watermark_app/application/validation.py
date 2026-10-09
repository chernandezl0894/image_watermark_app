"""User-facing validation of form input, kept out of the domain and the view."""

from pathlib import Path


def validate_request(
    text: str, *, has_image: bool, font_path: Path | None = None
) -> list[str]:
    """Return friendly messages for invalid form input.

    An empty list means the input is valid.
    """
    errors: list[str] = []
    if not has_image:
        errors.append("Load an image first.")
    if not text or not text.strip():
        errors.append("Enter a watermark text.")
    if font_path is not None and not font_path.is_file():
        errors.append(f"Font file not found: {font_path}")
    return errors
