import numpy as np
from PIL import Image
from .yolo_damage import run_damage_detection
from .container_segment import segment_container


def detect_damage_in_image(pil_img: Image.Image, save_debug=False, debug_dir=None):
    """
    Full inspection pipeline:
      1. YOLO runs on the full image and finds all candidate damages.
      2. SAM segments the container surface.
      3. Any detection whose bounding box overlaps less than 40% with the
         container mask is discarded as a false positive (prime mover / background).

    Running YOLO first means SAM segmentation errors never cause missed damages —
    they can only cause a false positive to slip through, which is far less harmful.
    Falls back to returning all YOLO detections if SAM is unavailable.
    """
    image_np = np.array(pil_img).astype(np.uint8)
    if image_np.ndim == 3 and image_np.shape[2] == 4:
        image_np = image_np[:, :, :3]

    H, W = image_np.shape[:2]

    # Step 1: damage detection on the full image
    print("[Pipeline] Running YOLO damage detection on full image...")
    detections = run_damage_detection(image_np, conf=0.25)
    print(f"[Pipeline] YOLO found {len(detections)} candidate damage(s).")

    if not detections:
        return detections

    # Step 2: container segmentation for false-positive filtering
    print("[Pipeline] Segmenting container region with SAM...")
    mask = segment_container(
        pil_img,
        debug_dir=debug_dir if save_debug else None,
    )

    if mask is None:
        print("[Pipeline] No mask available — returning all YOLO detections.")
        return detections

    # Step 3: filter out detections that sit mostly outside the container mask
    kept, dropped = [], []
    for det in detections:
        x1n, y1n, x2n, y2n = det["box"]
        x1 = max(0, int(x1n * W))
        y1 = max(0, int(y1n * H))
        x2 = min(W, int(x2n * W))
        y2 = min(H, int(y2n * H))

        region = mask[y1:y2, x1:x2]
        overlap = float(region.mean()) if region.size > 0 else 0.0

        if overlap >= 0.20:
            kept.append(det)
        else:
            dropped.append((det["label"], round(overlap * 100, 1)))

    if dropped:
        for label, pct in dropped:
            print(f"[Pipeline] Dropped '{label}' — only {pct}% inside container mask (likely truck/background).")

    print(f"[Pipeline] After filtering: {len(kept)}/{len(detections)} damage(s) on container.")
    return kept
