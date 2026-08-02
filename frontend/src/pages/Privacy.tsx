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
          <h1>Privacy Policy</h1>
          <p style={{ color: 'var(--text-muted)', marginBottom: '24px', fontSize: '13px' }}>
            Last updated: August 2026
          </p>

          <h2>What we collect</h2>
          <p>
            HookCheck does not store the text, URLs, or images you submit for analysis. When you submit content, we compute a SHA-256 cryptographic hash of your input and store only that hash alongside the analysis result. The original content cannot be reconstructed from the hash.
          </p>

          <h2>Cache &amp; reports</h2>
          <p>
            Analysis results are cached by content hash for up to 24 hours. If you submit the same URL or message within that window, we return the cached result instantly without re-running the analysis. Report permalink pages are assigned a random, non-guessable ID and are marked noindex so search engines do not index them.
          </p>

          <h2>How your submission is analyzed</h2>
          <p>
            Message text and links are analyzed entirely using local, deterministic methods: offline pattern heuristics (typosquat detection, suspicious domain structure, scam language patterns) and a check against VirusTotal's threat database. No AI model is used to analyze the content you submit.
          </p>
          <p>
            Screenshots are first processed using local OCR (text extraction) running entirely on our servers. If local OCR cannot clearly read an image — for example, due to low resolution or heavy compression — the image may be sent to a third-party AI vision provider as a fallback, for the sole purpose of extracting visible text. This fallback is time-limited: if the AI provider doesn't respond quickly, we proceed without it and inform you the image couldn't be fully read. The AI provider is not used to assess risk or generate a verdict — only to help read text from hard-to-OCR images. When this fallback is used, no personal or identifying information is attached to the request.
          </p>

          <h2>Third-party services</h2>
          <p>
            URLs you submit are checked against the VirusTotal Public API. VirusTotal receives the URL string (not your message text or image) as part of this check. Please review VirusTotal's privacy policy at <a href="https://www.virustotal.com/gui/privacy-policy" target="_blank" rel="noopener noreferrer">virustotal.com</a>.
          </p>

          <h2>Rate limiting</h2>
          <p>
            Requests are rate-limited by IP address to prevent abuse. IP addresses are used only for this purpose and are not stored or logged beyond the current request session.
          </p>

          <h2>No accounts</h2>
          <p>
            HookCheck has no user accounts, no login, and no mechanism to associate submissions with individuals. There is no personal data processing beyond what is described above.
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
