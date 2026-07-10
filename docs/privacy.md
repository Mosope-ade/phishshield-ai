# Privacy Policy

See [frontend/src/pages/Privacy.tsx](../frontend/src/pages/Privacy.tsx) for the full privacy policy rendered in the app.

## Summary

- No raw user content is stored. Only SHA-256 hashes of submissions are used as cache keys.
- Submitted URLs are forwarded to the VirusTotal Public API for reputation checking.
- Message text and screenshots are sent to an LLM provider for phishing analysis.
- No user accounts, no tracking, no persistent personal data.
- Rate-limited per IP address to prevent abuse.
- Report permalinks are marked `noindex` so search engines do not index them.
