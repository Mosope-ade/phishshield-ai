"""
tests/test_safe_fetch.py

Unit tests for the SSRF-safe fetch wrapper.
PLAN.md §10 / SECURITY.md §4: must confirm rejection of private IPs,
metadata endpoints, and non-http(s) schemes.

These tests use mocking — no real network calls made.
"""

import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.safe_fetch import (
    SSRFError,
    _validate_url_scheme,
    _resolve_and_check_ip,
    safe_fetch_url,
)


# ── Scheme validation tests ───────────────────────────────────────────────────

class TestSchemeValidation:
    def test_http_allowed(self):
        _validate_url_scheme('http://example.com')  # Should not raise

    def test_https_allowed(self):
        _validate_url_scheme('https://example.com')  # Should not raise

    def test_file_scheme_rejected(self):
        with pytest.raises(SSRFError, match='file'):
            _validate_url_scheme('file:///etc/passwd')

    def test_gopher_scheme_rejected(self):
        with pytest.raises(SSRFError, match='gopher'):
            _validate_url_scheme('gopher://evil.com')

    def test_ftp_scheme_rejected(self):
        with pytest.raises(SSRFError, match='ftp'):
            _validate_url_scheme('ftp://files.example.com')

    def test_data_scheme_rejected(self):
        with pytest.raises(SSRFError):
            _validate_url_scheme('data:text/html,<script>alert(1)</script>')


# ── IP range rejection tests ──────────────────────────────────────────────────

class TestIPRangeRejection:
    def _mock_getaddrinfo(self, ip: str):
        """Return a mock getaddrinfo result for a given IP."""
        return [(None, None, None, None, (ip, 0))]

    def test_loopback_rejected(self):
        with patch('socket.getaddrinfo', return_value=self._mock_getaddrinfo('127.0.0.1')):
            with pytest.raises(SSRFError, match='127.0.0.1'):
                _resolve_and_check_ip('localhost')

    def test_private_10_rejected(self):
        with patch('socket.getaddrinfo', return_value=self._mock_getaddrinfo('10.0.0.1')):
            with pytest.raises(SSRFError, match='10.0.0.1'):
                _resolve_and_check_ip('internal-host')

    def test_private_172_rejected(self):
        with patch('socket.getaddrinfo', return_value=self._mock_getaddrinfo('172.16.0.5')):
            with pytest.raises(SSRFError, match='172.16.0.5'):
                _resolve_and_check_ip('internal-host')

    def test_private_192_168_rejected(self):
        with patch('socket.getaddrinfo', return_value=self._mock_getaddrinfo('192.168.1.100')):
            with pytest.raises(SSRFError, match='192.168.1.100'):
                _resolve_and_check_ip('router')

    def test_cloud_metadata_rejected(self):
        """169.254.169.254 — AWS/GCP/Azure metadata endpoint — must be blocked."""
        with patch('socket.getaddrinfo', return_value=self._mock_getaddrinfo('169.254.169.254')):
            with pytest.raises(SSRFError, match='169.254.169.254'):
                _resolve_and_check_ip('169.254.169.254')

    def test_link_local_rejected(self):
        with patch('socket.getaddrinfo', return_value=self._mock_getaddrinfo('169.254.0.1')):
            with pytest.raises(SSRFError):
                _resolve_and_check_ip('link-local-host')

    def test_public_ip_allowed(self):
        """A real public IP should not be blocked."""
        with patch('socket.getaddrinfo', return_value=self._mock_getaddrinfo('8.8.8.8')):
            _resolve_and_check_ip('dns.google')  # Should not raise

    def test_another_public_ip_allowed(self):
        with patch('socket.getaddrinfo', return_value=self._mock_getaddrinfo('1.1.1.1')):
            _resolve_and_check_ip('one.one.one.one')  # Should not raise


# ── safe_fetch_url integration tests (mocked) ─────────────────────────────────

class TestSafeFetchURL:
    @pytest.mark.asyncio
    async def test_file_scheme_raises_ssrf_error(self):
        with pytest.raises(SSRFError):
            await safe_fetch_url('file:///etc/passwd')

    @pytest.mark.asyncio
    async def test_private_ip_url_raises_ssrf_error(self):
        with patch('socket.getaddrinfo', return_value=[(None, None, None, None, ('10.0.0.1', 0))]):
            with pytest.raises(SSRFError):
                await safe_fetch_url('http://internal-service/secret')

    @pytest.mark.asyncio
    async def test_metadata_endpoint_raises_ssrf_error(self):
        with patch('socket.getaddrinfo', return_value=[(None, None, None, None, ('169.254.169.254', 0))]):
            with pytest.raises(SSRFError):
                await safe_fetch_url('http://169.254.169.254/latest/meta-data/')
