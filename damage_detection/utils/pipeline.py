import os
import numpy as np
from PIL import Image
from .yolo_damage import run_damage_detection

def detect_damage_in_image(pil_img: Image.Image, save_debug=False, debug_dir=None):
    """
    Simplified entry point using YOLO directly on the original image.
    pil_img: PIL Image (Must be RGB)
    """
    
    print("[Pipeline] Running YOLO damage detection on full image...")
    
    # Ensure image is a numpy array for YOLO
    image_np = np.array(pil_img).astype(np.uint8)
    if image_np.shape[2] == 4:  # handle RGBA if any
        image_np = image_np[:, :, :3]

    # Run YOLO on the original image
    detections = run_damage_detection(image_np, conf=0.25)
    
    # Normalized coordinates returned by run_damage_detection are already relative to full image
    print(f"[Pipeline] YOLO detections: {len(detections)}")
    return detections
