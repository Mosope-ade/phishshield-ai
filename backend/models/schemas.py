"""
models/schemas.py

Pydantic v2 schemas for:
- LLM output validation (AnalysisResult — PLAN.md §5)
- Aggregated API response sent to frontend (FullReport)
- Request bodies for each endpoint

SECURITY.md §6: raw LLM output is NEVER passed through unvalidated.
Every LLM response must be parsed against AnalysisResult before use.
"""

from __future__ import annotations

from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ── LLM output contract (must match PLAN.md §5 exactly) ──────────────────────


class HighlightedPhrase(BaseModel):
    phrase: str
    explanation: str


class AnalysisResult(BaseModel):
    """Validated schema for LLM output. PLAN.md §5."""

    risk_score: Annotated[int, Field(ge=0, le=100)]
    threat_level: Literal['Low', 'Medium', 'High', 'Critical']
    classification: Literal[
        'Likely Safe', 'Suspicious', 'Likely Scam', 'Likely Phishing'
    ]
    confidence: Annotated[int, Field(ge=0, le=100)]
    reasons: list[str]
    highlighted_phrases: list[HighlightedPhrase]
    recommendations: list[str]

    @field_validator('reasons', 'recommendations', mode='before')
    @classmethod
    def ensure_string_list(cls, v: object) -> list[str]:
        if not isinstance(v, list):
            return []
        return [str(item) for item in v]

    @field_validator('highlighted_phrases', mode='before')
    @classmethod
    def ensure_phrase_list(cls, v: object) -> list[dict]:
        if not isinstance(v, list):
            return []
        return [
            item if isinstance(item, dict)
            else {'phrase': str(item), 'explanation': ''}
            for item in v
        ]


# ── Heuristics findings (populated by the heuristics engine) ─────────────────


class HeuristicsFindings(BaseModel):
    typosquatting_detected: bool
    homograph_detected: bool
    suspicious_tld: bool
    brand_impersonation: bool
    suspicious_url_features: bool
    resolved_final_url: Optional[str] = None
    notes: list[str]


# ── VirusTotal findings ───────────────────────────────────────────────────────


class ThreatIntelFindings(BaseModel):
    source: Literal['VirusTotal'] = 'VirusTotal'
    available: bool
    malicious_votes: Optional[int] = None
    total_votes: Optional[int] = None
    notes: list[str] = Field(default_factory=list)


# ── Full report (the complete API response) ───────────────────────────────────


class FullReport(BaseModel):
    """Complete API response sent to frontend. PLAN.md §5."""

    overall_risk_score: Annotated[int, Field(ge=0, le=100)]
    threat_level: str
    ai_findings: AnalysisResult
    heuristics_findings: HeuristicsFindings
    threat_intel_findings: ThreatIntelFindings
    report_id: str  # Non-sequential random slug (SECURITY.md §15)
    disclaimer: str = (
        'This is a decision-support tool, not a guarantee of safety. '
        'Always exercise caution with unexpected messages and links.'
    )


# ── Request bodies ────────────────────────────────────────────────────────────


class TextAnalysisRequest(BaseModel):
    """POST /analyze/text — pasted message or URL."""

    content: Annotated[
        str,
        Field(
            min_length=1,
            max_length=10_000,  # SECURITY.md §2: prevent excessive LLM token cost
            description='Pasted message text or URL to analyze.',
        ),
    ]

    @field_validator('content', mode='before')
    @classmethod
    def strip_content(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v
