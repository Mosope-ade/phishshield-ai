/**
 * pages/Landing.tsx
 * The main check page (UI.md §8.1).
 * Layout rhythm (UI.md §4): hero → accepted-inputs → input-card → disclaimer → info-bar → results → footer
 * Results append in-place after submission (no route change, UI.md §6).
 */

import { useRef, useState, useId } from 'react';
import { useAnalysis } from '../hooks/useAnalysis';
import { ResultsBlock } from '../components/ResultsBlock';
import { Footer } from '../components/Footer';

const ACCEPTED_INPUTS = [
  { icon: '✉', label: 'Messages' },
  { icon: '🔗', label: 'Links' },
  { icon: '🖼', label: 'Screenshots' },
  { icon: '⬛', label: 'QR Codes' },
];

const PLACEHOLDER_TEXT =
  'Paste a suspicious message, URL, or attach a screenshot or QR code image…';

export function Landing() {
  const [text, setText] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaId = useId();
  const { state, submit, reset } = useAnalysis();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (state.status === 'loading') return;
    await submit(text, imageFile);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setImageFile(file);
    if (file) setText(''); // Image takes priority over text (PLAN.md §4.1)
  };

  const removeFile = () => {
    setImageFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleReset = () => {
    setText('');
    setImageFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    reset();
  };

  const isLoading = state.status === 'loading';

  return (
    <>
      <main id="main-content">
        {/* ── Hero (UI.md §5.2) ── */}
        <section className="hero" aria-labelledby="hero-title">
          <span className="hero__icon" aria-hidden="true">🛡</span>
          <h1 className="hero__title" id="hero-title">
            Detect Phishing &amp; Scams Instantly
          </h1>
          <p className="hero__tagline">
            Free, no-account analysis of messages, links, screenshots, and QR codes.
            Three independent evidence layers — AI, heuristics, and VirusTotal — all
            clearly labeled, none overriding the others.
          </p>
        </section>

        {/* ── Accepted input row (UI.md §5.3 — informational only) ── */}
        <div className="accepted-inputs" role="list" aria-label="Supported input types">
          {ACCEPTED_INPUTS.map(({ icon, label }) => (
            <span key={label} className="accepted-input-item" role="listitem">
              <span className="accepted-input-item__icon" aria-hidden="true">{icon}</span>
              <span>{label}</span>
            </span>
          ))}
        </div>

        {/* ── Input card (UI.md §5.4) ── */}
        <form onSubmit={handleSubmit} aria-label="Phishing analysis submission form">
          <div className="input-card">
            {/* Icon above textarea (UI.md §5.4 convention) */}
            <div className="input-card__icon-row" aria-hidden="true">🔍</div>

            <label htmlFor={textareaId} className="sr-only">
              Message, URL, or description to analyze
            </label>
            <textarea
              id={textareaId}
              className="input-card__textarea"
              placeholder={PLACEHOLDER_TEXT}
              value={text}
              onChange={(e) => {
                setText(e.target.value);
                if (imageFile) setImageFile(null); // Text clears image selection
              }}
              disabled={isLoading || !!imageFile}
              aria-disabled={isLoading}
              maxLength={10000}
              rows={4}
            />

            <div className="input-card__actions">
              {/* Attach image — left side */}
              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  id="image-upload"
                  accept="image/*"
                  className="sr-only"
                  onChange={handleFileChange}
                  disabled={isLoading}
                  aria-label="Attach screenshot or QR code image"
                />
                {imageFile ? (
                  <div className="attached-file-info">
                    <span>📎 {imageFile.name.length > 30 ? imageFile.name.slice(0, 27) + '…' : imageFile.name}</span>
                    <button
                      type="button"
                      className="attached-file-info__remove"
                      onClick={removeFile}
                      aria-label="Remove attached file"
                      title="Remove file"
                    >
                      ✕
                    </button>
                  </div>
                ) : (
                  <label
                    htmlFor="image-upload"
                    className="attach-btn"
                    tabIndex={0}
                    onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
                    role="button"
                    aria-label="Attach image file"
                  >
                    <span className="attach-btn__icon" aria-hidden="true">📎</span>
                    <span>Attach image</span>
                  </label>
                )}
              </div>

              {/* Primary CTA — right side, full width on mobile (UI.md §5.4) */}
              <button
                type="submit"
                className="btn-primary"
                id="analyze-submit-btn"
                disabled={isLoading || (!text.trim() && !imageFile)}
                aria-busy={isLoading}
              >
                {isLoading ? (
                  <>
                    <span className="sr-only">Analyzing…</span>
                    <span aria-hidden="true">Analyzing…</span>
                  </>
                ) : (
                  <>
                    <span>Check it</span>
                    <span aria-hidden="true">→</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {/* ── Disclaimer (UI.md §5.5 — always near input) ── */}
        <p className="disclaimer">
          By using this tool you agree to our{' '}
          <a href="/privacy">Privacy Policy</a> and{' '}
          <a href="/disclaimer">Disclaimer</a>.
          No messages or images are stored — only a cryptographic hash of your
          submission is used for caching.
        </p>

        {/* ── Info bar (UI.md §5.6) ── */}
        <div className="info-bar" role="complementary" aria-label="Additional information">
          <span>
            Also checks file hashes against VirusTotal —{' '}
            <a href="/learn">learn how it works</a>
          </span>
        </div>

        {/* ── Loading state ── */}
        {isLoading && (
          <div className="loading-state" role="status" aria-live="polite">
            <div className="spinner" aria-hidden="true" />
            <p>{state.step}</p>
            <p style={{ fontSize: '12px', color: 'var(--text-2)' }}>
              Running three independent analysis layers…
            </p>
          </div>
        )}

        {/* ── Error state ── */}
        {state.status === 'error' && (
          <div className="error-state" role="alert">
            <p className="error-state__title">Analysis failed</p>
            {/* SECURITY.md §14: safe, generic error — backend never returns internals */}
            <p>{state.message}</p>
            <button
              onClick={handleReset}
              style={{
                marginTop: '10px',
                background: 'none',
                border: '1px solid var(--border)',
                borderRadius: '6px',
                color: 'var(--text-2)',
                fontSize: '13px',
                padding: '6px 14px',
                cursor: 'pointer',
              }}
            >
              Try again
            </button>
          </div>
        )}

        {/* ── Results — appended below input after submission (UI.md §4) ── */}
        {state.status === 'success' && (
          <div className="container">
            <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '0 0 8px' }}>
              <button
                onClick={handleReset}
                style={{
                  background: 'none',
                  border: '1px solid var(--border)',
                  borderRadius: '6px',
                  color: 'var(--text-2)',
                  fontSize: '12px',
                  padding: '5px 12px',
                  cursor: 'pointer',
                }}
                aria-label="Clear results and start a new analysis"
              >
                ← New analysis
              </button>
            </div>
            <ResultsBlock report={state.report} />
          </div>
        )}
      </main>

      <Footer />
    </>
  );
}
