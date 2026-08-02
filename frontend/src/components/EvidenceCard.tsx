/**
 * components/EvidenceCard.tsx
 * Evidence card displaying active scoring layers (Heuristics & VirusTotal)
 * with distinct color-coded chips and an optional disabled treatment for AI.
 */

import type { HeuristicsFindings, ThreatIntelFindings } from '../types/api';

// ── Heuristics Evidence Card (Active Layer 1) ────────────────────────────────

interface HeuristicsEvidenceCardProps {
  findings: HeuristicsFindings;
}

export function HeuristicsEvidenceCard({ findings }: HeuristicsEvidenceCardProps) {
  const flags: string[] = [];
  if (findings.typosquatting_detected) flags.push('Typosquatting domain match');
  if (findings.homograph_detected) flags.push('Homograph / IDN unicode attack');
  if (findings.suspicious_tld) flags.push('High-risk TLD extension');
  if (findings.brand_impersonation) flags.push('Subdomain brand impersonation');
  if (findings.suspicious_url_features) flags.push('Suspicious URL structural features');

  const hasFindings = flags.length > 0 || findings.notes.length > 0;

  return (
    <article className="evidence-card evidence-card--heuristics" aria-label="Deterministic Heuristics Engine">
      <header className="evidence-card__header">
        <span className="evidence-chip evidence-chip--heuristics">Offline Heuristics</span>
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
            {findings.notes.map((note, i) => (
              <span key={`note-${i}`} className="evidence-tag" style={{ fontSize: '11px', color: 'var(--text-2)' }}>
                {note.replace(/^\[(?:Heuristics|Text Patterns)\]\s*/, '')}
              </span>
            ))}
          </>
        ) : (
          <span style={{ fontSize: '13px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
            No structural or pattern heuristic flags triggered.
          </span>
        )}
      </div>
    </article>
  );
}

// ── Threat Intel / VirusTotal Evidence Card (Active Layer 2) ──────────────────

interface ThreatIntelEvidenceCardProps {
  findings: ThreatIntelFindings;
}

export function ThreatIntelEvidenceCard({ findings }: ThreatIntelEvidenceCardProps) {
  return (
    <article className="evidence-card evidence-card--vt" aria-label="VirusTotal Threat Intelligence">
      <header className="evidence-card__header">
        <span className="evidence-chip evidence-chip--vt">VirusTotal Intelligence</span>
      </header>
      <div className="evidence-card__content">
        {findings.available ? (
          <>
            {findings.malicious_votes !== null && findings.total_votes !== null && (
              <span className="evidence-tag" style={{ fontWeight: 600 }}>
                {findings.malicious_votes} / {findings.total_votes} engines flagged as malicious
              </span>
            )}
            {findings.notes.map((note, i) => (
              <span key={i} className="evidence-tag">{note}</span>
            ))}
          </>
        ) : (
          <>
            <span className="evidence-tag" style={{ color: 'var(--risk-medium)' }}>
              Reputation data currently unavailable or rate-limited.
            </span>
            {findings.notes.map((note, i) => (
              <span key={i} className="evidence-tag" style={{ fontSize: '11px' }}>{note}</span>
            ))}
          </>
        )}
      </div>
    </article>
  );
}

// ── AI Inactive Evidence Card (Disabled State) ────────────────────────────────

export function AIEvidenceCardDisabled() {
  return (
    <article className="evidence-card evidence-card--ai-disabled" aria-label="AI Enrichment Inactive">
      <header className="evidence-card__header">
        <span className="evidence-chip evidence-chip--disabled">AI Enrichment: Inactive</span>
      </header>
      <div className="evidence-card__content">
        <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          LLM enrichment is currently disabled. Verdict is calculated strictly via offline Heuristics and VirusTotal threat intelligence.
        </span>
      </div>
    </article>
  );
}
