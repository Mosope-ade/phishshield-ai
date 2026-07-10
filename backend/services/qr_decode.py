"""
services/qr_decode.py

QR code decoding via pyzbar + Pillow.
Applies decompression-bomb protection and EXIF stripping before processing.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Optional

from PIL import Image

try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

# Decompression-bomb protection (SECURITY.md §8)
Image.MAX_IMAGE_PIXELS = 89_478_485  # ~8000x8000 @ 1px


@dataclass
class QRDecodeResult:
    found: bool
    payload: Optional[str] = None  # Raw decoded string
    is_url: bool = False           # True if payload looks like a URL
    error: Optional[str] = None


def _strip_exif_and_load(image_bytes: bytes) -> Image.Image:
    """
    Load image from bytes, stripping any EXIF metadata before processing.
    SECURITY.md §8: uploaded images may contain location/device metadata.
    """
    img = Image.open(io.BytesIO(image_bytes))
    # Create a clean copy without EXIF by saving to a buffer as RGB
    # (no EXIF in a raw pixel copy)
    mode = img.mode if img.mode in ('RGB', 'RGBA', 'L') else 'RGB'
    clean = Image.new(mode, img.size)
    clean.paste(img)
    return clean


def decode_qr(image_bytes: bytes) -> QRDecodeResult:
    """
    Attempt to decode a QR code from the given image bytes.

    Returns a QRDecodeResult with:
    - found=True if a QR code was detected
    - payload: the decoded string
    - is_url: True if the payload starts with http:// or https://

    SECURITY.md §8 controls applied:
    - MAX_IMAGE_PIXELS set at module level (decompression-bomb protection)
    - EXIF stripped before processing
    - Does NOT write image to disk
    """
    if not PYZBAR_AVAILABLE:
        return QRDecodeResult(
            found=False,
            error='pyzbar library not installed; QR decoding unavailable.'
        )

    try:
        img = _strip_exif_and_load(image_bytes)
    except Exception as exc:
        return QRDecodeResult(found=False, error=f'Image load failed: {exc}')

    try:
        decoded_list = pyzbar_decode(img)
    except Exception as exc:
        return QRDecodeResult(found=False, error=f'QR decode failed: {exc}')

    if not decoded_list:
        return QRDecodeResult(found=False)

    # Take the first QR code found (most images have only one)
    first = decoded_list[0]
    try:
        payload = first.data.decode('utf-8', errors='replace')
    except Exception:
        payload = str(first.data)

    is_url = payload.lower().startswith(('http://', 'https://'))

    return QRDecodeResult(found=True, payload=payload, is_url=is_url)
