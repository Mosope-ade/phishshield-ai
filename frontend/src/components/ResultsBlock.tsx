/**
 * components/ResultsBlock.tsx
 * Results view displaying Risk Badge, active evidence layers (Heuristics & VT),
 * inactive AI indicator card, recommendations, and permalink link.
 */

import { useState, useCallback } from 'react';
import type { FullReport } from '../types/api';
import { RiskBadge } from './RiskBadge';
import {
  HeuristicsEvidenceCard,
  ThreatIntelEvidenceCard,
  AIEvidenceCardDisabled,
} from './EvidenceCard';

interface ResultsBlockProps {
  report: FullReport;
}

export function ResultsBlock({ report }: ResultsBlockProps) {
  const [copied, setCopied] = useState(false);
  const reportUrl = `${window.location.origin}/report/${report.report_id}`;

  const copyLink = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(reportUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
    }
  }, [reportUrl]);

  return (
    <section className="results-section" aria-label="Analysis results">
      {/* Verdict badge & overall score */}
      <RiskBadge report={report} />

      {/* Evidence layers grid: Active Heuristics + Active VT + Disabled AI card */}
      <div className="evidence-grid">
        <HeuristicsEvidenceCard findings={report.heuristics_findings} />
        <ThreatIntelEvidenceCard findings={report.threat_intel_findings} />
      </div>

      <AIEvidenceCardDisabled />

      {/* Recommendations Box */}
      {report.ai_findings.recommendations.length > 0 && (
        <div className="recommendations-box">
          <h3 className="recommendations-box__title">Safety Guidance &amp; Recommendations</h3>
          <ul className="recommendations-list">
            {report.ai_findings.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Permalink share row */}
      <div className="report-copy-row">
        <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text)' }}>Report Link:</span>
        <span className="report-copy-link" title={reportUrl}>{reportUrl}</span>
        <button className="btn-copy" onClick={copyLink} id="copy-report-link-btn">
          {copied ? '✓ Copied' : 'Copy permalink'}
        </button>
      </div>

      <p style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic', textAlign: 'center' }}>
        {report.disclaimer}
      </p>
    </section>
  );
}
