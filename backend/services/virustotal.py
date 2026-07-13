"""
services/virustotal.py

VirusTotal Public API v3 integration.
URL and file-hash endpoints only (PLAN.md §4.6 note: no full file upload to VT).

SECURITY.md §7: always check cache before calling VT; handle 429 gracefully.
SECURITY.md §11: VT key used server-side only; never surfaced to the client.
PLAN.md §4.3: VT is corroborating evidence, never the sole verdict.
"""

from __future__ import annotations

import base64
import logging
import os
from typing import Optional

import httpx

from ..models.schemas import ThreatIntelFindings

logger = logging.getLogger(__name__)

VT_BASE_URL = 'https://www.virustotal.com/api/v3'
VT_TIMEOUT = httpx.Timeout(20.0)


def _get_vt_key() -> Optional[str]:
    key = os.environ.get('VIRUSTOTAL_API_KEY', '')
    return key if key else None


async def check_url_virustotal(url: str) -> ThreatIntelFindings:
    """
    Query VirusTotal URL reputation endpoint.

    VT URL lookup requires base64url-encoding the URL (no padding).
    Returns ThreatIntelFindings with available=False on any failure.
    """
    api_key = _get_vt_key()
    if not api_key:
        return ThreatIntelFindings(
            available=False,
            notes=['VirusTotal API key not configured.']
        )

    url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip('=')

    try:
        async with httpx.AsyncClient(timeout=VT_TIMEOUT) as client:
            response = await client.get(
                f'{VT_BASE_URL}/urls/{url_id}',
                headers={'x-apikey': api_key},
            )

        if response.status_code == 429:
            # SECURITY.md §7: fail gracefully on rate limit
            logger.warning('VirusTotal rate limit hit (429); returning partial result.')
            return ThreatIntelFindings(
                available=False,
                notes=['VirusTotal quota reached; reputation check pending. Re-check later.']
            )

        if response.status_code == 404:
            # URL not yet analyzed by VT
            return ThreatIntelFindings(
                available=True,
                malicious_votes=None,
                total_votes=None,
                notes=['URL has not been previously analyzed by VirusTotal.']
            )

        if response.status_code != 200:
            logger.warning('VirusTotal returned %d for URL lookup.', response.status_code)
            return ThreatIntelFindings(
                available=False,
                notes=[f'VirusTotal returned an unexpected response (status {response.status_code}).']
            )

        data = response.json()
        stats = (
            data.get('data', {})
            .get('attributes', {})
            .get('last_analysis_stats', {})
        )
        malicious = stats.get('malicious', 0)
        suspicious = stats.get('suspicious', 0)
        total = sum(stats.values()) if stats else 0

        notes = []
        if malicious > 0:
            notes.append(
                f'{malicious} of {total} VirusTotal engines flagged this URL as malicious.'
            )
        if suspicious > 0:
            notes.append(
                f'{suspicious} of {total} VirusTotal engines flagged this URL as suspicious.'
            )
        if malicious == 0 and suspicious == 0 and total > 0:
            notes.append(
                f'VirusTotal: 0 of {total} engines flagged this URL. '
                'Clean VT result does not guarantee safety.'
            )

        return ThreatIntelFindings(
            available=True,
            malicious_votes=malicious + suspicious,
            total_votes=total,
            notes=notes,
        )

    except httpx.TimeoutException:
        logger.warning('VirusTotal request timed out.')
        return ThreatIntelFindings(
            available=False,
            notes=['VirusTotal check timed out; reputation data unavailable.']
        )
    except Exception as exc:
        logger.warning('VirusTotal check failed: %s', exc)
        return ThreatIntelFindings(
            available=False,
            notes=['VirusTotal check failed; reputation data unavailable.']
        )


async def check_hash_virustotal(sha256_hash: str) -> ThreatIntelFindings:
    """
    Query VirusTotal file hash reputation endpoint.
    PLAN.md §4.6: hash lookup only — file content NEVER sent to VT.
    """
    api_key = _get_vt_key()
    if not api_key:
        return ThreatIntelFindings(
            available=False,
            notes=['VirusTotal API key not configured.']
        )

    try:
        async with httpx.AsyncClient(timeout=VT_TIMEOUT) as client:
            response = await client.get(
                f'{VT_BASE_URL}/files/{sha256_hash}',
                headers={'x-apikey': api_key},
            )

        if response.status_code == 429:
            return ThreatIntelFindings(
                available=False,
                notes=['VirusTotal quota reached; hash check pending.']
            )

        if response.status_code == 404:
            return ThreatIntelFindings(
                available=True,
                malicious_votes=0,
                total_votes=0,
                notes=['File hash not found in VirusTotal — not previously analyzed.']
            )

        if response.status_code != 200:
            return ThreatIntelFindings(
                available=False,
                notes=[f'VirusTotal returned status {response.status_code} for hash lookup.']
            )

        data = response.json()
        stats = (
            data.get('data', {})
            .get('attributes', {})
            .get('last_analysis_stats', {})
        )
        malicious = stats.get('malicious', 0)
        suspicious = stats.get('suspicious', 0)
        total = sum(stats.values()) if stats else 0

        notes = []
        if malicious > 0:
            notes.append(f'{malicious} of {total} VT engines flagged this file hash as malicious.')
        elif total > 0:
            notes.append(f'VirusTotal: 0 of {total} engines flagged this file hash.')

        return ThreatIntelFindings(
            available=True,
            malicious_votes=malicious + suspicious,
            total_votes=total,
            notes=notes,
        )

    except Exception as exc:
        logger.warning('VirusTotal hash check failed: %s', exc)
        return ThreatIntelFindings(
            available=False,
            notes=['VirusTotal hash check failed.']
        )
