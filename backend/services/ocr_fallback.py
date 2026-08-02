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

import shutil

try:
    import pytesseract
    TESSERACT_AVAILABLE = shutil.which('tesseract') is not None
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
        clean_buf = io.BytesIO()
        rgb_img = img.convert('RGB')

        # ── Preprocessing Pass 1: Upscale & Sharpen ───────────────────
        from PIL import ImageEnhance, ImageFilter
        width, height = rgb_img.size
        # Upscale 2.5x with Lanczos interpolation
        resized_img = rgb_img.resize((int(width * 2.5), int(height * 2.5)), Image.Resampling.LANCZOS)
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(resized_img)
        enhanced_img = enhancer.enhance(1.8)
        # Apply sharpening filter
        sharpened_img = enhanced_img.filter(ImageFilter.SHARPEN)

        sharpened_img.save(clean_buf, format='PNG')
        clean_buf.seek(0)
        clean_img = Image.open(clean_buf)

        # Multi-pass OCR: Pass 1 (PSM 6: Uniform block), Pass 2 (PSM 11: Sparse text)
        text_pass1 = pytesseract.image_to_string(clean_img, config='--psm 6').strip()
        text_pass2 = pytesseract.image_to_string(clean_img, config='--psm 11').strip()

        # Smart exact line deduplication across OCR passes
        lines_pass1 = [l.strip() for l in text_pass1.splitlines() if l.strip()]
        lines_pass2 = [l.strip() for l in text_pass2.splitlines() if l.strip()]

        unique_lines = list(lines_pass1)
        seen_lower = {l.lower() for l in lines_pass1}

        for line in lines_pass2:
            if line.lower() not in seen_lower:
                unique_lines.append(line)
                seen_lower.add(line.lower())

        combined_text = '\n'.join(unique_lines)
        return OCRResult(text=combined_text.strip(), available=True)





    except Exception as exc:
        return OCRResult(text='', available=False, error=f'OCR failed: {exc}')
