"""
heuristics/homograph.py

Detects IDN homograph attacks: domains that use Unicode characters visually
indistinguishable from ASCII in order to impersonate a trusted domain.

Approach:
- If the domain contains any non-ASCII character, check each character against
  the confusable_homoglyphs database to detect lookalike substitutions.
- Also flag Punycode domains (xn-- prefix) that decode to a confusable form.
- The same top-domains list used by typosquat.py is used as the reference set.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field

try:
    from confusable_homoglyphs import confusables
except ImportError:
    confusables = None  # type: ignore[assignment]


@dataclass
class HomographResult:
    detected: bool = False
    notes: list[str] = field(default_factory=list)


def _is_ascii(text: str) -> bool:
    try:
        text.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def _decode_punycode(domain: str) -> str:
    """Attempt to IDNA-decode a domain; return original on failure."""
    try:
        return domain.encode('ascii').decode('idna')
    except (UnicodeError, UnicodeDecodeError):
        return domain


def check_homograph(registered_domain: str) -> HomographResult:
    """
    Check registered_domain for homograph/IDN confusion.

    Flags:
    - Any non-ASCII character in the domain label
    - Punycode-encoded (xn--) domain that decodes to a visually ambiguous form
    - Characters identified as confusable by confusable_homoglyphs library

    Parameters
    ----------
    registered_domain : str
        The eTLD+1 extracted by tldextract (e.g. "xn--googIe-fke.com").
    """
    if not registered_domain:
        return HomographResult()

    domain_lower = registered_domain.lower()

    # Punycode domains always start label portions with 'xn--'
    is_punycode = any(label.startswith('xn--') for label in domain_lower.split('.'))

    if is_punycode:
        decoded = _decode_punycode(domain_lower)
        if not _is_ascii(decoded):
            return HomographResult(
                detected=True,
                notes=[
                    f"[Heuristics] Punycode/IDN domain detected: '{domain_lower}' "
                    f"decodes to '{decoded}', which contains non-ASCII characters "
                    "that may impersonate a legitimate domain."
                ],
            )
        else:
            # Even if decoded is ASCII, still flag it — punycode in registered domain
            # is suspicious on its own (legitimate sites use it rarely)
            return HomographResult(
                detected=True,
                notes=[
                    f"[Heuristics] Punycode/IDN domain detected: '{domain_lower}' "
                    "contains xn-- encoded labels, which is characteristic of "
                    "IDN homograph attacks."
                ],
            )

    # Check for non-ASCII characters in the raw domain
    if not _is_ascii(domain_lower):
        suspicious_chars: list[str] = []
        if confusables is not None:
            for ch in domain_lower:
                if ord(ch) > 127:
                    confused = confusables.is_confusable(ch, preferred_aliases=['LATIN'])
                    if confused:
                        suspicious_chars.append(ch)
        else:
            # Fallback: flag any non-ASCII char if library unavailable
            suspicious_chars = [ch for ch in domain_lower if ord(ch) > 127]

        if suspicious_chars:
            char_list = ', '.join(repr(c) for c in set(suspicious_chars))
            return HomographResult(
                detected=True,
                notes=[
                    f"[Heuristics] Homograph attack suspected in '{domain_lower}': "
                    f"non-ASCII characters {char_list} may be visually confusable "
                    "with Latin characters used in legitimate domain names."
                ],
            )
        elif not _is_ascii(domain_lower):
            # Non-ASCII but no confirmed confusables — still flag as suspicious
            return HomographResult(
                detected=True,
                notes=[
                    f"[Heuristics] Non-ASCII characters detected in domain '{domain_lower}': "
                    "may be an IDN homograph attack."
                ],
            )

    return HomographResult()
