/**
 * components/RiskMeter.tsx
 * Displays the overall risk score as a progress bar + numerical score.
 * UI.md §5.7: risk level communicated by icon + text + color (never color alone).
 * SECURITY.md §5: all strings rendered as text nodes, never dangerouslySetInnerHTML.
 */

import type { FullReport } from '../types/api';

interface RiskMeterProps {
  report: FullReport;
}

function getRiskColor(score: number): string {
  if (score >= 75) return 'var(--risk-critical)';
  if (score >= 50) return 'var(--risk-high)';
  if (score >= 25) return 'var(--risk-medium)';
  return 'var(--risk-low)';
}

function getRiskScoreColor(score: number): string {
  if (score >= 75) return 'var(--risk-critical)';
  if (score >= 50) return 'var(--risk-high)';
  if (score >= 25) return 'var(--risk-medium)';
  return 'var(--risk-low)';
}

export function RiskMeter({ report }: RiskMeterProps) {
  const { overall_risk_score } = report;
  const color = getRiskColor(overall_risk_score);

  return (
    <div className="risk-meter" role="meter" aria-valuenow={overall_risk_score} aria-valuemin={0} aria-valuemax={100} aria-label={`Risk score: ${overall_risk_score} out of 100`}>
      <div className="risk-meter__header">
        <span className="risk-meter__label mono">Overall Risk</span>
        <span className="risk-meter__score mono" style={{ color: getRiskScoreColor(overall_risk_score) }}>
          {overall_risk_score} / 100
        </span>
      </div>
      <div className="risk-meter__bar">
        <div
          className="risk-meter__fill"
          style={{
            width: `${overall_risk_score}%`,
            background: color,
          }}
        />
      </div>
    </div>
  );
}
