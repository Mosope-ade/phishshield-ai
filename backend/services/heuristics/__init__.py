"""
heuristics/__init__.py

Exposes the unified run_all_heuristics() entry point and re-exports
individual checker results. Each checker is standalone and testable
in isolation — no external API calls, no database access.
"""

from .typosquat import check_typosquatting
from .homograph import check_homograph
from .tld import check_suspicious_tld
from .subdomain import check_subdomain_impersonation
from .url_features import check_url_features

from dataclasses import dataclass, field
from typing import Optional
import tldextract


@dataclass
class HeuristicsResult:
    """Aggregated output from all heuristics checks. Every field is labeled
    by which check produced it so callers (and the frontend) can see the
    source of each finding — never a silent combined score."""

    typosquatting_detected: bool = False
    homograph_detected: bool = False
    suspicious_tld: bool = False
    brand_impersonation: bool = False  # subdomain-based impersonation
    suspicious_url_features: bool = False  # length, raw IP, shortener, HTTP, keywords
    notes: list[str] = field(default_factory=list)
    # Populated by the shortener-resolution step in the pipeline, not heuristics itself.
    resolved_final_url: Optional[str] = None

    @property
    def any_flag(self) -> bool:
        """True if at least one heuristic was triggered."""
        return any([
            self.typosquatting_detected,
            self.homograph_detected,
            self.suspicious_tld,
            self.brand_impersonation,
            self.suspicious_url_features,
        ])


def run_all_heuristics(url: str) -> HeuristicsResult:
    """
    Run the full heuristics suite against a single URL.

    Steps (all deterministic, no external calls):
      1. Typosquatting check (Levenshtein ≤ 2 vs Tranco top-domains)
      2. Homograph / IDN check (confusable_homoglyphs)
      3. Suspicious TLD check (curated list)
      4. Subdomain impersonation check (brand name only in subdomain component)
      5. URL feature checks (length, raw IP, shortener, HTTP, trigger keywords)

    Returns a HeuristicsResult with every finding labeled by source.
    Does NOT make any network requests — shortener resolution is handled
    separately by safe_fetch.py in the pipeline layer.
    """
    ext = tldextract.extract(url)
    # tldextract v5+ deprecated registered_domain in favor of top_domain_under_public_suffix
    registered_domain = getattr(ext, 'top_domain_under_public_suffix', None) or ext.registered_domain
    subdomain = ext.subdomain
    full_hostname = ".".join(filter(None, [subdomain, registered_domain]))
    suffix = ext.suffix  # TLD

    result = HeuristicsResult()

    # ── 1. Typosquatting ─────────────────────────────────────────────────────
    typo_result = check_typosquatting(registered_domain)
    if typo_result.detected:
        result.typosquatting_detected = True
        result.notes.extend(typo_result.notes)

    # ── 2. Homograph / IDN ───────────────────────────────────────────────────
    homograph_result = check_homograph(registered_domain)
    if homograph_result.detected:
        result.homograph_detected = True
        result.notes.extend(homograph_result.notes)

    # ── 3. Suspicious TLD ────────────────────────────────────────────────────
    tld_result = check_suspicious_tld(suffix)
    if tld_result.detected:
        result.suspicious_tld = True
        result.notes.extend(tld_result.notes)

    # ── 4. Subdomain impersonation ───────────────────────────────────────────
    sub_result = check_subdomain_impersonation(subdomain, registered_domain)
    if sub_result.detected:
        result.brand_impersonation = True
        result.notes.extend(sub_result.notes)

    # ── 5. URL feature flags ─────────────────────────────────────────────────
    feat_result = check_url_features(url, full_hostname, registered_domain)
    if feat_result.detected:
        result.suspicious_url_features = True
        result.notes.extend(feat_result.notes)

    return result
