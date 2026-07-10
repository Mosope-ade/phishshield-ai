"""
utils/sanitize.py

Text sanitization utilities. Used when preparing content for the frontend
(SECURITY.md §5: untrusted content must be rendered as text, never raw HTML).

Note: the primary XSS defense is in the React frontend (rendering text nodes,
not dangerouslySetInnerHTML). These server-side utilities provide defense-in-
depth and are used when generating the report's highlighted_phrases.
"""

from __future__ import annotations

import re

# Characters that could be dangerous if mishandled in downstream contexts
_HTML_ESCAPE_TABLE = str.maketrans({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
})


def escape_html(text: str) -> str:
    """HTML-escape a string. Use when generating any text that will be
    embedded in an HTML context."""
    return text.translate(_HTML_ESCAPE_TABLE)


def strip_null_bytes(text: str) -> str:
    """Remove null bytes that could cause issues in DB storage or string handling."""
    return text.replace('\x00', '')


def sanitize_for_log(text: str, max_length: int = 100) -> str:
    """
    Produce a safe, truncated representation of untrusted text for logging.
    SECURITY.md §13: never log raw user content.
    Returns only a length + hash summary, not the content itself.
    """
    from .hashing import hash_content
    content_hash = hash_content(text)[:8]  # Short prefix for log correlation
    return f'[content_hash={content_hash}, length={len(text)}]'
