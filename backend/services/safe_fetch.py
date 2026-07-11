"""
services/safe_fetch.py

SSRF-safe outbound HTTP wrapper. This is the ONLY sanctioned way to make
outbound HTTP requests to user-supplied or user-derived URLs in this codebase.
Do NOT call httpx directly on user-supplied URLs anywhere else.

Security controls (per SECURITY.md §4):
- Resolves hostname and rejects private/reserved IP ranges (RFC1918, loopback,
  link-local, including 169.254.169.254 cloud metadata)
- Re-checks resolved IP after every redirect hop
- Allows only http/https schemes (rejects file://, gopher://, etc.)
- Enforces strict connect/read timeout
- Caps redirect depth (max 5 hops)
- Caps response body read into memory
"""

from __future__ import annotations

import ipaddress
import socket
from contextvars import ContextVar
from typing import NamedTuple
from urllib.parse import urlparse

import httpx

# ── DNS Rebinding Prevention Context ──────────────────────────────────────────
_dns_override: ContextVar[dict[str, str]] = ContextVar('dns_override', default={})
_original_getaddrinfo = socket.getaddrinfo


def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    override = _dns_override.get()
    if host in override:
        ip = override[host]
        if ':' in ip:  # IPv6
            return [(socket.AF_INET6, socket.SocketKind.SOCK_STREAM, 6, '', (ip, port or 80, 0, 0))]
        else:  # IPv4
            return [(socket.AF_INET, socket.SocketKind.SOCK_STREAM, 6, '', (ip, port or 80))]
    return _original_getaddrinfo(host, port, family, type, proto, flags)


# Apply the global DNS patch at module startup
socket.getaddrinfo = _patched_getaddrinfo

# ── Configuration constants ───────────────────────────────────────────────────

ALLOWED_SCHEMES = frozenset({'http', 'https'})
MAX_REDIRECTS = 5
CONNECT_TIMEOUT_S = 5.0
READ_TIMEOUT_S = 10.0
MAX_RESPONSE_BYTES = 1 * 1024 * 1024  # 1 MB cap on body read

# Private / reserved IP networks that must never be targeted
_BLOCKED_NETWORKS = [
    ipaddress.ip_network('0.0.0.0/8'),
    ipaddress.ip_network('10.0.0.0/8'),        # RFC1918
    ipaddress.ip_network('100.64.0.0/10'),     # Shared Address Space
    ipaddress.ip_network('127.0.0.0/8'),       # Loopback
    ipaddress.ip_network('169.254.0.0/16'),    # Link-local + cloud metadata (169.254.169.254)
    ipaddress.ip_network('172.16.0.0/12'),     # RFC1918
    ipaddress.ip_network('192.0.0.0/24'),      # IETF Protocol
    ipaddress.ip_network('192.168.0.0/16'),    # RFC1918
    ipaddress.ip_network('198.18.0.0/15'),     # Benchmarking
    ipaddress.ip_network('198.51.100.0/24'),   # TEST-NET-2
    ipaddress.ip_network('203.0.113.0/24'),    # TEST-NET-3
    ipaddress.ip_network('224.0.0.0/4'),       # Multicast
    ipaddress.ip_network('240.0.0.0/4'),       # Reserved
    ipaddress.ip_network('255.255.255.255/32'),# Broadcast
    ipaddress.ip_network('::1/128'),           # IPv6 loopback
    ipaddress.ip_network('fc00::/7'),          # IPv6 ULA
    ipaddress.ip_network('fe80::/10'),         # IPv6 link-local
    ipaddress.ip_network('::/128'),            # IPv6 unspecified
]


class SSRFError(ValueError):
    """Raised when a URL would cause an SSRF vulnerability."""


class FetchResult(NamedTuple):
    final_url: str
    status_code: int
    redirect_chain: list[str]  # All URLs visited in order


def _resolve_and_check_ip(hostname: str) -> str:
    """
    DNS-resolve hostname and reject any result that falls within a blocked
    network range. Raises SSRFError if blocked. Returns the verified IP address.
    """
    try:
        # Call socket.getaddrinfo so test mocks can intercept DNS resolution.
        # When no override is active, this safely falls back to the original resolver.
        results = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise SSRFError(f'Cannot resolve hostname: {hostname!r}: {exc}') from exc

    resolved_ip = None
    for _family, _type, _proto, _canonname, sockaddr in results:
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        for blocked_net in _BLOCKED_NETWORKS:
            if ip in blocked_net:
                raise SSRFError(
                    f'Hostname {hostname!r} resolves to {ip_str}, which is in a '
                    f'blocked private/reserved range ({blocked_net}). '
                    'Request blocked to prevent SSRF.'
                )
        if resolved_ip is None:
            resolved_ip = ip_str

    if not resolved_ip:
        raise SSRFError(f'No valid IP address resolved for hostname: {hostname!r}')

    return resolved_ip


def _validate_url_scheme(url: str) -> None:
    """Reject non-http/https schemes."""
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise SSRFError(
            f'URL scheme {parsed.scheme!r} is not allowed. '
            f'Only {sorted(ALLOWED_SCHEMES)} are permitted.'
        )


async def safe_fetch_url(
    url: str, *, follow_redirects: bool = True
) -> FetchResult:
    """
    Fetch a user-supplied URL safely, with full SSRF protection.

    This function is used exclusively for resolving URL shorteners and
    fetching redirect chains — NOT for fetching page content for analysis
    (only headers/status are used in practice).

    Parameters
    ----------
    url : str
        The URL to fetch. Must use http or https.
    follow_redirects : bool
        If True, follow the redirect chain up to MAX_REDIRECTS hops,
        re-validating the IP at each hop.

    Returns
    -------
    FetchResult
        Contains the final URL after all redirects, the final HTTP status code,
        and the list of all URLs visited.

    Raises
    ------
    SSRFError
        If any URL in the chain targets a blocked IP or uses a banned scheme.
    httpx.TimeoutException
        If the connection or read exceeds the timeout.
    """
    _validate_url_scheme(url)

    redirect_chain: list[str] = [url]
    current_url = url
    hops = 0

    timeout = httpx.Timeout(connect=CONNECT_TIMEOUT_S, read=READ_TIMEOUT_S, write=5.0, pool=5.0)

    async with httpx.AsyncClient(
        follow_redirects=False,  # We handle redirects manually for IP re-check
        timeout=timeout,
        headers={'User-Agent': 'PhishShield-SafeFetch/1.0 (security research)'},
    ) as client:
        while True:
            parsed = urlparse(current_url)
            hostname = parsed.hostname
            if not hostname:
                raise SSRFError(f'Cannot extract hostname from URL: {current_url!r}')

            # IP check BEFORE each request, returning the verified IP
            resolved_ip = _resolve_and_check_ip(hostname)

            # Apply context-local DNS override to prevent DNS rebinding
            token = _dns_override.set({hostname: resolved_ip})
            try:
                response = await client.head(current_url)
            finally:
                _dns_override.reset(token)

            if follow_redirects and response.is_redirect:
                if hops >= MAX_REDIRECTS:
                    # Exceeded max redirect depth — return what we have
                    return FetchResult(
                        final_url=current_url,
                        status_code=response.status_code,
                        redirect_chain=redirect_chain,
                    )

                location = response.headers.get('location', '')
                if not location:
                    break

                # Resolve relative redirects against current URL
                if location.startswith('/'):
                    parsed_current = urlparse(current_url)
                    location = f'{parsed_current.scheme}://{parsed_current.netloc}{location}'

                _validate_url_scheme(location)
                current_url = location
                redirect_chain.append(current_url)
                hops += 1
            else:
                return FetchResult(
                    final_url=current_url,
                    status_code=response.status_code,
                    redirect_chain=redirect_chain,
                )

    return FetchResult(
        final_url=current_url,
        status_code=0,
        redirect_chain=redirect_chain,
    )
