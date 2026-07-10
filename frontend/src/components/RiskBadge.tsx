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

type ThreatLevel = 'Low' | 'Medium' | 'High' | 'Critical';

function getBadgeClass(level: string): string {
  const l = level.toLowerCase() as Lowercase<ThreatLevel>;
  const map: Record<string, string> = {
    low: 'risk-badge--low',
    medium: 'risk-badge--medium',
    high: 'risk-badge--high',
    critical: 'risk-badge--critical',
  };
  return map[l] ?? 'risk-badge--low';
}

function getIcon(level: string): string {
  // UI.md §5.7: Low → check, Medium → alert-circle, High/Critical → alert-triangle
  const l = level.toLowerCase();
  if (l === 'low') return '✓';
  if (l === 'medium') return '⚠';
  return '⚠'; // high / critical
}

function getSummary(report: FullReport): string {
  const { ai_findings } = report;
  if (ai_findings.reasons.length > 0) {
    return ai_findings.reasons[0];
  }
  return `Classified as: ${ai_findings.classification}`;
}

export function RiskBadge({ report }: RiskBadgeProps) {
  const { threat_level, ai_findings } = report;

  return (
    <div className="risk-badge-row">
      <span
        className={`risk-badge ${getBadgeClass(threat_level)}`}
        role="status"
        aria-label={`Threat level: ${threat_level}`}
      >
        <span className="risk-badge__icon" aria-hidden="true">
          {getIcon(threat_level)}
        </span>
        {/* Text label always present (UI.md §7) */}
        <span className="mono">{threat_level.toUpperCase()}</span>
        <span> — {ai_findings.classification}</span>
      </span>
      {/* Plain-language summary always paired with badge (UI.md §5.7) */}
      <p className="risk-summary">{getSummary(report)}</p>
    </div>
  );
}
