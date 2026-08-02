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
from .text_patterns import check_text_patterns

from dataclasses import dataclass, field
from typing import Optional
import tldextract


@dataclass
class HeuristicsResult:
    """Aggregated output from all heuristics checks."""

    typosquatting_detected: bool = False
    homograph_detected: bool = False
    suspicious_tld: bool = False
    brand_impersonation: bool = False  # subdomain-based impersonation
    suspicious_url_features: bool = False  # length, raw IP, shortener, HTTP, keywords
    text_scam_detected: bool = False  # Free-text scam patterns (urgency, gift cards, etc.)
    text_scam_score: int = 0
    notes: list[str] = field(default_factory=list)
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
            self.text_scam_detected,
        ])


def run_all_heuristics(url: str, text: str | None = None) -> HeuristicsResult:
    """
    Run the full heuristics suite against a single URL and optional plain text.
    """
    result = HeuristicsResult()

    if url:
        ext = tldextract.extract(url)
        registered_domain = getattr(ext, 'top_domain_under_public_suffix', None) or ext.registered_domain
        subdomain = ext.subdomain
        full_hostname = ".".join(filter(None, [subdomain, registered_domain]))
        suffix = ext.suffix

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

    # ── 6. Plain text scam patterns ──────────────────────────────────────────
    if text:
        text_res = check_text_patterns(text)
        if text_res.detected:
            result.text_scam_detected = True
            result.text_scam_score = text_res.score_bump
            result.notes.extend(text_res.notes)

    return result

