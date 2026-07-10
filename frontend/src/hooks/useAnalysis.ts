/**
 * hooks/useAnalysis.ts
 * Custom hook managing the full analysis lifecycle:
 * - Submit text/image to backend
 * - Track loading / error state
 * - Surface the FullReport when done
 */

import { useState, useCallback } from 'react';
import { analyzeText, analyzeImage, ApiError } from '../services/api';
import type { FullReport } from '../types/api';

type AnalysisState =
  | { status: 'idle' }
  | { status: 'loading'; step: string }
  | { status: 'success'; report: FullReport }
  | { status: 'error'; message: string };

const LOADING_STEPS = [
  'Running heuristics engine…',
  'Querying VirusTotal…',
  'Analyzing with AI…',
  'Building report…',
];

export function useAnalysis() {
  const [state, setState] = useState<AnalysisState>({ status: 'idle' });

  const submit = useCallback(
    async (text: string, imageFile: File | null) => {
      setState({ status: 'loading', step: LOADING_STEPS[0] });

      // Cycle through loading step messages for UX
      let stepIdx = 0;
      const stepInterval = setInterval(() => {
        stepIdx = Math.min(stepIdx + 1, LOADING_STEPS.length - 1);
        setState({ status: 'loading', step: LOADING_STEPS[stepIdx] });
      }, 1800);

      try {
        let report: FullReport;
        if (imageFile) {
          report = await analyzeImage(imageFile);
        } else {
          if (!text.trim()) throw new Error('Please enter a message, URL, or attach an image.');
          report = await analyzeText(text.trim());
        }
        clearInterval(stepInterval);
        setState({ status: 'success', report });
      } catch (err) {
        clearInterval(stepInterval);
        if (err instanceof ApiError) {
          setState({ status: 'error', message: err.message });
        } else if (err instanceof Error) {
          setState({ status: 'error', message: err.message });
        } else {
          setState({ status: 'error', message: 'An unexpected error occurred. Please try again.' });
        }
      }
    },
    [],
  );

  const reset = useCallback(() => setState({ status: 'idle' }), []);

  return { state, submit, reset };
}

export { LOADING_STEPS };
