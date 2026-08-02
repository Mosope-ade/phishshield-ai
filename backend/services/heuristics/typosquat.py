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
    Also checks base brand tokens (e.g. "paypa1" in "paypa1-verify.xyz" or "arnaz0n" in "arnaz0n-support.com").
    """
    if not registered_domain:
        return TyposquatResult()

    candidate = registered_domain.lower()
    top_domains = _load_top_domains()

    # Exact match → legitimate, not a typosquat
    if candidate in top_domains:
        return TyposquatResult()

    # Extract base domain name without TLD (e.g. "paypa1-verify" from "paypa1-verify.xyz")
    cand_base = candidate.split('.')[0]

    # Pre-extract base brand names from top domains for apples-to-apples comparison
    top_brands = {td.split('.')[0]: td for td in top_domains}

    # Extract potential brand tokens if domain is hyphenated (e.g. ["paypa1", "verify"])
    cand_tokens = cand_base.split('-') if '-' in cand_base else [cand_base]

    closest_domain: str | None = None
    min_dist = TYPOSQUAT_DISTANCE_THRESHOLD + 1
    matched_cand_part = candidate

    for token in cand_tokens:
        if len(token) < 3:
            continue

        for top_brand, full_top_domain in top_brands.items():
            # Skip exact matches on legit brand tokens (e.g. "support" in "paypal-support.com")
            if token == top_brand:
                continue

            if abs(len(token) - len(top_brand)) > TYPOSQUAT_DISTANCE_THRESHOLD:
                continue

            dist = levenshtein_distance(token, top_brand)

            if 0 < dist <= TYPOSQUAT_DISTANCE_THRESHOLD:
                if dist < min_dist:
                    min_dist = dist
                    closest_domain = full_top_domain
                    matched_cand_part = token

    if closest_domain is not None:
        return TyposquatResult(
            detected=True,
            notes=[
                f"[Heuristics] Possible typosquat: '{matched_cand_part}' in '{candidate}' is {min_dist} edit(s) "
                f"away from top domain '{closest_domain}'."
            ],
        )

    return TyposquatResult()

