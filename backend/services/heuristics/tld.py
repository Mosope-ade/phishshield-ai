"""
heuristics/tld.py

Flags domains using TLDs from a curated suspicious-TLD list.

IMPORTANT: a suspicious TLD is a contributing signal only, never standalone
proof of malice. The notes text makes this explicit so the AI layer (which
receives these notes as context) does not over-weight it.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
SUSPICIOUS_TLDS_FILE = os.path.join(DATA_DIR, 'suspicious_tlds.txt')


def _load_suspicious_tlds() -> frozenset[str]:
    try:
        with open(SUSPICIOUS_TLDS_FILE, encoding='utf-8') as f:
            return frozenset(
                line.strip().lower().lstrip('.')
                for line in f
                if line.strip() and not line.startswith('#')
            )
    except FileNotFoundError:
        return frozenset()


# Module-level constant — loaded once
_SUSPICIOUS_TLDS: frozenset[str] = _load_suspicious_tlds()


@dataclass
class TLDResult:
    detected: bool = False
    notes: list[str] = field(default_factory=list)


def check_suspicious_tld(suffix: str) -> TLDResult:
    """
    Check whether the TLD (suffix) is in the curated suspicious-TLD list.

    Parameters
    ----------
    suffix : str
        The TLD portion extracted by tldextract (e.g. 'xyz', 'com', 'co.uk').
    """
    if not suffix:
        return TLDResult()

    tld = suffix.lower().lstrip('.')
    # For compound TLDs like 'co.uk', check only the rightmost label
    rightmost = tld.split('.')[-1]

    if rightmost in _SUSPICIOUS_TLDS or tld in _SUSPICIOUS_TLDS:
        matched = tld if tld in _SUSPICIOUS_TLDS else rightmost
        return TLDResult(
            detected=True,
            notes=[
                f"[Heuristics] TLD '.{matched}' is on the suspicious-TLD list. "
                "This is a contributing signal, not standalone proof of malice."
            ],
        )

    return TLDResult()
