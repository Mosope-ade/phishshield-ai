"""
tests/test_audit_fixes.py

Unit and integration tests verifying the security, performance, and
architectural fixes introduced from the codebase audit.
"""

import socket
import pytest
from unittest.mock import patch, MagicMock

from backend.services.safe_fetch import _dns_override, _patched_getaddrinfo
from backend.db.cache import _get_supabase_client
from backend.utils.limiter import limiter
from fastapi.testclient import TestClient
from backend.main import app


def test_supabase_client_singleton(monkeypatch):
    """Verify that the Supabase client helper caches and reuses a single client instance."""
    # Reset singleton state for the test
    import backend.db.cache
    backend.db.cache._supabase_client_singleton = None

    monkeypatch.setenv('SUPABASE_URL', 'https://example.supabase.co')
    monkeypatch.setenv('SUPABASE_SERVICE_KEY', 'mock-service-key')

    with patch('supabase.create_client') as mock_create:
        mock_create.return_value = MagicMock()
        client1 = _get_supabase_client()
        client2 = _get_supabase_client()

        assert client1 is client2
        assert mock_create.call_count == 1

    # Reset singleton state to clean up after test
    backend.db.cache._supabase_client_singleton = None


def test_dns_rebinding_override():
    """Verify context-local DNS override intercepts socket resolution correctly."""
    # Verify active override routes to the overridden IP
    token = _dns_override.set({'evil-rebinding.com': '1.2.3.4'})
    try:
        res = _patched_getaddrinfo('evil-rebinding.com', 80)
        assert len(res) == 1
        assert res[0][4][0] == '1.2.3.4'
    finally:
        _dns_override.reset(token)

    # Verify fallback to original resolver when no override matches
    with patch('backend.services.safe_fetch._original_getaddrinfo') as mock_orig:
        mock_orig.return_value = [('mock-family', 'mock-type', 0, '', ('5.5.5.5', 80))]
        res = _patched_getaddrinfo('some-other-domain.com', 80)
        assert res == [('mock-family', 'mock-type', 0, '', ('5.5.5.5', 80))]
        mock_orig.assert_called_once_with('some-other-domain.com', 80, 0, 0, 0, 0)


def test_rate_limiting_headers():
    """Verify rate-limiting headers are present on successful analysis routes."""
    client = TestClient(app)
    # Mock cached report to return a valid dict, yielding a 200 response
    valid_report = {
        'overall_risk_score': 10,
        'threat_level': 'Low',
        'ai_findings': {
            'risk_score': 10,
            'threat_level': 'Low',
            'classification': 'Likely Safe',
            'confidence': 90,
            'reasons': ['Safe'],
            'highlighted_phrases': [],
            'recommendations': [],
        },
        'heuristics_findings': {
            'typosquatting_detected': False,
            'homograph_detected': False,
            'suspicious_tld': False,
            'brand_impersonation': False,
            'suspicious_url_features': False,
            'notes': [],
        },
        'threat_intel_findings': {
            'source': 'VirusTotal',
            'available': False,
            'notes': [],
        },
        'report_id': 'test-id',
    }
    with patch('backend.api.analyze.get_report_by_id', return_value=valid_report):
        response = client.get('/analyze/report/test-id')
        assert response.status_code == 200
        headers = response.headers
        assert 'x-ratelimit-limit' in headers
        assert 'x-ratelimit-remaining' in headers

