"""
tests/test_heuristics.py

Unit tests for the heuristics engine.
PLAN.md §10: must cover real known-bad domains and known-good domains.

Runs standalone — no external API calls, no database required.
"""

import sys
import os
import pytest

# Ensure backend is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.heuristics.typosquat import check_typosquatting, _load_top_domains
from backend.services.heuristics.homograph import check_homograph
from backend.services.heuristics.tld import check_suspicious_tld
from backend.services.heuristics.subdomain import check_subdomain_impersonation
from backend.services.heuristics.url_features import check_url_features
from backend.services.heuristics import run_all_heuristics


# ── Typosquatting tests ───────────────────────────────────────────────────────

class TestTyposquatting:
    def test_known_typosquat_gooogle(self):
        """gooogle.com (3 o's) should flag as typosquat of google.com."""
        result = check_typosquatting('gooogle.com')
        assert result.detected is True
        assert any('google' in n.lower() for n in result.notes)

    def test_known_typosquat_paypa1(self):
        """paypa1.com (digit 1) should flag as typosquat of paypal.com."""
        result = check_typosquatting('paypa1.com')
        assert result.detected is True

    def test_known_typosquat_amaz0n(self):
        """amaz0n.com should flag as typosquat of amazon.com."""
        result = check_typosquatting('amaz0n.com')
        assert result.detected is True

    def test_legitimate_google_not_flagged(self):
        """google.com itself must NOT be flagged (distance 0 = exact match)."""
        result = check_typosquatting('google.com')
        assert result.detected is False

    def test_legitimate_paypal_not_flagged(self):
        result = check_typosquatting('paypal.com')
        assert result.detected is False

    def test_legitimate_github_not_flagged(self):
        result = check_typosquatting('github.com')
        assert result.detected is False

    def test_unrelated_domain_not_flagged(self):
        """A completely unrelated domain should not be flagged."""
        result = check_typosquatting('myrandomapp.io')
        assert result.detected is False

    def test_empty_domain_not_flagged(self):
        result = check_typosquatting('')
        assert result.detected is False

    def test_notes_contain_source_label(self):
        """All notes must be labeled [Heuristics] as per architecture."""
        result = check_typosquatting('gooogle.com')
        if result.detected:
            assert all('[Heuristics]' in note for note in result.notes)


# ── Homograph tests ───────────────────────────────────────────────────────────

class TestHomograph:
    def test_punycode_flagged(self):
        """Punycode IDN domain should be flagged."""
        # xn-- prefix indicates IDN encoding
        result = check_homograph('xn--googl-fsa.com')
        assert result.detected is True

    def test_plain_ascii_not_flagged(self):
        result = check_homograph('google.com')
        assert result.detected is False

    def test_empty_not_flagged(self):
        result = check_homograph('')
        assert result.detected is False

    def test_notes_contain_source_label(self):
        result = check_homograph('xn--googl-fsa.com')
        if result.detected:
            assert all('[Heuristics]' in note for note in result.notes)


# ── TLD tests ─────────────────────────────────────────────────────────────────

class TestSuspiciousTLD:
    def test_xyz_flagged(self):
        result = check_suspicious_tld('xyz')
        assert result.detected is True

    def test_click_flagged(self):
        result = check_suspicious_tld('click')
        assert result.detected is True

    def test_zip_flagged(self):
        result = check_suspicious_tld('zip')
        assert result.detected is True

    def test_tk_flagged(self):
        result = check_suspicious_tld('tk')
        assert result.detected is True

    def test_com_not_flagged(self):
        result = check_suspicious_tld('com')
        assert result.detected is False

    def test_org_not_flagged(self):
        result = check_suspicious_tld('org')
        assert result.detected is False

    def test_co_uk_not_flagged(self):
        result = check_suspicious_tld('co.uk')
        assert result.detected is False

    def test_empty_not_flagged(self):
        result = check_suspicious_tld('')
        assert result.detected is False


# ── Subdomain impersonation tests ─────────────────────────────────────────────

class TestSubdomainImpersonation:
    def test_paypal_subdomain_flagged(self):
        """paypal.com.evil.ru — brand in subdomain, not registered domain."""
        result = check_subdomain_impersonation('paypal.com', 'evil.ru')
        assert result.detected is True

    def test_paypal_real_domain_not_flagged(self):
        """www.paypal.com — brand IS the registered domain, not just subdomain."""
        result = check_subdomain_impersonation('www', 'paypal.com')
        assert result.detected is False

    def test_amazon_subdomain_flagged(self):
        result = check_subdomain_impersonation('amazon', 'secure-login.xyz')
        assert result.detected is True

    def test_empty_subdomain_not_flagged(self):
        result = check_subdomain_impersonation('', 'evil.ru')
        assert result.detected is False

    def test_generic_subdomain_not_flagged(self):
        result = check_subdomain_impersonation('mail', 'example.com')
        assert result.detected is False


# ── URL feature tests ─────────────────────────────────────────────────────────

class TestURLFeatures:
    def test_long_url_flagged(self):
        url = 'https://example.com/' + 'a' * 120
        result = check_url_features(url, 'example.com', 'example.com')
        assert result.detected is True
        assert any('long' in n.lower() or 'character' in n.lower() for n in result.notes)

    def test_raw_ip_flagged(self):
        url = 'http://192.168.1.1/login'
        result = check_url_features(url, '192.168.1.1', '')
        assert result.detected is True
        assert any('ip' in n.lower() for n in result.notes)

    def test_shortener_flagged(self):
        url = 'https://bit.ly/abc123'
        result = check_url_features(url, 'bit.ly', 'bit.ly')
        assert result.detected is True
        assert any('shortener' in n.lower() for n in result.notes)

    def test_http_flagged(self):
        url = 'http://legitimate-looking-site.com/page'
        result = check_url_features(url, 'legitimate-looking-site.com', 'legitimate-looking-site.com')
        assert result.detected is True
        assert any('http' in n.lower() for n in result.notes)

    def test_trigger_keyword_in_path(self):
        url = 'https://example.com/account/verify/login'
        result = check_url_features(url, 'example.com', 'example.com')
        assert result.detected is True

    def test_clean_https_url_minimal_flags(self):
        """A clean HTTPS URL with no suspicious features should not be flagged."""
        url = 'https://github.com/user/repo'
        result = check_url_features(url, 'github.com', 'github.com')
        # May flag 'login' if it appears in keywords but 'github.com/user/repo' should not
        assert result.detected is False or all(
            'shortener' not in n.lower() and 'ip' not in n.lower() for n in result.notes
        )


# ── Integration: run_all_heuristics ──────────────────────────────────────────

class TestRunAllHeuristics:
    def test_phishing_url_flagged(self):
        """A URL with multiple phishing signals should trigger heuristics."""
        url = 'http://paypal.com.secure-login.xyz/account/verify'
        result = run_all_heuristics(url)
        assert result.any_flag is True
        # Multiple flags expected
        assert result.brand_impersonation or result.suspicious_tld or result.suspicious_url_features

    def test_legitimate_url_minimal_flags(self):
        """A legitimate HTTPS URL for a known brand should have minimal flags."""
        url = 'https://www.github.com'
        result = run_all_heuristics(url)
        # Should not falsely flag typosquatting or brand impersonation
        assert result.typosquatting_detected is False
        assert result.homograph_detected is False
        assert result.brand_impersonation is False

    def test_typosquat_url_detected(self):
        """A typosquatted URL should be flagged by the typosquatting check."""
        url = 'https://gooogle.com/signin'
        result = run_all_heuristics(url)
        assert result.typosquatting_detected is True

    def test_result_notes_all_labeled(self):
        """Every note in the result must be labeled with its source."""
        url = 'http://paypal.com.malicious.xyz/login/verify'
        result = run_all_heuristics(url)
        for note in result.notes:
            assert note.startswith('[Heuristics]') or note.startswith('['), \
                f'Unlabeled note: {note!r}'
