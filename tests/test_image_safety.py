from io import BytesIO

import pytest
from PIL import Image

from image_safety import ImageValidationError, load_validated_image


def test_valid_png_is_loaded():
    buffer = BytesIO()
    Image.new("RGB", (20, 10), "red").save(buffer, format="PNG")
    image = load_validated_image(buffer.getvalue(), "rack.png")
    assert image.size == (20, 10)


def test_fake_image_is_rejected():
    with pytest.raises(ImageValidationError):
        load_validated_image(b"not an image", "rack.png")


def test_wrong_extension_is_rejected():
    with pytest.raises(ImageValidationError):
        load_validated_image(b"content", "rack.svg")
