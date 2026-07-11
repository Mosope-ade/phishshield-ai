"""
heuristics/subdomain.py

Detects subdomain-based brand impersonation: a trusted brand name appears
only in the subdomain portion (e.g. paypal.com.security-login.ru), not as
the actual registered domain.

The registered domain comparison uses the Tranco top-domains list from
typosquat.py.
"""

from __future__ import annotations

import functools
import re
from dataclasses import dataclass, field
from .typosquat import _load_top_domains

# Well-known brands that are specifically high-value impersonation targets.
# This supplements the Tranco list with short brand names that would produce
# too many false positives if searched for in arbitrary text.
_BRAND_NAMES: frozenset[str] = frozenset([
    'paypal', 'amazon', 'apple', 'google', 'microsoft', 'facebook',
    'instagram', 'netflix', 'wellsfargo', 'chase', 'coinbase', 'blockchain',
    'twitter', 'linkedin', 'dropbox', 'adobe', 'office', 'outlook',
    'whatsapp', 'telegram', 'spotify', 'uber', 'airbnb', 'ebay',
    'walmart', 'target', 'bestbuy', 'americanexpress', 'visa', 'mastercard',
    'discover', 'citibank', 'bankofamerica', 'capitalone', 'robinhood',
    'stripe', 'square', 'venmo', 'cashapp', 'zelle', 'steam', 'discord',
])


@dataclass
class SubdomainResult:
    detected: bool = False
    notes: list[str] = field(default_factory=list)


def _extract_brand_from_domain(domain: str) -> str | None:
    """Return the domain name without TLD for brand matching (e.g. 'paypal' from 'paypal.com')."""
    parts = domain.split('.')
    if parts:
        return parts[0].lower()
    return None


@functools.lru_cache(maxsize=1)
def _get_combined_brand_names() -> frozenset[str]:
    """Cache the combined brand names list once loaded from typosquat top domains."""
    top_domains = _load_top_domains()
    brand_names = set(_BRAND_NAMES)
    for td in top_domains:
        brand = _extract_brand_from_domain(td)
        if brand and len(brand) > 3:  # Skip very short names (e.g. 'go', 'fb')
            brand_names.add(brand)
    return frozenset(brand_names)


def check_subdomain_impersonation(
    subdomain: str, registered_domain: str
) -> SubdomainResult:
    """
    Flag when a trusted brand name appears in the subdomain but the
    registered domain is *not* that brand's domain.

    Example flagged: subdomain='paypal.com', registered_domain='security-login.ru'
    Example safe: subdomain='www', registered_domain='paypal.com'

    Parameters
    ----------
    subdomain : str
        The subdomain portion from tldextract (may be empty string).
    registered_domain : str
        The eTLD+1 from tldextract.
    """
    if not subdomain:
        return SubdomainResult()

    subdomain_lower = subdomain.lower()
    registered_lower = registered_domain.lower()
    brand_names = _get_combined_brand_names()

    # Check each label of the subdomain
    subdomain_labels = re.split(r'[\.\-]', subdomain_lower)
    found_brand: str | None = None

    for label in subdomain_labels:
        if label in brand_names:
            # Verify the registered domain is NOT the legitimate one for this brand
            # (e.g. 'www.paypal.com' → registered_domain='paypal.com' → safe)
            if not registered_lower.startswith(label + '.'):
                found_brand = label
                break

    if found_brand:
        return SubdomainResult(
            detected=True,
            notes=[
                f"[Heuristics] Brand impersonation via subdomain: '{found_brand}' "
                f"appears in the subdomain but the actual registered domain is "
                f"'{registered_domain}'. This pattern (e.g. paypal.com.evil.ru) "
                "is a common phishing technique."
            ],
        )

    return SubdomainResult()
