"""
tests/conftest.py

Shared pytest fixtures and configuration.
Ensures the test data (Tranco CSV, TLD list, etc.) is available before tests run.
"""

import os
import sys
import csv

import pytest

# Ensure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(autouse=True, scope='session')
def ensure_test_data():
    """
    Write minimal test data files if they don't already exist.
    This allows tests to run without the full Tranco dataset.
    """
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data')
    os.makedirs(data_dir, exist_ok=True)

    tranco_path = os.path.join(data_dir, 'tranco_top_domains.csv')
    if not os.path.exists(tranco_path):
        top_domains = [
            'google.com', 'youtube.com', 'facebook.com', 'twitter.com',
            'instagram.com', 'linkedin.com', 'github.com', 'microsoft.com',
            'apple.com', 'amazon.com', 'netflix.com', 'reddit.com',
            'wikipedia.org', 'yahoo.com', 'twitch.tv', 'discord.com',
            'paypal.com', 'ebay.com', 'walmart.com', 'spotify.com',
        ]
        with open(tranco_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['rank', 'domain'])
            writer.writeheader()
            for i, d in enumerate(top_domains, 1):
                writer.writerow({'rank': i, 'domain': d})

    tld_path = os.path.join(data_dir, 'suspicious_tlds.txt')
    if not os.path.exists(tld_path):
        with open(tld_path, 'w') as f:
            f.write('xyz\ntop\nclick\nzip\nmov\ntk\nml\nga\ncf\ngq\n')

    shortener_path = os.path.join(data_dir, 'shortener_domains.txt')
    if not os.path.exists(shortener_path):
        with open(shortener_path, 'w') as f:
            f.write('bit.ly\ntinyurl.com\nt.co\nis.gd\now.ly\n')

    keywords_path = os.path.join(data_dir, 'brand_keywords.txt')
    if not os.path.exists(keywords_path):
        with open(keywords_path, 'w') as f:
            f.write('login\nverify\nupdate\nsecure\naccount\nsupport\nbilling\nwallet\nclaim\nbonus\n')
