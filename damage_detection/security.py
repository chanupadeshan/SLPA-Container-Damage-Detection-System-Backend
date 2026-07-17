from PIL import Image, UnidentifiedImageError
from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission


ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/pjpeg",
}

# Mobile browsers / WebViews often omit type or send a generic one.
LAX_IMAGE_CONTENT_TYPES = {
    "",
    "application/octet-stream",
    "binary/octet-stream",
}


class HasApiKey(BasePermission):
    """
    Protect expensive ML/OCR endpoints with a shared API key.

    Local development remains usable when DEBUG=True and API_KEY is unset.
    Production startup requires API_KEY, so this endpoint is not accidentally public.
    """

    message = "Invalid or missing API key."

    def has_permission(self, request, view):
        api_key = getattr(settings, "API_KEY", "")
        if not api_key and settings.DEBUG:
            return True
        return request.headers.get("X-API-Key") == api_key


def load_validated_image(file_obj) -> Image.Image:
    if not file_obj:
        raise ValidationError("No file provided.")

    max_bytes = settings.MAX_IMAGE_UPLOAD_BYTES
    if file_obj.size > max_bytes:
        raise ValidationError(
            f"Image is too large. Maximum allowed size is {max_bytes // (1024 * 1024)} MB."
        )

    content_type = (getattr(file_obj, "content_type", "") or "").lower().strip()
    if (
        content_type
        and content_type not in ALLOWED_IMAGE_CONTENT_TYPES
        and content_type not in LAX_IMAGE_CONTENT_TYPES
    ):
        raise ValidationError("Unsupported image type. Use JPEG, PNG, or WebP.")

    Image.MAX_IMAGE_PIXELS = settings.MAX_IMAGE_PIXELS

    try:
        file_obj.seek(0)
        probe = Image.open(file_obj)
        probe.verify()

        file_obj.seek(0)
        img = Image.open(file_obj)
        img.load()
    except Image.DecompressionBombError as exc:
        raise ValidationError("Image dimensions are too large.") from exc
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError("Invalid or corrupted image file.") from exc

    # If Content-Type was missing/generic, accept only real image formats.
    if content_type in LAX_IMAGE_CONTENT_TYPES:
        fmt = (img.format or "").upper()
        if fmt not in {"JPEG", "PNG", "WEBP"}:
            raise ValidationError("Unsupported image type. Use JPEG, PNG, or WebP.")

    if img.width > settings.MAX_IMAGE_WIDTH or img.height > settings.MAX_IMAGE_HEIGHT:
        raise ValidationError(
            f"Image dimensions are too large. Maximum is {settings.MAX_IMAGE_WIDTH}x{settings.MAX_IMAGE_HEIGHT}."
        )

    if img.mode != "RGB":
        img = img.convert("RGB")

    return img
