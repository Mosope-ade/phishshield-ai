/**
 * components/ResultsBlock.tsx
 * The complete results view: risk meter, badge, evidence cards, highlighted phrases,
 * recommendations, permalink copy, and disclaimer.
 *
 * Rendered on the Landing page (appended below input after submission)
 * and on the Report/:id permalink page (standalone, no input card).
 *
 * UI.md §4: verdict-first, evidence-second layout.
 * SECURITY.md §5: no dangerouslySetInnerHTML anywhere in this tree.
 */

import { useState, useCallback } from 'react';
import type { FullReport } from '../types/api';
import { RiskMeter } from './RiskMeter';
import { RiskBadge } from './RiskBadge';
import {
  AIEvidenceCard,
  HeuristicsEvidenceCard,
  ThreatIntelEvidenceCard,
} from './EvidenceCard';
import { HighlightedText } from './HighlightedText';
import { RecommendationsList } from './RecommendationsList';

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
      // Fallback: select text
    }
  }, [reportUrl]);

  return (
    <section className="results-section" aria-label="Analysis results">
      {/* ── Verdict first (UI.md §1 design law) ── */}
      <RiskBadge report={report} />
      <RiskMeter report={report} />

      {/* ── Evidence second — each source clearly labeled (PLAN.md §1) ── */}
      <div className="evidence-grid">
        {/*
         * Three independent evidence layers. Sources are NEVER merged.
         * AI can be prompt-injected; heuristics + VT remain independent checks.
         * (SECURITY.md §3, PLAN.md §1 core design law)
         */}
        <AIEvidenceCard findings={report.ai_findings} />
        <HeuristicsEvidenceCard findings={report.heuristics_findings} />
        <ThreatIntelEvidenceCard findings={report.threat_intel_findings} />
      </div>

      {/* ── Highlighted phrases ── */}
      <HighlightedText phrases={report.ai_findings.highlighted_phrases} />

      {/* ── Recommendations ── */}
      <RecommendationsList recommendations={report.ai_findings.recommendations} />

      {/* ── Permalink copy (PLAN.md §6) ── */}
      <div className="report-copy-row">
        <span className="report-copy-label">Report link:</span>
        <span className="report-copy-link" title={reportUrl}>
          {reportUrl}
        </span>
        <button
          className="btn-copy"
          onClick={copyLink}
          aria-label="Copy report link to clipboard"
          id="copy-report-link-btn"
        >
          {copied ? '✓ Copied' : '⎘ Copy'}
        </button>
      </div>

      {/* ── Disclaimer (SECURITY.md §1, PLAN.md §5) ── */}
      <p className="result-disclaimer">
        {report.disclaimer}
      </p>
    </section>
  );
}
