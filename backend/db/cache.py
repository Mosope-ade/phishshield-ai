"""
db/cache.py

Supabase-backed cache for analysis reports.

Schema (from PLAN.md §7):
    reports(
        id text primary key,          -- random slug (non-sequential)
        input_hash text unique,       -- sha256 of normalized input
        input_type text,              -- 'text' | 'url' | 'screenshot' | 'qr' | 'file'
        report_json jsonb,
        created_at timestamptz
    )

SECURITY.md §9: all queries parameterized; no raw input stored.
SECURITY.md §7: cache is checked BEFORE any LLM/VT call to limit
  fresh API traffic from abusive scripts.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def _get_supabase_client():
    """Lazy-import supabase client to avoid import errors when running tests
    without supabase configured."""
    try:
        from supabase import create_client, Client
        url = os.environ.get('SUPABASE_URL', '')
        key = os.environ.get('SUPABASE_SERVICE_KEY', '')
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception as exc:
        logger.warning('Supabase client init failed: %s', exc)
        return None


async def get_cached_report(input_hash: str) -> Optional[dict]:
    """
    Look up a cached report by its content hash.
    Returns the report_json dict if found, else None.
    """
    client = _get_supabase_client()
    if client is None:
        return None

    try:
        response = (
            client.table('reports')
            .select('report_json')
            .eq('input_hash', input_hash)  # Parameterized via supabase-py
            .single()
            .execute()
        )
        if response.data:
            rj = response.data.get('report_json')
            if isinstance(rj, str):
                return json.loads(rj)
            return rj
    except Exception as exc:
        # Cache miss is not an error — fail open
        logger.debug('Cache lookup failed (treating as miss): %s', exc)

    return None


async def store_report(
    report_id: str,
    input_hash: str,
    input_type: str,
    report_json: dict,
) -> bool:
    """
    Store a completed report in the cache.
    SECURITY.md §9: only hash + report JSON stored, never raw input.

    Returns True on success, False on failure (partial results still returned
    to user — cache failure is non-fatal).
    """
    client = _get_supabase_client()
    if client is None:
        return False

    try:
        client.table('reports').insert({
            'id': report_id,
            'input_hash': input_hash,
            'input_type': input_type,
            'report_json': report_json,  # supabase-py handles jsonb serialization
        }).execute()
        return True
    except Exception as exc:
        logger.warning('Failed to cache report %s: %s', report_id, exc)
        return False


async def get_report_by_id(report_id: str) -> Optional[dict]:
    """
    Fetch a report by its public slug ID (for permalink pages).
    Used by the /report/:id endpoint.
    """
    client = _get_supabase_client()
    if client is None:
        return None

    try:
        response = (
            client.table('reports')
            .select('report_json')
            .eq('id', report_id)  # Parameterized via supabase-py
            .single()
            .execute()
        )
        if response.data:
            rj = response.data.get('report_json')
            if isinstance(rj, str):
                return json.loads(rj)
            return rj
    except Exception as exc:
        logger.debug('Report ID lookup failed: %s', exc)

    return None
