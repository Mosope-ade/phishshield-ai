"""
utils/limiter.py

Shared slowapi Limiter instance to prevent circular imports between
main.py and analyze.py.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared rate limiter instance using client IP and enabling rate limit response headers
limiter = Limiter(key_func=get_remote_address, headers_enabled=True)
