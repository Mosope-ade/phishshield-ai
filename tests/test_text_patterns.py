"""
tests/test_text_patterns.py

Unit tests for backend/services/heuristics/text_patterns.py:
- True Positives (scam messages across all 4 categories)
- True Negatives (legitimate transactional/notification/recruitment messages)
- False Positive mitigation & multi-category compounding rules
"""

import pytest
from backend.services.heuristics.text_patterns import check_text_patterns


def test_text_patterns_true_positives():
    """Verify high-risk scoring on actual scam messages matching multiple categories."""
    
    # Scam 1: Urgency + Gift Card Payment Demand (2 categories -> +40 pts)
    scam_1 = (
        "URGENT: Your account will be suspended within 24 hours due to unauthorized activity. "
        "To verify your identity immediately, buy a $200 Apple gift card and send the code."
    )
    res1 = check_text_patterns(scam_1)
    assert res1.detected is True
    assert res1.categories_matched == 2
    assert res1.score_bump == 40

    # Scam 2: Advance-Fee + Off-Platform Telegram Harvest (2 categories -> +40 pts)
    scam_2 = (
        "Congratulations! You were selected for an inheritance grant of $50,000. "
        "Claim your prize now by contacting our agent on Telegram at +1234567890."
    )
    res2 = check_text_patterns(scam_2)
    assert res2.detected is True
    assert res2.categories_matched == 2
    assert res2.score_bump == 40

    # Scam 3: Urgency + Payment + Credential Harvest (3 categories -> +60 pts)
    scam_3 = (
        "IMMEDIATE ACTION REQUIRED: Unauthorized transaction detected! Account blocked in 2 hours. "
        "Pay with Bitcoin to restore access and send your password and OTP immediately."
    )
    res3 = check_text_patterns(scam_3)
    assert res3.detected is True
    assert res3.categories_matched == 3
    assert res3.score_bump == 60


def test_text_patterns_true_negatives():
    """Verify legitimate transactional messages do NOT trigger high risk or false positives."""
    
    # Benign 1: Gift card purchase shipping confirmation receipt
    benign_1 = "Your Amazon gift card order has shipped! Thank you for your order."
    res1 = check_text_patterns(benign_1)
    assert res1.categories_matched == 0
    assert res1.score_bump == 0

    # Benign 2: Standard password change receipt
    benign_2 = "Security Notice: Your account password was changed successfully. If you did not do this, log in."
    res2 = check_text_patterns(benign_2)
    assert res2.categories_matched == 0
    assert res2.score_bump == 0

    # Benign 3: Recruitment job application message
    benign_3 = "Thank you for applying for the Senior Developer role. Please send your CV and portfolio to our HR department."
    res3 = check_text_patterns(benign_3)
    assert res3.categories_matched == 0
    assert res3.score_bump == 0


def test_text_patterns_single_category_low_score():
    """Verify isolated single-category matches yield low caution score (15 pts) to prevent FP."""
    single_category = "Claim your reward points from our annual customer survey now."
    res = check_text_patterns(single_category)
    assert res.detected is True
    assert res.categories_matched == 1
    assert res.score_bump == 15
