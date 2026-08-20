from io import BytesIO

from PIL import Image, UnidentifiedImageError


MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
ALLOWED_IMAGE_FORMATS = {"PNG", "JPEG"}


class ImageValidationError(ValueError):
    """Raised when an uploaded image is unsafe or unsupported."""


def load_validated_image(file_bytes: bytes, file_name: str) -> Image.Image:
    if not file_bytes:
        raise ImageValidationError("The uploaded image is empty.")
    if len(file_bytes) > MAX_IMAGE_BYTES:
        raise ImageValidationError("The uploaded image exceeds the 5 MB limit.")
    if not str(file_name).lower().endswith((".png", ".jpg", ".jpeg")):
        raise ImageValidationError("Only PNG and JPEG images are supported.")

    try:
        with Image.open(BytesIO(file_bytes)) as probe:
            if probe.format not in ALLOWED_IMAGE_FORMATS:
                raise ImageValidationError("The image content is not PNG or JPEG.")
            width, height = probe.size
            if width * height > MAX_IMAGE_PIXELS:
                raise ImageValidationError("The image dimensions are too large.")
            probe.verify()

        image = Image.open(BytesIO(file_bytes))
        image.load()
        return image
    except ImageValidationError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageValidationError("The uploaded image is invalid or corrupted.") from exc
