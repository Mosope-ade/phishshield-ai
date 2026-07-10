/**
 * services/api.ts
 * API client for the PhishShield AI backend.
 * All keys and sensitive data stay server-side (SECURITY.md §11).
 */

import type { FullReport } from '../types/api';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

class ApiError extends Error {
  readonly status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    // SECURITY.md §14: backend returns safe, generic error messages
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore JSON parse failure
    }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

/** Analyze a pasted message or URL. */
export async function analyzeText(content: string): Promise<FullReport> {
  const res = await fetch(`${API_BASE}/analyze/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
  return handleResponse<FullReport>(res);
}

/** Analyze an uploaded image (screenshot or QR code). */
export async function analyzeImage(file: File): Promise<FullReport> {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_BASE}/analyze/image`, {
    method: 'POST',
    body: form,
  });
  return handleResponse<FullReport>(res);
}

/** Fetch a cached report by its public slug ID (for permalink pages). */
export async function getReport(reportId: string): Promise<FullReport> {
  const res = await fetch(`${API_BASE}/analyze/report/${encodeURIComponent(reportId)}`);
  return handleResponse<FullReport>(res);
}

export { ApiError };
