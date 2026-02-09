import os
import numpy as np
from ultralytics import YOLO
from django.conf import settings

_damage_model = None


def get_damage_model():
    global _damage_model
    if _damage_model is None:
        # Construct path relative to this file's directory to be more robust
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # pipeline.py is in Backend/damage_detection/utils/
        # base_dir is Backend/
        # CV-series is at the same level as Backend/
        model_path = os.path.abspath(
            os.path.join(current_dir, "../../../CV-series/models/yolo_damage/best.pt")
        )

        if not os.path.exists(model_path):
            # Fallback to settings.BASE_DIR if available
            try:
                model_path = os.path.abspath(
                    os.path.join(settings.BASE_DIR, "../CV-series/models/yolo_damage/best.pt")
                )
            except Exception:
                pass

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"YOLO damage model not found at {model_path}")

        print(f"[YOLO] Loading damage model: {model_path}")
        try:
            _damage_model = YOLO(model_path)
            # Use GPU if available
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _damage_model.to(device)
            print(f"[YOLO] Model loaded successfully on {device}.")
        except Exception as e:
            print(f"[YOLO] Failed to load model: {e}")
            raise

    return _damage_model


def run_damage_detection(image_rgb: np.ndarray, conf: float = 0.25):
    """
    image_rgb: numpy array (H,W,3) uint8 RGB
    returns: list of {label, confidence, box(normalized xyxy)}
    """
    model = get_damage_model()

    results = model.predict(image_rgb, conf=conf)

    detections = []
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            detections.append({
                "label": model.names[cls_id],
                "confidence": float(box.conf[0]),
                "box": box.xyxyn[0].tolist()  # normalized xyxy
            })
    return detections
