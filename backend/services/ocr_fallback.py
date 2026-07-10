"""
services/ocr_fallback.py

Fallback OCR using Tesseract when the configured vision LLM is unavailable.
Used by the screenshot analysis pipeline (§4.4) when supports_vision() is False.

SECURITY.md §8 controls applied: same decompression-bomb protection and
EXIF stripping as qr_decode.py.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Optional

from PIL import Image

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Decompression-bomb protection (SECURITY.md §8)
Image.MAX_IMAGE_PIXELS = 89_478_485


@dataclass
class OCRResult:
    text: str
    available: bool
    error: Optional[str] = None


def extract_text_from_image(image_bytes: bytes) -> OCRResult:
    """
    Extract plain text from an image using Tesseract OCR.

    Returns OCRResult with available=False if Tesseract is not installed.
    The extracted text is treated as untrusted user-influenced content
    (SECURITY.md §5) — callers must sanitize before rendering.
    """
    if not TESSERACT_AVAILABLE:
        return OCRResult(
            text='',
            available=False,
            error='pytesseract/Tesseract not installed; OCR fallback unavailable.'
        )

    try:
        img = Image.open(io.BytesIO(image_bytes))
        # Strip EXIF by re-saving to buffer (SECURITY.md §8)
        clean_buf = io.BytesIO()
        rgb_img = img.convert('RGB')
        rgb_img.save(clean_buf, format='PNG')
        clean_buf.seek(0)
        clean_img = Image.open(clean_buf)

        text = pytesseract.image_to_string(clean_img)
        return OCRResult(text=text.strip(), available=True)
    except Exception as exc:
        return OCRResult(text='', available=False, error=f'OCR failed: {exc}')
