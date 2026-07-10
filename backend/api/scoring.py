"""
api/scoring.py

Aggregated risk score computation.

PLAN.md §4.3 Step 5 and PLAN.md §1 (core design law):
- Three independent layers: AI, heuristics, VirusTotal.
- VT clean + heuristics/AI flagged STILL yields a non-trivial risk score.
- No layer silently overrides the others.
- VirusTotal is corroborating evidence, never the sole verdict.

This function's weighting logic is deliberately documented here so nobody
'simplifies' it into a plain average later — that would break the defense-
in-depth property described in PLAN.md §1 and SECURITY.md §3.

Weight rationale:
- AI (40%): captures language/intent nuance; but can be prompt-injected.
- Heuristics (35%): deterministic, uninjectable; highest confidence findings.
- VirusTotal (25%): external corroboration; added to, not replacing, others.

Important: when VT is unavailable, its weight is redistributed to AI (60%) +
heuristics (40%) rather than treating 'no VT data' as 'VT says clean'. This
ensures unavailable VT never silently deflates the risk score.
"""

from __future__ import annotations

from ..models.schemas import AnalysisResult, ThreatIntelFindings
from ..services.heuristics import HeuristicsResult


def _heuristics_score(h: HeuristicsResult) -> int:
    """
    Convert heuristics flags to a 0-100 score.
    Each flag adds to the score; multiple flags compound.
    """
    score = 0
    if h.typosquatting_detected:
        score += 40  # High confidence — Levenshtein match to known domain
    if h.homograph_detected:
        score += 45  # Very high confidence — IDN attacks are almost always malicious
    if h.brand_impersonation:
        score += 35  # Subdomain trick is highly specific
    if h.suspicious_tld:
        score += 10  # Contributing signal only (PLAN.md §4.3)
    if h.suspicious_url_features:
        score += 15  # Aggregate of length/IP/shortener/HTTP/keywords
    return min(score, 100)


def _virustotal_score(vt: ThreatIntelFindings) -> int | None:
    """
    Convert VT findings to a 0-100 score.
    Returns None if VT data is unavailable (caller handles redistribution).
    """
    if not vt.available:
        return None

    if vt.malicious_votes is None or vt.total_votes is None or vt.total_votes == 0:
        return 0

    # Scale: 1 malicious engine = 20; 5+ = 100
    # (VT free tier gets ~70 engines; 5 flagging = ~7% = high confidence)
    ratio = vt.malicious_votes / vt.total_votes
    if ratio == 0:
        return 0
    if ratio < 0.01:  # < 1%: single engine, possibly FP
        return 15
    if ratio < 0.05:  # 1-5%
        return 40
    if ratio < 0.15:  # 5-15%
        return 70
    return 100  # >=15% engines agree -> very high confidence


def compute_overall_risk_score(
    ai: AnalysisResult,
    heuristics: HeuristicsResult,
    vt: ThreatIntelFindings,
) -> int:
    """
    Compute the final 0-100 risk score from all three evidence layers.

    IMPORTANT: VT clean + heuristics/AI flagged STILL yields a non-trivial
    risk score. Do not simplify this into a plain average — doing so would
    allow a clean VT result to silently suppress clear heuristic signals.
    This is the defense-in-depth guarantee described in PLAN.md §1.
    """
    ai_score = ai.risk_score  # Already 0-100 from LLM schema
    h_score = _heuristics_score(heuristics)
    vt_score = _virustotal_score(vt)

    if vt_score is not None:
        # All three layers available: 40% AI + 35% heuristics + 25% VT
        combined = (ai_score * 0.40) + (h_score * 0.35) + (vt_score * 0.25)
    else:
        # VT unavailable: redistribute to 60% AI + 40% heuristics
        # 'No VT data' != 'VT clean' — do not deflate score
        combined = (ai_score * 0.60) + (h_score * 0.40)

    # Floor: if any single layer is Critical (>=80), overall score is at least 40
    # This prevents a clean VT result from washing out a clear AI+heuristics finding
    if ai_score >= 80 or h_score >= 80:
        combined = max(combined, 40.0)

    return round(min(combined, 100))
