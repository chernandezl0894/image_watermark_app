"""User-facing validation of form input, kept out of the domain and the view."""


def validate_request(text: str, *, has_image: bool) -> list[str]:
    """Return friendly messages for invalid form input.

    An empty list means the input is valid.
    """
    errors: list[str] = []
    if not has_image:
        errors.append("Load an image first.")
    if not text or not text.strip():
        errors.append("Enter a watermark text.")
    return errors
