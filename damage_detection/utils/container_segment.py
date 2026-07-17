import os
import logging
import numpy as np
import torch
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

_predictor = None


def _model_path() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(
        os.path.join(current_dir, "../../../CV-series/models/sam/sam_vit_b_01ec64.pth")
    )


def _load_predictor():
    global _predictor
    if _predictor is not None:
        return _predictor

    try:
        from segment_anything import sam_model_registry, SamPredictor
    except ImportError:
        logger.warning("[SAM] segment-anything not installed. Run: pip install segment-anything")
        return None

    checkpoint = _model_path()
    if not os.path.exists(checkpoint):
        logger.warning(f"[SAM] Checkpoint not found at {checkpoint}")
        return None

    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        sam = sam_model_registry["vit_b"](checkpoint=checkpoint)
        sam.to(device=device)
        sam.eval()
        _predictor = SamPredictor(sam)
        logger.info(f"[SAM] SAM ViT-B loaded on {device}")
        return _predictor
    except Exception as e:
        logger.warning(f"[SAM] Failed to load SAM model: {e}")
        return None


def _heuristic_box(H: int, W: int) -> np.ndarray:
    """
    For fixed gate cameras the container fills most of the frame.
    Prime mover/chassis sits below; sky/background at the very edges.
    Returns [x1, y1, x2, y2] in pixel coords.
    """
    return np.array([
        int(W * 0.03), int(H * 0.05),
        int(W * 0.97), int(H * 0.88),
    ])


def segment_container(
    pil_img: Image.Image,
    debug_dir: str | None = None,
) -> np.ndarray | None:
    """
    Segments the container surface from a full gate-camera frame.

    Uses a heuristic bounding box as a SAM prompt so the model refines it
    to pixel-level accuracy, excluding the prime mover chassis and background.

    If debug_dir is set, saves three debug images there:
        sam_mask.png          — raw binary mask (white = container)
        sam_masked_image.png  — input with non-container pixels blacked out
        sam_overlay.png       — green overlay on original showing container region

    Returns:
        Binary mask (H, W) uint8 — 1 = container, 0 = everything else.
        None if SAM is unavailable or the result looks unreliable.
    """
    predictor = _load_predictor()
    if predictor is None:
        return None

    image_np = np.array(pil_img.convert("RGB"))
    H, W = image_np.shape[:2]
    box = _heuristic_box(H, W)

    print(f"[SAM] Heuristic box: {box.tolist()}  (image {W}x{H})")

    try:
        predictor.set_image(image_np)

        # multimask_output=True returns 3 masks at different granularities.
        # For large objects like containers we pick the LARGEST mask, not the
        # highest-scored one — the highest-scored mask often latches onto a small
        # high-confidence feature (door handle, logo) rather than the whole surface.
        masks, scores, _ = predictor.predict(
            point_coords=None,
            point_labels=None,
            box=box[None, :],   # SAM expects shape (1, 4)
            multimask_output=True,
        )

        best = int(np.argmax([m.sum() for m in masks]))  # largest mask
        mask = masks[best].astype(np.uint8)
        coverage = float(mask.mean() * 100)
        score = float(scores[best])

        print(f"[SAM] Mask coverage={coverage:.1f}%  score={score:.3f}")
        logger.info(f"[SAM] coverage={coverage:.1f}%  score={score:.3f}")

        if debug_dir:
            _save_debug(image_np, mask, box, debug_dir)

        # A very small mask means SAM picked up a tiny feature, not the container.
        # A near-100% mask means the box prompt wasn't refined at all.
        if coverage < 10 or coverage > 98:
            logger.warning(
                f"[SAM] Coverage {coverage:.1f}% outside 10–98% — "
                "discarding mask, falling back to full image."
            )
            return None

        return mask

    except Exception as e:
        logger.warning(f"[SAM] Segmentation failed: {e}")
        return None


def apply_container_mask(image_np: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Returns a copy of image_np with all non-container pixels set to black.
    image_np : (H, W, 3) uint8 RGB
    mask     : (H, W) uint8  — 1 = keep, 0 = discard
    """
    out = image_np.copy()
    out[mask == 0] = 0
    return out


def _save_debug(
    image_np: np.ndarray,
    mask: np.ndarray,
    box: np.ndarray,
    debug_dir: str,
) -> None:
    """Saves mask, masked image, and colour overlay to debug_dir for visual inspection."""
    os.makedirs(debug_dir, exist_ok=True)

    # 1. Raw mask
    Image.fromarray(mask * 255).save(os.path.join(debug_dir, "sam_mask.png"))

    # 2. Masked image (non-container = black)
    masked = image_np.copy()
    masked[mask == 0] = 0
    Image.fromarray(masked).save(os.path.join(debug_dir, "sam_masked_image.png"))

    # 3. Green overlay on original + heuristic box drawn in red
    overlay = Image.fromarray(image_np).convert("RGBA")
    green_layer = Image.new("RGBA", overlay.size, (0, 200, 0, 0))
    alpha = Image.fromarray((mask * 80).astype(np.uint8))   # 80/255 ≈ 31% opacity
    green_layer.putalpha(alpha)
    overlay = Image.alpha_composite(overlay, green_layer)

    draw = ImageDraw.Draw(overlay)
    x1, y1, x2, y2 = box.tolist()
    draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0, 255), width=3)
    overlay.convert("RGB").save(os.path.join(debug_dir, "sam_overlay.png"))

    print(f"[SAM] Debug images saved to {debug_dir}")
