/**
 * pages/Disclaimer.tsx
 * Disclaimer page. Static content, no backend dependency.
 */

import { Footer } from '../components/Footer';

export function Disclaimer() {
  return (
    <>
      <main id="main-content">
        <article className="learn-page">
          <h1 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: '28px', marginBottom: '6px', color: 'var(--text)' }}>
            Disclaimer
          </h1>

          <h2>Decision-support tool, not a guarantee</h2>
          <p>
            PhishShield AI is a <strong>decision-support tool</strong>. Its analysis is intended to help
            you make a more informed judgment, not to replace your own judgment. A result of
            "Likely Safe" does not mean the content is definitively safe, and a result of
            "Likely Phishing" does not mean the content is definitively malicious.
          </p>

          <h2>Limitations</h2>
          <ul>
            <li>Newly registered phishing domains may not yet appear in VirusTotal's database.</li>
            <li>AI analysis can be fooled by carefully crafted adversarial messages.</li>
            <li>Heuristic rules do not cover every phishing technique.</li>
            <li>The tool analyzes content as-submitted; it does not browse to URLs or render web pages.</li>
          </ul>

          <h2>No liability</h2>
          <p>
            PhishShield AI and its operators accept no liability for any harm arising from acting
            on or ignoring the results of an analysis. Use of this tool is at your own risk.
            Always exercise independent judgment and, when in doubt, consult your organization's
            IT or security team.
          </p>

          <h2>Accuracy</h2>
          <p>
            We make no representations about the accuracy, completeness, or timeliness of any
            analysis result. The tool is provided "as is" without warranty of any kind.
          </p>
        </article>
      </main>
      <Footer />
    </>
  );
}
