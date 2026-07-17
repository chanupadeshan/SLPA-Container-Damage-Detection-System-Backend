import re
import shutil
import subprocess
import tempfile
from collections import Counter

import cv2
import numpy as np
from PIL import Image


CONTAINER_NUMBER_PATTERN = re.compile(r"[A-Z]{4}\d{7}")


def _normalize_ocr_text(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (text or "").upper())


def _iso6346_check_digit_is_valid(container_number: str) -> bool:
    """
    Validate an ISO 6346 container number.
    Format: 4 letters + 6 serial digits + 1 check digit, e.g. MSCU1234567.
    """
    if not CONTAINER_NUMBER_PATTERN.fullmatch(container_number):
        return False

    letter_values = {
        "A": 10, "B": 12, "C": 13, "D": 14, "E": 15, "F": 16, "G": 17,
        "H": 18, "I": 19, "J": 20, "K": 21, "L": 23, "M": 24, "N": 25,
        "O": 26, "P": 27, "Q": 28, "R": 29, "S": 30, "T": 31, "U": 32,
        "V": 34, "W": 35, "X": 36, "Y": 37, "Z": 38,
    }

    total = 0
    for idx, char in enumerate(container_number[:10]):
        value = letter_values[char] if char.isalpha() else int(char)
        total += value * (2 ** idx)

    check_digit = total % 11
    if check_digit == 10:
        check_digit = 0

    return check_digit == int(container_number[-1])


def _candidate_numbers(text: str) -> list[str]:
    normalized = _normalize_ocr_text(text)
    candidates = set(CONTAINER_NUMBER_PATTERN.findall(normalized))

    # OCR often inserts/removes separators, so also scan sliding windows.
    for idx in range(max(0, len(normalized) - 10)):
        window = normalized[idx:idx + 11]
        if CONTAINER_NUMBER_PATTERN.fullmatch(window):
            candidates.add(window)

    return list(candidates)


def _preprocess_variants(pil_img: Image.Image) -> list[np.ndarray]:
    rgb = np.array(pil_img.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    max_side = max(bgr.shape[:2])
    if max_side > 1800:
        scale = 1800 / max_side
        bgr = cv2.resize(bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    variants = []
    variants.append(gray)

    # Upscale to help OCR on container markings.
    scaled = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    variants.append(scaled)

    denoised = cv2.bilateralFilter(scaled, 9, 75, 75)
    variants.append(denoised)

    variants.append(cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1])
    # Strong contrast can help with faded/painted text.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(scaled)
    variants.append(clahe)

    return variants


def _run_tesseract(image: np.ndarray, psm: int) -> str:
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        cv2.imwrite(tmp.name, image)
        command = [
            "tesseract",
            tmp.name,
            "stdout",
            "--psm",
            str(psm),
            "-c",
            "tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        ]
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        return completed.stdout or ""


def extract_container_number(pil_img: Image.Image) -> dict:
    """
    Best-effort OCR extraction for ISO 6346 container numbers.
    Returns a small result object and never raises for normal OCR failures.
    """
    if not shutil.which("tesseract"):
        return {
            "number": None,
            "candidates": [],
            "error": "tesseract executable not found",
        }

    counter = Counter()

    try:
        for image in _preprocess_variants(pil_img):
            for psm in (6, 11, 12):
                text = _run_tesseract(image, psm)
                for candidate in _candidate_numbers(text):
                    score = 3 if _iso6346_check_digit_is_valid(candidate) else 1
                    counter[candidate] += score
    except Exception as exc:
        return {
            "number": None,
            "candidates": [],
            "error": str(exc),
        }

    candidates = [candidate for candidate, _ in counter.most_common(5)]
    valid_candidates = [
        candidate for candidate in candidates
        if _iso6346_check_digit_is_valid(candidate)
    ]

    return {
        "number": valid_candidates[0] if valid_candidates else (candidates[0] if candidates else None),
        "candidates": candidates,
        "error": None,
    }
