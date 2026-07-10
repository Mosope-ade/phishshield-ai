"""
heuristics/typosquat.py

Detects typosquatting: the registered domain is suspiciously close (Levenshtein
distance ≤ 2) to a well-known domain from the bundled Tranco top-domains list.

Key design choices:
- Only the registered domain (not full hostname) is compared, so legitimate
  subdomains of a top domain aren't flagged.
- We skip the comparison when the registered domain *is* the top domain — that's
  a match, not a typosquat.
- Distance 0 exact-match → the domain IS the legitimate one → not flagged.
- Distance 1–2 → flagged as potential typosquat.
"""

from __future__ import annotations

import os
import csv
import functools
from dataclasses import dataclass, field
from Levenshtein import distance as levenshtein_distance  # python-Levenshtein

# ── Data loading ──────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
TRANCO_CSV = os.path.join(DATA_DIR, "tranco_top_domains.csv")

# Maximum Levenshtein distance to flag as a typosquat (inclusive)
TYPOSQUAT_DISTANCE_THRESHOLD = 2


@functools.lru_cache(maxsize=1)
def _load_top_domains() -> frozenset[str]:
    """
    Load the bundled Tranco top-domains CSV.  File format expected:
      rank,domain
      1,google.com
      2,youtube.com
      ...

    Returns a frozenset of lowercase registered domain strings (no scheme,
    no subdomain, no trailing dot).  Cached after first call.
    """
    domains: set[str] = set()
    try:
        with open(TRANCO_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                domain = row.get("domain", "").strip().lower()
                if domain:
                    domains.add(domain)
    except FileNotFoundError:
        # Fail open so the rest of the heuristics still work during development
        # before the data file is present.  Tests will catch this via fixture.
        pass
    return frozenset(domains)


# ── Result type ───────────────────────────────────────────────────────────────


@dataclass
class TyposquatResult:
    detected: bool = False
    notes: list[str] = field(default_factory=list)


# ── Public check ─────────────────────────────────────────────────────────────


def check_typosquatting(registered_domain: str) -> TyposquatResult:
    """
    Compare registered_domain against every domain in the top-domains list.
    Flag if Levenshtein distance is 1 or 2 (not 0 — that's the real domain).

    Parameters
    ----------
    registered_domain : str
        The eTLD+1 portion extracted by tldextract (e.g. "go0gle.com").

    Returns
    -------
    TyposquatResult
    """
    if not registered_domain:
        return TyposquatResult()

    candidate = registered_domain.lower()
    top_domains = _load_top_domains()

    # Exact match → legitimate, not a typosquat
    if candidate in top_domains:
        return TyposquatResult()

    closest_domain: str | None = None
    min_dist = TYPOSQUAT_DISTANCE_THRESHOLD + 1  # start above threshold

    for top_domain in top_domains:
        # Skip comparing domains of very different lengths early — a domain that
        # differs by more than threshold characters in length cannot be within
        # threshold edit distance.
        if abs(len(candidate) - len(top_domain)) > TYPOSQUAT_DISTANCE_THRESHOLD:
            continue

        dist = levenshtein_distance(candidate, top_domain)

        if 0 < dist <= TYPOSQUAT_DISTANCE_THRESHOLD:
            if dist < min_dist:
                min_dist = dist
                closest_domain = top_domain

    if closest_domain is not None:
        return TyposquatResult(
            detected=True,
            notes=[
                f"[Heuristics] Possible typosquat: '{candidate}' is {min_dist} edit(s) "
                f"away from '{closest_domain}' (a top-ranked domain)."
            ],
        )

    return TyposquatResult()
