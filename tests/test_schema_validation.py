"""
tests/test_schema_validation.py

Unit tests for LLM output schema validation.
PLAN.md §10: malformed/non-JSON LLM output must be caught and handled;
never crash the endpoint, never pass through unvalidated.
"""

import sys
import os
import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models.schemas import AnalysisResult, FullReport, HeuristicsFindings, ThreatIntelFindings
from backend.services.llm_client import _extract_json_from_response


class TestAnalysisResultValidation:
    def test_valid_schema_passes(self):
        data = {
            'risk_score': 85,
            'threat_level': 'High',
            'classification': 'Likely Phishing',
            'confidence': 90,
            'reasons': ['Uses urgency tactics', 'Requests credentials'],
            'highlighted_phrases': [{'phrase': 'Act now', 'explanation': 'Urgency tactic'}],
            'recommendations': ['Do not click any links', 'Report to your IT department'],
        }
        result = AnalysisResult.model_validate(data)
        assert result.risk_score == 85
        assert result.threat_level == 'High'

    def test_risk_score_out_of_range_raises(self):
        """risk_score must be 0-100."""
        data = {
            'risk_score': 150,  # Invalid
            'threat_level': 'High',
            'classification': 'Likely Phishing',
            'confidence': 90,
            'reasons': [],
            'highlighted_phrases': [],
            'recommendations': [],
        }
        with pytest.raises(ValidationError):
            AnalysisResult.model_validate(data)

    def test_invalid_threat_level_raises(self):
        data = {
            'risk_score': 50,
            'threat_level': 'Extreme',  # Not in Literal
            'classification': 'Likely Phishing',
            'confidence': 70,
            'reasons': [],
            'highlighted_phrases': [],
            'recommendations': [],
        }
        with pytest.raises(ValidationError):
            AnalysisResult.model_validate(data)

    def test_invalid_classification_raises(self):
        data = {
            'risk_score': 50,
            'threat_level': 'High',
            'classification': 'Definitely Malware',  # Not in Literal
            'confidence': 70,
            'reasons': [],
            'highlighted_phrases': [],
            'recommendations': [],
        }
        with pytest.raises(ValidationError):
            AnalysisResult.model_validate(data)

    def test_missing_required_field_raises(self):
        data = {
            'risk_score': 50,
            # Missing threat_level, classification, etc.
        }
        with pytest.raises(ValidationError):
            AnalysisResult.model_validate(data)

    def test_non_list_reasons_coerced(self):
        """reasons as non-list should be coerced to empty list."""
        data = {
            'risk_score': 50,
            'threat_level': 'Medium',
            'classification': 'Suspicious',
            'confidence': 60,
            'reasons': 'not a list',  # Should be coerced
            'highlighted_phrases': [],
            'recommendations': [],
        }
        result = AnalysisResult.model_validate(data)
        assert isinstance(result.reasons, list)

    def test_empty_json_raises(self):
        with pytest.raises(ValidationError):
            AnalysisResult.model_validate({})

    def test_null_input_raises(self):
        with pytest.raises(Exception):
            AnalysisResult.model_validate(None)


class TestJSONExtraction:
    def test_extracts_raw_json(self):
        raw = '{"risk_score": 50, "threat_level": "Medium", "classification": "Suspicious", "confidence": 60, "reasons": [], "highlighted_phrases": [], "recommendations": []}'
        result = _extract_json_from_response(raw)
        assert result is not None
        assert result['risk_score'] == 50

    def test_extracts_json_from_markdown_fence(self):
        raw = '```json\n{"risk_score": 30, "threat_level": "Low", "classification": "Likely Safe", "confidence": 80, "reasons": [], "highlighted_phrases": [], "recommendations": []}\n```'
        result = _extract_json_from_response(raw)
        assert result is not None
        assert result['risk_score'] == 30

    def test_returns_none_on_prose(self):
        result = _extract_json_from_response('I cannot analyze this. Please try again.')
        assert result is None

    def test_returns_none_on_empty(self):
        result = _extract_json_from_response('')
        assert result is None

    def test_extracts_json_from_mixed_text(self):
        raw = 'Here is my analysis:\n{"risk_score": 75, "threat_level": "High", "classification": "Likely Phishing", "confidence": 85, "reasons": ["suspicious"], "highlighted_phrases": [], "recommendations": []}\nEnd of analysis.'
        result = _extract_json_from_response(raw)
        assert result is not None
        assert result['risk_score'] == 75
