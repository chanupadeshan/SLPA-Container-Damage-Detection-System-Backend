import os
import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.uploadedfile import SimpleUploadedFile
import base64
import binascii
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .security import HasApiKey, load_validated_image

logger = logging.getLogger(__name__)


class OCRContainerView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (HasApiKey,)
    throttle_scope = "ocr"

    def post(self, request, *args, **kwargs):
        from .utils.container_ocr import extract_container_number

        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.FILES['file']

        try:
            img = load_validated_image(file_obj)
            result = extract_container_number(img)

            return Response({
                "success": result["number"] is not None,
                "container_id": result["number"],
                "candidates": result["candidates"],
                "error": result["error"],
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"success": False, "error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Error during container OCR")
            return Response({
                "success": False,
                "error": "Container OCR failed. Please try again.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DetectDamageView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = (HasApiKey,)
    throttle_scope = "detect"

    def post(self, request, *args, **kwargs):
        """
        Accepts either:
        - multipart/form-data with a 'file' field (desktop browsers), or
        - JSON { image_base64, filename? } (Android WebView / Expo — more reliable).
        """
        from .utils.pipeline import detect_damage_in_image
        from .utils.container_ocr import extract_container_number

        file_obj = None
        if "file" in request.FILES:
            file_obj = request.FILES["file"]
        else:
            raw_b64 = request.data.get("image_base64") or request.data.get("file_base64")
            if raw_b64:
                try:
                    if isinstance(raw_b64, str) and "," in raw_b64:
                        raw_b64 = raw_b64.split(",", 1)[1]
                    raw_bytes = base64.b64decode(raw_b64)
                except (binascii.Error, ValueError, TypeError):
                    return Response(
                        {"error": "Invalid base64 image payload."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                filename = request.data.get("filename") or "upload.jpg"
                content_type = request.data.get("content_type") or "image/jpeg"
                file_obj = SimpleUploadedFile(filename, raw_bytes, content_type=content_type)

        if file_obj is None:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        debug_mode = False
        if hasattr(request.data, "get"):
            debug_mode = str(request.data.get("debug", "false")).lower() == "true"
        if not debug_mode:
            debug_mode = request.POST.get("debug", "false").lower() == "true"
        debug_mode = debug_mode and settings.DEBUG

        try:
            img = load_validated_image(file_obj)

            # Set up debug directory
            debug_dir = None
            if debug_mode:
                debug_dir = os.path.join(settings.MEDIA_ROOT, "debug")
                os.makedirs(debug_dir, exist_ok=True)

            # Run detection pipeline
            result = detect_damage_in_image(img, save_debug=debug_mode, debug_dir=debug_dir)
            ocr_result = extract_container_number(img)

            # Handle response based on debug mode
            if debug_mode and isinstance(result, tuple):
                detections, debug_paths = result
                # Convert absolute paths to URLs
                debug_urls = {}
                for key, path in debug_paths.items():
                    rel_path = os.path.relpath(path, settings.MEDIA_ROOT)
                    debug_urls[key] = request.build_absolute_uri(
                        settings.MEDIA_URL + rel_path
                    )

                return Response(
                    {
                        "success": True,
                        "filename": file_obj.name,
                        "damages": detections,
                        "container_number": ocr_result.get("number"),
                        "container_number_candidates": ocr_result.get("candidates", []),
                        "container_number_ocr_error": ocr_result.get("error"),
                        "debug_images": debug_urls,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                detections = result if not isinstance(result, tuple) else result[0]
                return Response(
                    {
                        "success": True,
                        "filename": file_obj.name,
                        "damages": detections,
                        "container_number": ocr_result.get("number"),
                        "container_number_candidates": ocr_result.get("candidates", []),
                        "container_number_ocr_error": ocr_result.get("error"),
                    },
                    status=status.HTTP_200_OK,
                )

        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "error": e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception(f"Error during damage detection for file {file_obj.name}")
            return Response(
                {
                    "success": False,
                    "error": "Damage detection failed. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
