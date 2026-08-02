/**
 * pages/Landing.tsx
 * Redesigned Landing page adhering to Warm Paper & Ink theme:
 * - Left-aligned editorial typography
 * - Asymmetric, large input card
 * - Connected directly to /analyze/text and /analyze/image endpoints
 * - Unobtrusive privacy notice
 */

import { useRef, useState, useId, useEffect } from 'react';
import { useAnalysis } from '../hooks/useAnalysis';
import { ResultsBlock } from '../components/ResultsBlock';
import { Footer } from '../components/Footer';

const ACCEPTED_INPUTS = [
  { icon: '✉', label: 'Messages & Email' },
  { icon: '🔗', label: 'Links & Shorteners' },
  { icon: '🖼', label: 'Screenshots' },
  { icon: '⬛', label: 'QR Codes' },
];

const PLACEHOLDER_TEXT =
  'Paste a suspicious email, message, link, or attach a screenshot/QR image for instant multi-layer verification…';

export function Landing() {
  const [text, setText] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaId = useId();
  const { state, submit, reset } = useAnalysis();

  useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.type.startsWith('image/')) {
          const file = item.getAsFile();
          if (file) {
            setValidationError(null);
            if (file.size > 2 * 1024 * 1024) {
              setValidationError('Upload exceeds maximum size of 2MB.');
              setImageFile(null);
              if (fileInputRef.current) fileInputRef.current.value = '';
              return;
            }
            const pastedFile = new File([file], 'pasted-screenshot.png', { type: file.type });
            setImageFile(pastedFile);
            setText('');
            e.preventDefault();
            break;
          }
        }
      }
    };

    window.addEventListener('paste', handlePaste);
    return () => {
      window.removeEventListener('paste', handlePaste);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (state.status === 'loading') return;
    setValidationError(null);
    await submit(text, imageFile);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setValidationError(null);
    if (file) {
      if (file.size > 2 * 1024 * 1024) {
        setValidationError('Upload exceeds maximum size of 2MB.');
        setImageFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
        return;
      }
      setImageFile(file);
      setText('');
    }
  };

  const removeFile = () => {
    setImageFile(null);
    setValidationError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleReset = () => {
    setText('');
    setImageFile(null);
    setValidationError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    reset();
  };

  const isLoading = state.status === 'loading';

  return (
    <>
      <main id="main-content">
        <div className="container">
          {/* Left-aligned editorial hero section */}
          <section className="hero" aria-labelledby="hero-title">
            <p className="hero__eyebrow">Privacy-First Verification</p>
            <h1 className="hero__title" id="hero-title">
              Detect Phishing &amp; Scams with Independent Evidence
            </h1>
            <p className="hero__tagline">
              Analyze suspicious messages, links, and screenshots using deterministic offline heuristics and global VirusTotal threat intelligence.
            </p>
          </section>

          {/* Supported inputs row */}
          <div className="accepted-inputs" role="list" aria-label="Supported input types">
            {ACCEPTED_INPUTS.map(({ icon, label }) => (
              <span key={label} className="accepted-input-item" role="listitem">
                <span aria-hidden="true">{icon}</span>
                <span>{label}</span>
              </span>
            ))}
          </div>

          {/* Large input card */}
          <form onSubmit={handleSubmit} aria-label="Analysis submission form">
            <div className="input-card">
              <label htmlFor={textareaId} className="sr-only">
                Message, URL, or content to analyze
              </label>
              <textarea
                id={textareaId}
                className="input-card__textarea"
                placeholder={PLACEHOLDER_TEXT}
                value={text}
                onChange={(e) => {
                  setText(e.target.value);
                  if (imageFile) setImageFile(null);
                }}
                disabled={isLoading || !!imageFile}
                maxLength={10000}
                rows={5}
              />

              <div className="input-card__actions">
                <div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    id="image-upload"
                    accept="image/*"
                    className="sr-only"
                    onChange={handleFileChange}
                    disabled={isLoading}
                    aria-label="Attach image file"
                  />
                  {imageFile ? (
                    <div className="attached-file-info">
                      <span>📎 {imageFile.name.length > 30 ? imageFile.name.slice(0, 27) + '…' : imageFile.name}</span>
                      <button
                        type="button"
                        className="attached-file-info__remove"
                        onClick={removeFile}
                        aria-label="Remove attached file"
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <label
                        htmlFor="image-upload"
                        className="attach-btn"
                        tabIndex={0}
                        onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
                        role="button"
                      >
                        <span aria-hidden="true">📎</span>
                        <span>Attach image / QR</span>
                      </label>
                      <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        (Max 2MB)
                      </span>
                    </div>
                  )}
                </div>

                <button
                  type="submit"
                  className="btn-primary"
                  id="analyze-submit-btn"
                  disabled={isLoading || (!text.trim() && !imageFile)}
                  aria-busy={isLoading}
                >
                  {isLoading ? 'Analyzing…' : 'Check submission →'}
                </button>
              </div>
            </div>
          </form>

          {/* Unobtrusive trust & hash notice */}
          <p className="disclaimer">
            🔒 No raw messages or images are stored. Submissions are checked in-memory and indexed strictly via cryptographic SHA-256 hashes for caching.
          </p>

          {/* Loading state */}
          {isLoading && (
            <div className="loading-state" role="status" aria-live="polite">
              <div className="spinner" aria-hidden="true" />
              <p style={{ fontWeight: 500 }}>Running Heuristics and Threat Intelligence checks…</p>
            </div>
          )}

          {/* Validation error */}
          {validationError && (
            <div className="error-state" role="alert">
              <p style={{ fontWeight: 600 }}>Validation error</p>
              <p>{validationError}</p>
              <button
                onClick={handleReset}
                style={{ marginTop: '8px', background: 'none', border: '1px solid currentColor', borderRadius: '4px', padding: '4px 10px', cursor: 'pointer' }}
              >
                Clear
              </button>
            </div>
          )}

          {/* Submission error */}
          {state.status === 'error' && (
            <div className="error-state" role="alert">
              <p style={{ fontWeight: 600 }}>Analysis failed</p>
              <p>{state.message}</p>
              <button
                onClick={handleReset}
                style={{ marginTop: '8px', background: 'none', border: '1px solid currentColor', borderRadius: '4px', padding: '4px 10px', cursor: 'pointer' }}
              >
                Try again
              </button>
            </div>
          )}

          {/* Results Block */}
          {state.status === 'success' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '12px' }}>
                <button
                  onClick={handleReset}
                  style={{ background: 'none', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-2)', fontSize: '13px', padding: '6px 14px', cursor: 'pointer' }}
                >
                  ← Start new check
                </button>
              </div>
              <ResultsBlock report={state.report} />
            </div>
          )}
        </div>
      </main>

      <Footer />
    </>
  );
}
