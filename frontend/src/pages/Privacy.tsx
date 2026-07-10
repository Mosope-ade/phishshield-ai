/**
 * pages/Privacy.tsx
 * Privacy policy page. Static content, no backend dependency.
 */

import { Footer } from '../components/Footer';

export function Privacy() {
  return (
    <>
      <main id="main-content">
        <article className="learn-page">
          <h1 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: '28px', marginBottom: '6px', color: 'var(--text)' }}>
            Privacy Policy
          </h1>
          <p style={{ color: 'var(--text-2)', marginBottom: '24px', fontSize: '12px' }}>
            Last updated: July 2026
          </p>

          <h2>What we collect</h2>
          <p>
            PhishShield AI does <strong>not</strong> store the text, URLs, or images you submit for analysis.
            When you submit content, we compute a SHA-256 cryptographic hash of your input and store only that
            hash alongside the analysis result. The original content cannot be reconstructed from the hash.
          </p>

          <h2>Cache &amp; reports</h2>
          <p>
            Analysis results are cached by content hash for up to 24 hours. If you submit the same URL
            or message within that window, we return the cached result instantly without re-running the analysis.
            Report permalink pages are assigned a random, non-guessable ID and are marked <code>noindex</code>
            so search engines do not index them.
          </p>

          <h2>Third-party services</h2>
          <p>
            URLs you submit are checked against the <strong>VirusTotal</strong> Public API. VirusTotal receives
            the URL string (not your message text or image) as part of this check. Please review
            VirusTotal's privacy policy at <a href="https://www.virustotal.com/gui/privacy-policy" target="_blank" rel="noopener noreferrer">virustotal.com</a>.
          </p>
          <p>
            Message text and screenshots are sent to a large language model (LLM) provider for analysis.
            The LLM provider receives only the content you submit for analysis — no identifying information.
          </p>

          <h2>Rate limiting</h2>
          <p>
            Requests are rate-limited by IP address to prevent abuse. IP addresses are used only for this
            purpose and are not stored or logged beyond the current request session.
          </p>

          <h2>No accounts</h2>
          <p>
            PhishShield AI has no user accounts, no login, and no mechanism to associate submissions with
            individuals. There is no personal data processing beyond what is described above.
          </p>

          <h2>Contact</h2>
          <p>
            If you have privacy questions, please open an issue on our GitHub repository.
          </p>
        </article>
      </main>
      <Footer />
    </>
  );
}
