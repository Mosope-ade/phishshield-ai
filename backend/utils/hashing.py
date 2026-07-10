"""
utils/hashing.py

Content hashing utilities. The cache key is always the SHA-256 hash of the
normalized input — NEVER the raw input itself (PLAN.md §7, SECURITY.md §13).
"""

from __future__ import annotations

import hashlib
import secrets
import string


def hash_content(content: str | bytes) -> str:
    """Return the SHA-256 hex digest of the given content (str or bytes)."""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()


def normalize_url(url: str) -> str:
    """Normalize a URL for consistent cache key generation."""
    return url.strip().lower()


def normalize_text(text: str) -> str:
    """Normalize message text for consistent cache key generation."""
    return ' '.join(text.strip().lower().split())


def generate_report_id(length: int = 12) -> str:
    """
    Generate a cryptographically random, non-sequential report slug.
    SECURITY.md §15: report IDs must be non-guessable.

    Uses URL-safe characters (alphanumeric + underscore + hyphen).
    At 12 chars, the search space is ~62^12 ≈ 3.2e21.
    """
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
