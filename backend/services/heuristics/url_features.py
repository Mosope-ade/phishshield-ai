"""
heuristics/url_features.py

Detects suspicious URL structural features:
- Excessive URL length (>100 chars)
- Raw IP address as host
- Known URL shortener domain
- HTTP (not HTTPS) — contributing signal only, not proof of safety either way
- Brand/trigger keyword in the URL path or query string

All findings are labeled as contributing signals, not standalone verdicts.
"""

from __future__ import annotations

import os
import re
import socket
from dataclasses import dataclass, field
from urllib.parse import urlparse

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
SHORTENER_FILE = os.path.join(DATA_DIR, 'shortener_domains.txt')
KEYWORDS_FILE = os.path.join(DATA_DIR, 'brand_keywords.txt')

URL_LENGTH_THRESHOLD = 100

# IPv4 pattern (raw IP as hostname)
_IPV4_RE = re.compile(
    r'^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$'
)


def _load_set_from_file(filepath: str) -> frozenset[str]:
    try:
        with open(filepath, encoding='utf-8') as f:
            return frozenset(
                line.strip().lower()
                for line in f
                if line.strip() and not line.startswith('#')
            )
    except FileNotFoundError:
        return frozenset()


_SHORTENER_DOMAINS: frozenset[str] = _load_set_from_file(SHORTENER_FILE)
_BRAND_KEYWORDS: frozenset[str] = _load_set_from_file(KEYWORDS_FILE)


@dataclass
class URLFeaturesResult:
    detected: bool = False
    notes: list[str] = field(default_factory=list)


def check_url_features(
    full_url: str, full_hostname: str, registered_domain: str
) -> URLFeaturesResult:
    """
    Check a URL for multiple structural red-flag features.

    Parameters
    ----------
    full_url : str
        The complete URL string.
    full_hostname : str
        The full hostname (subdomain + registered domain).
    registered_domain : str
        The eTLD+1 (used for shortener check).
    """
    result = URLFeaturesResult()

    try:
        parsed = urlparse(full_url)
    except Exception:
        result.notes.append('[Heuristics] URL could not be parsed.')
        result.detected = True
        return result

    # ── Length ───────────────────────────────────────────────────────────────
    if len(full_url) > URL_LENGTH_THRESHOLD:
        result.notes.append(
            f'[Heuristics] URL is {len(full_url)} characters long (>{URL_LENGTH_THRESHOLD}): '
            'excessively long URLs are a contributing phishing indicator.'
        )
        result.detected = True

    # ── Raw IP address as hostname ────────────────────────────────────────────
    hostname = parsed.hostname or ''
    if _IPV4_RE.match(hostname):
        result.notes.append(
            f'[Heuristics] Raw IPv4 address used as hostname ({hostname}): '
            'legitimate services almost never use raw IPs in user-facing URLs.'
        )
        result.detected = True

    # ── Known URL shortener ───────────────────────────────────────────────────
    if registered_domain.lower() in _SHORTENER_DOMAINS or full_hostname.lower() in _SHORTENER_DOMAINS:
        result.notes.append(
            f'[Heuristics] Known URL shortener domain detected ({registered_domain}): '
            'the real destination is hidden; will attempt to resolve the redirect chain.'
        )
        result.detected = True

    # ── HTTP (not HTTPS) ─────────────────────────────────────────────────────
    if parsed.scheme == 'http':
        result.notes.append(
            '[Heuristics] URL uses HTTP (not HTTPS): a contributing signal. '
            'Note: HTTPS alone does not guarantee a site is safe.'
        )
        result.detected = True

    # ── Brand/trigger keyword in path or query ────────────────────────────────
    path_and_query = ((parsed.path or '') + '?' + (parsed.query or '')).lower()
    found_keywords: list[str] = []
    for kw in _BRAND_KEYWORDS:
        # Use word-boundary-aware check for keywords
        if re.search(r'(?<![a-z])' + re.escape(kw) + r'(?![a-z])', path_and_query):
            found_keywords.append(kw)

    if found_keywords:
        kw_str = ', '.join(f"'{k}'" for k in sorted(found_keywords))
        result.notes.append(
            f'[Heuristics] Trigger keywords found in URL path/query ({kw_str}): '
            'combined with other signals, these suggest a credential-harvesting page.'
        )
        result.detected = True

    return result
