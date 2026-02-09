import os
import logging
from PIL import Image
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .utils.pipeline import detect_damage_in_image

logger = logging.getLogger(__name__)

class DetectDamageView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        """
        Expects a multipart/form-data request with a 'file' field containing the image.
        Optional 'debug' parameter to enable debug visualizations.
        """
        if 'file' not in request.FILES:
             return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['file']
        debug_mode = request.POST.get('debug', 'false').lower() == 'true'
        
        print(f"[View] Debug mode: {debug_mode}")
        print(f"[View] POST params: {request.POST}")
        
        try:
            img = Image.open(file_obj)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Set up debug directory
            debug_dir = None
            if debug_mode:
                debug_dir = os.path.join(settings.MEDIA_ROOT, 'debug')
                os.makedirs(debug_dir, exist_ok=True)
            
            # Run detection pipeline
            result = detect_damage_in_image(img, save_debug=debug_mode, debug_dir=debug_dir)
            
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
                
                return Response({
                    "success": True,
                    "filename": file_obj.name,
                    "damages": detections,
                    "debug_images": debug_urls
                }, status=status.HTTP_200_OK)
            else:
                detections = result if not isinstance(result, tuple) else result[0]
                return Response({
                    "success": True,
                    "filename": file_obj.name,
                    "damages": detections
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error during damage detection for file {file_obj.name}")
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
