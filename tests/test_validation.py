from image_watermark_app.application import validate_request


def test_valid_input_has_no_errors() -> None:
    assert validate_request("Crissis", has_image=True) == []


def test_missing_image_is_reported() -> None:
    assert validate_request("Crissis", has_image=False) == ["Load an image first."]


def test_empty_text_is_reported() -> None:
    assert validate_request("   ", has_image=True) == ["Enter a watermark text."]


def test_all_problems_are_reported_in_order() -> None:
    assert validate_request("", has_image=False) == [
        "Load an image first.",
        "Enter a watermark text.",
    ]
