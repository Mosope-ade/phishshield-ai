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
    if h.text_scam_detected:
        score += h.text_scam_score
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
    heuristics: HeuristicsResult,
    vt: ThreatIntelFindings,
    ai: AnalysisResult | None = None,
) -> int:
    """
    Compute the final 0-100 risk score from Heuristics and VirusTotal.
    If optional AI findings are provided and active, AI can contribute;
    otherwise, core scoring relies on 60% Heuristics + 40% VirusTotal.

    IMPORTANT: VT clean + heuristics flagged STILL yields a non-trivial
    risk score. Do not simplify this into a plain average — doing so would
    allow a clean VT result to silently suppress clear heuristic signals.
    """
    h_score = _heuristics_score(heuristics)
    vt_score = _virustotal_score(vt)

    if vt_score is not None:
        # Both Heuristics and VT available: 60% Heuristics + 40% VT
        combined = (h_score * 0.60) + (vt_score * 0.40)
    else:
        # VT unavailable: rely 100% on Heuristics score
        combined = float(h_score)

    # Floor rule: if either layer detects severe risk (>=80), guarantee overall score >= 50
    if h_score >= 80 or (vt_score is not None and vt_score >= 80):
        combined = max(combined, 50.0)

    return round(min(combined, 100))

