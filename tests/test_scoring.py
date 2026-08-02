"""
tests/test_scoring.py

Direct unit tests for backend/api/scoring.py:
- Normal 60% Heuristics / 40% VirusTotal split
- VirusTotal-unavailable 100%-heuristics fallback
- Critical floor rule triggers (Heuristics >= 80 or VT >= 80 -> Floor of 50)
"""

import pytest
from backend.api.scoring import compute_overall_risk_score
from backend.services.heuristics import HeuristicsResult
from backend.models.schemas import ThreatIntelFindings


def test_scoring_normal_60_40_split():
    """Verify 60% Heuristics / 40% VT weighting when both are available."""
    # Typosquatting adds +40 to Heuristics score -> 40 * 0.60 = 24
    h = HeuristicsResult(typosquatting_detected=True)
    
    # 5/50 malicious engines -> 5/50 = 0.10 -> 70 VT score -> 70 * 0.40 = 28
    vt = ThreatIntelFindings(
        available=True,
        malicious_votes=5,
        total_votes=50,
        notes=[]
    )
    
    # Combined = 24 + 28 = 52
    score = compute_overall_risk_score(h, vt)
    assert score == 52


def test_scoring_vt_unavailable_fallback():
    """Verify that when VT is unavailable, Heuristics receives 100% weight."""
    # Typosquatting (+40) + Suspicious TLD (+10) = 50 Heuristic score
    h = HeuristicsResult(typosquatting_detected=True, suspicious_tld=True)
    
    vt = ThreatIntelFindings(available=False, notes=['VT API key missing.'])
    
    # Combined = 50 * 1.0 = 50
    score = compute_overall_risk_score(h, vt)
    assert score == 50


def test_scoring_heuristics_floor_trigger():
    """Verify that a Heuristic score >= 80 triggers the floor of 50 even if VT is clean."""
    # Typosquatting (+40) + Homograph (+45) = 85 Heuristic score
    h = HeuristicsResult(typosquatting_detected=True, homograph_detected=True)
    
    # Clean VT score (0)
    vt = ThreatIntelFindings(available=True, malicious_votes=0, total_votes=70, notes=[])
    
    # Without floor: (85 * 0.60) + (0 * 0.40) = 51
    # With floor: max(51, 50) = 51 (Floor satisfied)
    score = compute_overall_risk_score(h, vt)
    assert score >= 50


def test_scoring_vt_floor_trigger():
    """Verify that a VT score >= 80 triggers the floor of 50 even if Heuristics score is low."""
    # Minor heuristic signal (Suspicious TLD +10)
    h = HeuristicsResult(suspicious_tld=True)
    
    # High VT score: 15/70 malicious -> 100 VT score
    vt = ThreatIntelFindings(available=True, malicious_votes=15, total_votes=70, notes=[])
    
    # Without floor: (10 * 0.60) + (100 * 0.40) = 46
    # With floor trigger (VT >= 80): max(46, 50) = 50
    score = compute_overall_risk_score(h, vt)
    assert score == 50
