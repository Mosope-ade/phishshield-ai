"""
services/heuristics/text_patterns.py

Deterministic free-text scam pattern analyzer with false-positive mitigation.

False Positive Defense:
- Requires multi-pattern compounding or explicit coercive action verbs before assigning high scores.
- Legitimate transactional/notification phrases ("your gift card order has shipped",
  "your account password was changed successfully") are excluded via negative lookaheads and context rules.
- Multi-category matching rule: A single isolated category match yields a low/caution score (10-15 pts).
  Two or more distinct categories matching simultaneously (e.g. Urgency + Gift Card / Advance-Fee + Telegram)
  compounds the risk score to High (35-60 pts).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ── 1. Urgency & Threat Triggers ──────────────────────────────────────────────
# Must indicate high pressure or imminent account suspension, excluding past-tense security receipts.
_URGENCY_RE = re.compile(
    r'\b(?:'
    r'(?:immediate|urgent)\s+(?:action|attention|verification)\s+(?:required|needed|mandatory)|'
    r'account\s+(?:will\s+be\s+)?(?:suspended|locked|terminated|blocked|disabled|restricted)\s+(?:within|in)\s+\d+\s*(?:hours|minutes|mins)|'
    r'unauthorized\s+(?:login|transaction|access|activity)\s+detected\s+-\s+verify\s+now|'
    r'verify\s+your\s+identity\s+immediately\s+to\s+prevent'
    r')\b',
    re.IGNORECASE,
)

# Exclude legitimate security receipt notifications like "your password was changed" or "successful login"
_URGENCY_BENIGN_RE = re.compile(
    r'\b(?:password\s+(?:was\s+)?changed\s+successfully|successful\s+login|order\s+(?:has\s+)?shipped|receipt\s+for)\b',
    re.IGNORECASE,
)

# ── 2. Coercive Untraceable Payment Demands ──────────────────────────────────
# Flexible pattern allowing filler words, amounts ($200, two, 100), and card types between action verbs and payment methods
_PAYMENT_RE = re.compile(
    r'\b(?:'
    r'(?:buy|purchase|send|pay\s+with|provide)\s+(?:[^\n\.\,\!\?]{0,35}?)\s*'
    r'(?:gift\s*cards?|steam\s*cards?|apple\s*cards?|google\s*play\s*cards?|ebay\s*cards?|amazon\s*cards?|crypto|bitcoin|usdt|btc|wire\s*transfers?|zelle|cash\s*app|venmo)|'
    r'send\s+(?:the\s+)?(?:code|pin|back\s+of\s+the\s+card|picture\s+of\s+the\s+card)'
    r')\b',
    re.IGNORECASE,
)

_PAYMENT_BENIGN_RE = re.compile(
    r'\b(?:order\s+(?:has\s+)?shipped|e-gift\s+card\s+purchase\s+confirmation|thank\s+you\s+for\s+your\s+order)\b',
    re.IGNORECASE,
)

# ── 3. Advance-Fee / Prize / Lottery Solicitations ───────────────────────────
_ADVANCE_FEE_RE = re.compile(
    r'\b(?:'
    r'you\s+(?:have\s+won|were\s+selected|are\s+eligible)|'
    r'(?:grant|inheritance|lottery|prize|unclaimed\s+fund|donation)\s+of\s+\$?\d+[\d,]*|'
    r'claim\s+your\s+(?:reward|prize|payout|lottery|grant)'
    r')\b',
    re.IGNORECASE,
)

# ── 4. Credential Harvest & Off-Platform Redirection ──────────────────────────
_HARVEST_RE = re.compile(
    r'\b(?:'
    r'(?:send|reply\s+with|provide)\s+(?:your\s+)?(?:password|pin|ssn|social\s+security|credit\s+card|cvv|account\s+details|otp|verification\s+code)|'
    r'(?:text|message|contact)\s+(?:me|our\s+agent|us|agent)?\s*(?:on|via|at)?\s*(?:telegram|whatsapp|signal)|'
    r'telegram|whatsapp'
    r')\b',
    re.IGNORECASE,
)



_HARVEST_BENIGN_RE = re.compile(
    r'\b(?:send\s+(?:your\s+)?(?:cv|resume|portfolio)|apply\s+online)\b',
    re.IGNORECASE,
)


@dataclass
class TextPatternResult:
    detected: bool = False
    categories_matched: int = 0
    score_bump: int = 0
    notes: list[str] = field(default_factory=list)


def check_text_patterns(text: str) -> TextPatternResult:
    """
    Scan plain text for high-confidence scam indicator patterns.
    Multi-category compounding rule prevents single benign phrase false positives.
    """
    if not text or len(text.strip()) < 10:
        return TextPatternResult()

    result = TextPatternResult()
    categories: list[str] = []

    # Check Urgency
    if _URGENCY_RE.search(text) and not _URGENCY_BENIGN_RE.search(text):
        categories.append('urgency')
        result.notes.append('[Text Patterns] High-urgency threat or immediate action demand.')

    # Check Payment Demand
    if _PAYMENT_RE.search(text) and not _PAYMENT_BENIGN_RE.search(text):
        categories.append('payment')
        result.notes.append('[Text Patterns] Coercive demand for untraceable payment (gift card/crypto/wire).')

    # Check Advance-Fee
    if _ADVANCE_FEE_RE.search(text):
        categories.append('advance_fee')
        result.notes.append('[Text Patterns] Advance-fee/lottery/grant solicitation language.')

    # Check Credential Harvest / Off-Platform
    if _HARVEST_RE.search(text) and not _HARVEST_BENIGN_RE.search(text):
        categories.append('harvest')
        result.notes.append('[Text Patterns] Credential harvest or off-platform redirection demand.')

    matched_count = len(categories)
    result.categories_matched = matched_count

    if matched_count == 0:
        result.detected = False
        result.score_bump = 0
    elif matched_count == 1:
        # Single category match: Caution/low signal only (+15 pts) to prevent FP
        result.detected = True
        result.score_bump = 15
    elif matched_count == 2:
        # Dual category match (e.g. Urgency + Gift Card): High risk (+40 pts)
        result.detected = True
        result.score_bump = 40
    elif matched_count >= 3:
        # 3 or 4 category matches (e.g. Urgency + Gift Card + Telegram): Critical risk (+60 pts)
        result.detected = True
        result.score_bump = 60

    return result
