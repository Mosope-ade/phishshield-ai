/**
 * components/EvidenceCard.tsx
 * Source-labeled evidence card per UI.md §5.8.
 * Three distinct sources: AI analysis, Heuristics, Threat intel.
 * Sources are NEVER merged into one unlabeled block (PLAN.md §1 core design law).
 * SECURITY.md §5: all note text rendered as text nodes, never innerHTML.
 */

import type { HeuristicsFindings, ThreatIntelFindings, AIFindings } from '../types/api';

// ── AI Evidence Card ────────────────────────────────────────────────────────

interface AIEvidenceCardProps {
  findings: AIFindings;
}

export function AIEvidenceCard({ findings }: AIEvidenceCardProps) {
  const hasFindings = findings.reasons.length > 0;

  return (
    <article className="evidence-card" aria-label="AI Analysis findings">
      <header className="evidence-card__label">
        <span className="evidence-card__label-icon" aria-hidden="true">◈</span>
        <span>AI Analysis</span>
      </header>
      <div className="evidence-card__content">
        {hasFindings ? (
          findings.reasons.map((reason, i) => (
            // SECURITY.md §5: rendered as text content, not innerHTML
            <span key={i} className="evidence-tag">{reason}</span>
          ))
        ) : (
          <span className="evidence-card__empty">No AI findings available.</span>
        )}
        <span className="evidence-tag" style={{ marginTop: '4px' }}>
          Confidence: {findings.confidence}%
        </span>
      </div>
    </article>
  );
}

// ── Heuristics Evidence Card ────────────────────────────────────────────────

interface HeuristicsEvidenceCardProps {
  findings: HeuristicsFindings;
}

export function HeuristicsEvidenceCard({ findings }: HeuristicsEvidenceCardProps) {
  const flags: string[] = [];
  if (findings.typosquatting_detected) flags.push('Typosquatting detected');
  if (findings.homograph_detected) flags.push('Homograph/IDN attack detected');
  if (findings.suspicious_tld) flags.push('Suspicious TLD');
  if (findings.brand_impersonation) flags.push('Brand impersonation via subdomain');
  if (findings.suspicious_url_features) flags.push('Suspicious URL features');

  const hasFindings = flags.length > 0 || findings.notes.length > 0;

  return (
    <article className="evidence-card" aria-label="Heuristics engine findings">
      <header className="evidence-card__label">
        <span className="evidence-card__label-icon" aria-hidden="true">⚙</span>
        <span>Heuristics</span>
      </header>
      <div className="evidence-card__content">
        {hasFindings ? (
          <>
            {flags.map((flag, i) => (
              <span key={i} className="evidence-tag">{flag}</span>
            ))}
            {findings.resolved_final_url && findings.resolved_final_url !== '' && (
              <span className="evidence-tag">
                Resolved to: {findings.resolved_final_url}
              </span>
            )}
            {/* Show up to 3 detail notes */}
            {findings.notes.slice(0, 3).map((note, i) => (
              <span key={`note-${i}`} className="evidence-tag" style={{ fontSize: '10px' }}>
                {note.replace(/^\[Heuristics\]\s*/, '')}
              </span>
            ))}
          </>
        ) : (
          <span className="evidence-card__empty">No heuristic flags triggered.</span>
        )}
      </div>
    </article>
  );
}

// ── Threat Intel Evidence Card ──────────────────────────────────────────────

interface ThreatIntelEvidenceCardProps {
  findings: ThreatIntelFindings;
}

export function ThreatIntelEvidenceCard({ findings }: ThreatIntelEvidenceCardProps) {
  return (
    <article className="evidence-card" aria-label="VirusTotal threat intelligence findings">
      <header className="evidence-card__label">
        <span className="evidence-card__label-icon" aria-hidden="true">◎</span>
        <span>Threat Intel</span>
      </header>
      <div className="evidence-card__content">
        {findings.available ? (
          <>
            {findings.malicious_votes !== null && findings.total_votes !== null && (
              <span className="evidence-tag">
                {findings.malicious_votes} / {findings.total_votes} engines flagged
              </span>
            )}
            {findings.notes.map((note, i) => (
              <span key={i} className="evidence-tag">{note}</span>
            ))}
          </>
        ) : (
          <>
            <span className="evidence-tag">Source: VirusTotal</span>
            {findings.notes.map((note, i) => (
              <span key={i} className="evidence-tag">{note}</span>
            ))}
          </>
        )}
        <span className="evidence-tag" style={{ fontSize: '10px' }}>
          VT is corroborating evidence — not the sole verdict
        </span>
      </div>
    </article>
  );
}
