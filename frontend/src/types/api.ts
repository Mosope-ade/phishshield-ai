/**
 * types/api.ts
 * TypeScript interfaces matching the backend's Pydantic schemas (PLAN.md §5).
 * Keep in sync with backend/models/schemas.py.
 */

export interface HighlightedPhrase {
  phrase: string;
  explanation: string;
}

/** Validated LLM output (AnalysisResult in backend). */
export interface AIFindings {
  risk_score: number;         // 0–100
  threat_level: 'Low' | 'Medium' | 'High' | 'Critical';
  classification: 'Likely Safe' | 'Suspicious' | 'Likely Scam' | 'Likely Phishing';
  confidence: number;         // 0–100
  reasons: string[];
  highlighted_phrases: HighlightedPhrase[];
  recommendations: string[];
}

/** Findings from the deterministic heuristics engine. */
export interface HeuristicsFindings {
  typosquatting_detected: boolean;
  homograph_detected: boolean;
  suspicious_tld: boolean;
  brand_impersonation: boolean;
  suspicious_url_features: boolean;
  resolved_final_url: string | null;
  notes: string[];
}

/** VirusTotal reputation data. */
export interface ThreatIntelFindings {
  source: 'VirusTotal';
  available: boolean;
  malicious_votes: number | null;
  total_votes: number | null;
  notes: string[];
}

/** Full report returned by the backend — all three evidence layers labeled. */
export interface FullReport {
  overall_risk_score: number;   // 0–100
  threat_level: string;
  ai_findings: AIFindings;
  heuristics_findings: HeuristicsFindings;
  threat_intel_findings: ThreatIntelFindings;
  report_id: string;
  disclaimer: string;
}
