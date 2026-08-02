# HookCheck — Full Technical Specification & Architecture Overview

## 1. System Architecture Overview

**HookCheck** (formerly PhishShield AI) is an open-source, privacy-first, full-stack decision-support application built to detect phishing, social engineering attacks, and scams across multiple input formats: free text, single URLs, uploaded/pasted screenshots, and QR codes.

The application follows a decoupled client-server architecture:
- **Frontend SPA:** Built with React 19, TypeScript, and Vite. Communicates asynchronously with the backend API via standard HTTP REST.
- **Backend API:** Built with Python 3.11+, FastAPI, Uvicorn, and Pydantic v2.
- **Database & Privacy Cache:** Powered by Supabase (Cloud PostgreSQL) using SHA-256 content hashes to prevent unnecessary external API calls and ensure zero raw user input is persisted.

```
                   ┌─────────────────────────────────────────┐
                   │             React 19 SPA                │
                   │    (Landing, Report, Learn, Privacy)    │
                   └────────────────────┬────────────────────┘
                                        │ HTTP REST
                                        ▼
                   ┌─────────────────────────────────────────┐
                   │           FastAPI Backend API           │
                   │        (Rate Limiting & Headers)        │
                   └───────────┬───────────────────┬─────────┘
                               │                   │
                               ▼                   ▼
                 ┌──────────────────┐    ┌──────────────────┐
                 │Heuristics Engine │    │ VirusTotal API   │
                 │ (Offline/Python) │    │  (v3 Reputation) │
                 └─────────┬────────┘    └─────────┬────────┘
                           │                       │
                           └───────────┬───────────┘
                                       │
                                       ▼
                         ┌─────────────────────────────┐
                         │   Supabase (Cloud Postgres) │
                         │ SHA-256 Hash Caching & Slugs│
                         └─────────────────────────────┘
```

---

## 2. Backend Implementation & Pipeline Logic

The backend pipeline enforces a strict design principle: **Multi-layered evidence separation**. Deterministic offline heuristics and VirusTotal threat intelligence operate concurrently to establish complete risk verdicts without blocking or external AI model dependencies. (LLM client integration remains preserved as an optional enrichment module).

### 2.1 Entry Point & Middleware (`backend/main.py`)
- **FastAPI App Initialization:** Sets service title to `HookCheck` and initializes custom routing modules.
- **CORS Configuration:** Enforces `ALLOWED_ORIGIN` (configured via environment variables, e.g., `http://localhost:5173`) to restrict cross-origin requests.
- **Rate Limiting:** Integrates `SlowAPIMiddleware` using a shared `Limiter` instance (`backend/utils/limiter.py`). Registers a global `429 Too Many Requests` exception handler and injects standard `X-RateLimit-*` response headers.
- **Security Headers Middleware:** Appends HTTP security headers to all responses.

### 2.2 Analysis Pipelines (`backend/api/analyze.py`)

#### A. Text & URL Pipeline (`POST /analyze/text`)
1. **Input Normalization & Hashing:** Strips input text and computes a SHA-256 hash using `hash_content()` (`backend/utils/hashing.py`).
2. **Cache Check:** Queries Supabase (`get_cached_report()`) using `.maybe_single()` to check for an existing cached report matching `input_hash`. If found, returns the cached `FullReport` JSON immediately (<50ms).
3. **URL vs. Text Detection:**
   - If input is a single HTTP/HTTPS URL, delegates to `_analyze_url_pipeline`.
   - If input is free-form text, delegates to `_analyze_text_pipeline`.
4. **URL Execution Sequence:**
   - **Concurrent Execution:** Heuristics (`run_all_heuristics()`) and VirusTotal (`check_url_virustotal()`) are executed concurrently via `asyncio.gather()`.
   - **URL Shortener Resolution:** Checks if the domain is a known URL shortener via `check_url_features()`. If flagged, calls `safe_fetch_url()` (`backend/services/safe_fetch.py`) to follow redirect chains up to 5 hops safely, re-running Heuristics and VT concurrently on final targets.
5. **Score Aggregation:** Combines weights: **60% Heuristics + 40% VirusTotal** (falling back to 100% Heuristics if VirusTotal is unavailable or rate-limited).
6. **Report Generation & Storage:** Generates a random 12-character slug ID, constructs `FullReport`, caches it in Supabase via `store_report()`, and returns the payload.


#### B. Image & QR Pipeline (`POST /analyze/image`)
1. **File Validation:** Verifies upload file size is under 2 MB and validates MIME type.
2. **QR Code Scanning:** Passes raw bytes to `decode_qr()` (`backend/services/qr_decode.py`). If a QR code containing a URL is found, re-routes execution directly into the URL analysis pipeline.
3. **Vision LLM vs. OCR Fallback:**
   - Checks `supports_vision()` (`backend/services/llm_client.py`).
   - If Vision is supported: Converts image to Base64 and calls `call_llm_for_analysis()` directly with image payload.
   - If Vision is unsupported: Executes `extract_text_from_image()` (`backend/services/ocr_fallback.py`) via Tesseract OCR to extract plain text, then feeds extracted text into the text pipeline.

### 2.3 Heuristics Engine (`backend/services/heuristics/`)
Operates completely offline with zero external network requests:
- **`typosquat.py`:** Calculates Levenshtein edit distance ($\le 2$) against `tranco_top_domains.csv` (600 top legitimate domains).
- **`homograph.py`:** Inspects domain labels for non-ASCII Unicode confusable homoglyphs using `confusable_homoglyphs` and flags IDN Punycode (`xn--`) labels.
- **`subdomain.py`:** Uses `@functools.lru_cache` to check if trusted brand names appear in subdomains of untrusted registered base domains (e.g., `paypal.com.login-verify.ru`).
- **`tld.py`:** Matches TLD suffix against `suspicious_tlds.txt` (curated high-risk TLDs like `.xyz`, `.click`, `.zip`).
- **`url_features.py`:** Evaluates structural red flags using a pre-compiled regex union (`_BRAND_KEYWORDS_RE`) for path/query trigger keywords (`login`, `verify`, `wallet`), checks for raw IPv4 hostnames, URL length ($>100$ chars), and HTTP scheme usage.

### 2.4 SSRF & DNS Rebinding Protection (`backend/services/safe_fetch.py`)
Provides safe outbound HTTP requests for resolving redirect chains:
- **Scheme Restriction:** Permits `http://` and `https://` only.
- **Blocked IP Networks:** Rejects loopback (`127.0.0.0/8`), private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local/cloud metadata (`169.254.169.254`), IPv6 loopback (`::1`), and multicast.
- **Context-Local DNS Pinning:** Utilizes a `ContextVar` (`_dns_override`) patching `socket.getaddrinfo`. This pins the pre-verified safe IP address during `client.head` connection execution, preventing fast-flux DNS rebinding attacks while maintaining standard HTTPS domain TLS certificate verification.

### 2.5 LLM Integration (`backend/services/llm_client.py`)
- **Multi-Provider REST Client:** Built using `httpx` supporting Google Gemini, OpenAI, and Anthropic.
- **Prompt Isolation:** Wraps user input in explicit structural delimiters and instructs the LLM to treat content as data rather than instructions, mitigating prompt injection.
- **Format Enforcement & Retry:** Requests JSON output. If non-JSON output is returned, retries once with an explicit schema reminder before failing open gracefully to `_ai_unavailable_result()`.

---

## 3. API Specification & Schema Contracts

### 3.1 Endpoints

#### `POST /analyze/text`
- **Rate Limit:** `10/minute`
- **Request Body (`application/json`):**
  ```json
  {
    "content": "https://paypa1-security-update.xyz/login"
  }
  ```
- **Response (`200 OK` - `FullReport`):** (See Section 3.2)

#### `POST /analyze/image`
- **Rate Limit:** `10/minute`
- **Request Body (`multipart/form-data`):**
  - `file`: UploadFile (Max 2 MB, `image/png`, `image/jpeg`, `image/webp`)
- **Response (`200 OK` - `FullReport`):** (See Section 3.2)

#### `GET /analyze/report/{report_id}`
- **Rate Limit:** `30/minute`
- **Response (`200 OK`):** Returns the cached `FullReport` corresponding to the slug ID.
- **Response (`404 Not Found`):** If slug does not exist.

#### `GET /health`
- **Response (`200 OK`):**
  ```json
  {
    "status": "ok",
    "service": "HookCheck"
  }
  ```

### 3.2 Core Data Models (`backend/models/schemas.py`)

```typescript
// Equivalent TypeScript Interfaces used in Frontend (src/types/api.ts)

export interface HighlightedPhrase {
  phrase: str;
  explanation: str;
}

export interface AnalysisResult {
  risk_score: number; // 0 - 100
  threat_level: 'Low' | 'Medium' | 'High' | 'Critical';
  classification: 'Likely Safe' | 'Suspicious' | 'Likely Scam' | 'Likely Phishing';
  confidence: number; // 0 - 100
  reasons: string[];
  highlighted_phrases: HighlightedPhrase[];
  recommendations: string[];
}

export interface HeuristicsFindings {
  typosquatting_detected: boolean;
  homograph_detected: boolean;
  suspicious_tld: boolean;
  brand_impersonation: boolean;
  suspicious_url_features: boolean;
  resolved_final_url: string | null;
  notes: string[];
}

export interface ThreatIntelFindings {
  source: 'VirusTotal';
  available: boolean;
  malicious_votes: number | null;
  total_votes: number | null;
  notes: string[];
}

export interface FullReport {
  overall_risk_score: number; // 0 - 100
  threat_level: string;
  ai_findings: AnalysisResult;
  heuristics_findings: HeuristicsFindings;
  threat_intel_findings: ThreatIntelFindings;
  report_id: string;
  disclaimer: string;
}
```

---

## 4. Frontend Architecture & UI Component Tree

The frontend is a single-page application built with React 19, TypeScript, and Vite. It consumes the FastAPI endpoints via an API service client (`src/services/api.ts`).

### 4.1 Route Structure (`src/App.tsx`)
- `/` -> **Landing Page (`src/pages/Landing.tsx`):** Hero section, tabbed input switcher (Text/URL vs. Screenshot/QR), global paste event listener (`Ctrl+V`), drag-and-drop zone, and feature highlights.
- `/report/:id` -> **Report Permalink Page (`src/pages/Report.tsx`):** Displays aggregated risk badges, threat breakdown cards, reasons list, highlighted phrases, recommendations, and copyable report link. Injects dynamic `<meta name="robots" content="noindex, nofollow" />` tag into `document.head`.
- `/learn` -> **Educational Page (`src/pages/Learn.tsx`):** Detailed breakdown of how the 3 evidence layers work and prompt injection defenses.
- `/privacy` -> **Privacy Policy (`src/pages/Privacy.tsx`):** Details cryptographic hash caching and data retention policies.
- `/disclaimer` -> **Disclaimer (`src/pages/Disclaimer.tsx`):** Explains decision-support boundaries and limitations.

### 4.2 Component Architecture
- **`Topbar.tsx`:** Slim navigation header with brand logo (`HookCheck`), title, and navigation links.
- **`Footer.tsx`:** Page footer with legal/documentation links and GitHub repository reference.
- **`RiskBadge.tsx`:** Color-coded threat level indicator (Low/Medium/High/Critical) styled using custom CSS variables.
- **`EvidenceCard.tsx`:** Card container rendering individual layer findings (AI, Heuristics, or Threat Intel) with source-attributed labels.

---

## 5. Security, Privacy & Infrastructure Controls

| Security Domain | Implementation Details |
| :--- | :--- |
| **Data Privacy** | Raw user text and images are **never stored**. Inputs are normalized and converted to SHA-256 hex digests before database storage. |
| **SSRF / DNS Rebinding** | Context-local `ContextVar` DNS pinning in `safe_fetch.py` intercepts `socket.getaddrinfo`, preventing requests to internal IPs (`127.0.0.1`, `10.0.0.0/8`, `169.254.169.254`). |
| **Decompression Bomb Protection** | PIL `Image.MAX_IMAGE_PIXELS` set to `89,478,485` (~8000x8000). Image buffers are re-encoded to clean PNGs to strip EXIF data before pyzbar/Tesseract processing. |
| **Prompt Injection Defense** | Input is wrapped in structural delimiters in LLM prompts. Strict Pydantic JSON schema enforcement validates output structure. |
| **Rate Limiting** | `SlowAPIMiddleware` limits analysis endpoints to 10 requests/minute per IP and report lookups to 30 requests/minute per IP. |
| **Search Engine Indexing** | Dynamic metadata injection appends `noindex, nofollow` on report permalink pages to prevent search engine indexing. |
| **Containerization** | `Dockerfile` uses `python:3.11-slim` and explicitly installs native Linux binaries `libzbar0` (QR decoding) and `tesseract-ocr` (OCR fallback). |

---

## 6. Environment Configuration Reference (`.env`)

```env
# Backend Settings
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
LLM_API_KEY=your_gemini_api_key_here

VIRUSTOTAL_API_KEY=your_virustotal_api_key_here

# Supabase Database Caching
SUPABASE_URL=https://tfrbgthqszrxlfjpkwmn.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# Security & CORS
ALLOWED_ORIGIN=http://localhost:5173
RATE_LIMIT_PER_MINUTE=10
CACHE_TTL_HOURS=24

# Frontend Settings (Vite)
VITE_API_URL=http://localhost:8000
```
