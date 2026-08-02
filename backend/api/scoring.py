"""
api/scoring.py

Aggregated risk score computation.

PLAN.md §4.3 Step 5 and PLAN.md §1 (core design law):
- Three independent layers: AI, heuristics, VirusTotal.
- VT clean + heuristics/AI flagged STILL yields a non-trivial risk score.
- No layer silently overrides the others.
- VirusTotal is corroborating evidence, never the sole verdict.
- If AI or VirusTotal is unavailable (confidence == 0 or vt.available == False),
  missing data never deflates the score. Weights dynamically redistribute to active layers.
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
    Compute the final 0-100 risk score from available evidence layers.

    IMPORTANT: If AI or VT is unavailable (e.g. AI confidence=0 or VT unavailable=True),
    missing engines NEVER deflate the risk score. Their weights are dynamically
    redistributed to active engines.
    """
    ai_available = ai.confidence > 0
    ai_score = ai.risk_score
    h_score = _heuristics_score(heuristics)
    vt_score = _virustotal_score(vt)

    if ai_available and vt_score is not None:
        # All 3 layers active: 40% AI + 35% Heuristics + 25% VT
        combined = (ai_score * 0.40) + (h_score * 0.35) + (vt_score * 0.25)
    elif ai_available and vt_score is None:
        # AI + Heuristics active (VT offline): 60% AI + 40% Heuristics
        combined = (ai_score * 0.60) + (h_score * 0.40)
    elif not ai_available and vt_score is not None:
        # Heuristics + VT active (AI offline): 60% Heuristics + 40% VT
        combined = (h_score * 0.60) + (vt_score * 0.40)
    else:
        # Only Heuristics active (AI & VT offline): 100% Heuristics
        combined = float(h_score)

    # Floor: if any single active layer is Critical (>=80), overall score is at least 40
    if (ai_available and ai_score >= 80) or h_score >= 80 or (vt_score is not None and vt_score >= 80):
        combined = max(combined, 40.0)

    return round(min(combined, 100))
