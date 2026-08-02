/**
 * components/RiskBadge.tsx
 * Verdict-first pill badge per UI.md §5.7.
 * Icon + text label + color — never color alone (UI.md §7 accessibility).
 * SECURITY.md §5: all strings rendered as text nodes.
 */

import type { FullReport } from '../types/api';

interface RiskBadgeProps {
  report: FullReport;
}

export function RiskBadge({ report }: RiskBadgeProps) {
  const score = report.overall_risk_score;

  if (report.status === 'unreadable' || score === null) {
    return (
      <div className="verdict-header">
        <div>
          <span className="verdict-badge verdict-badge--medium" style={{ background: '#FAF0E6', color: '#B5654A', border: '1px solid #E8C8B8' }}>
            Unreadable Image
          </span>
          <p style={{ marginTop: '8px', fontSize: '14px', color: 'var(--text-2)' }}>
            We couldn't clearly read text in this screenshot.
          </p>
        </div>
        <div className="verdict-score" style={{ color: 'var(--text-muted)' }}>
          —<span style={{ fontSize: '20px', color: 'var(--text-muted)' }}>/100</span>
        </div>
      </div>
    );
  }

  let level = 'Low';
  let badgeClass = 'verdict-badge--low';

  if (score >= 75) {
    level = 'Critical Threat';
    badgeClass = 'verdict-badge--critical';
  } else if (score >= 50) {
    level = 'High Risk';
    badgeClass = 'verdict-badge--high';
  } else if (score >= 25) {
    level = 'Medium Risk';
    badgeClass = 'verdict-badge--medium';
  } else {
    level = 'Likely Safe';
    badgeClass = 'verdict-badge--low';
  }

  return (
    <div className="verdict-header">
      <div>
        <span className={`verdict-badge ${badgeClass}`}>
          {level}
        </span>
        <p style={{ marginTop: '8px', fontSize: '14px', color: 'var(--text-2)' }}>
          Calculated from deterministic heuristics and threat intelligence.
        </p>
      </div>
      <div className="verdict-score">
        {score}<span style={{ fontSize: '20px', color: 'var(--text-muted)' }}>/100</span>
      </div>
    </div>
  );
}

