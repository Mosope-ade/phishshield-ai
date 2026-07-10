# PhishShield AI

> Free, public, no-account web app that analyzes messages, links, screenshots, and QR codes to detect phishing and scam attempts — and explains exactly why.

**Three independent evidence layers** — AI, heuristics, VirusTotal — all labeled separately. None silently overrides the others.

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- A VirusTotal API key (free tier)
- An LLM provider API key (Gemini / OpenAI / Anthropic)
- A Supabase project

### 1. Clone & configure

```bash
git clone https://github.com/your-org/phishshield-ai.git
cd phishshield-ai
```

Copy and fill in both env files:

```bash
cp .env.example backend/.env
cp frontend/.env.example frontend/.env
```

Edit `backend/.env` and set every variable (see [Environment Variables](#environment-variables) below).

### 2. Backend setup

```bash
cd phishshield-ai
python3 -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

pip install -r backend/requirements.txt
```

Run the backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

App available at: http://localhost:5173

### 4. Database setup

Create a Supabase project and run this SQL in the SQL editor:

```sql
create table reports (
  id text primary key,
  input_hash text unique not null,
  input_type text not null,
  report_json jsonb not null,
  created_at timestamptz default now()
);
create index on reports (input_hash);

-- Row Level Security (SECURITY.md §9)
alter table reports enable row level security;

-- Public reads by slug ID only
create policy "public read by id"
  on reports for select
  using (true);

-- Writes restricted to service role (enforced by not granting anon insert)
create policy "service role write"
  on reports for insert
  with check (auth.role() = 'service_role');
```

---

## Running Tests (Phase 1)

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

Expected output: all tests in `test_heuristics.py`, `test_safe_fetch.py`, and `test_schema_validation.py` pass.

---

## Environment Variables

All variables are documented in [`.env.example`](.env.example). Backend variables:

| Variable | Description |
|---|---|
| `LLM_PROVIDER` | Provider name: `gemini`, `openai`, `anthropic` |
| `LLM_API_KEY` | API key for the LLM provider |
| `LLM_MODEL` | Model identifier (e.g. `gemini/gemini-1.5-pro`) |
| `VIRUSTOTAL_API_KEY` | VirusTotal Public API v3 key |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Service role key — **server-side only** |
| `SUPABASE_ANON_KEY` | Anon key — frontend read-only (optional) |
| `ALLOWED_ORIGIN` | Deployed frontend URL for CORS |
| `RATE_LIMIT_PER_MINUTE` | Per-IP rate limit (default: 10) |
| `CACHE_TTL_HOURS` | VirusTotal cache TTL in hours (default: 24) |

Frontend variable (in `frontend/.env`):

| Variable | Description |
|---|---|
| `VITE_API_URL` | Backend URL (default: `http://localhost:8000`) |

---

## Architecture

```
User input (text / URL / image / QR)
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│                    FastAPI Backend                        │
│                                                          │
│  ┌─────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Heuristics │  │   LLM (AI)     │  │  VirusTotal  │  │
│  │  engine     │  │   analysis     │  │  reputation  │  │
│  │ (no ext. I/O│  │ (prompt-inject │  │ (corroborate │  │
│  │  —fast, no  │  │  defended)     │  │  only — never│  │
│  │  injection) │  │                │  │  sole verdict│  │
│  └──────┬──────┘  └───────┬────────┘  └──────┬───────┘  │
│         │                 │                   │          │
│         └────────────┬────┘                   │          │
│                      │ Aggregated risk score  │          │
│                      │ (labeled by source)    │          │
│                      ▼                        │          │
│              ┌───────────────┐                │          │
│              │  FullReport   │◄───────────────┘          │
│              │  (Pydantic    │                           │
│              │   validated)  │                           │
│              └───────────────┘                           │
└──────────────────────────────────────────────────────────┘
        │
        ▼
  React Frontend
  (verdict-first, evidence-second,
   safe text rendering only)
```

---

## Folder Structure

```
phishshield-ai/
├── frontend/               React 19 + Vite + TypeScript
│   ├── src/
│   │   ├── pages/          Landing, Report, Learn, Privacy, Disclaimer
│   │   ├── components/     RiskMeter, RiskBadge, EvidenceCard, HighlightedText,
│   │   │                   RecommendationsList, ResultsBlock, Topbar, Footer
│   │   ├── hooks/          useAnalysis
│   │   ├── services/       api.ts (typed API client)
│   │   └── types/          api.ts (TypeScript interfaces)
│   └── .env.example
├── backend/
│   ├── api/                FastAPI routes (thin controllers)
│   │   ├── analyze.py      POST /analyze/text, POST /analyze/image, GET /analyze/report/:id
│   │   ├── prompts.py      LLM prompt construction (prompt-injection defended)
│   │   └── scoring.py      Risk score aggregation (defense-in-depth weighted)
│   ├── services/
│   │   ├── heuristics/     typosquat, homograph, tld, subdomain, url_features
│   │   ├── llm_client.py   LiteLLM provider-agnostic wrapper + vision support
│   │   ├── virustotal.py   VT v3 URL + hash endpoints
│   │   ├── safe_fetch.py   SSRF-safe URL fetcher (SECURITY.md §4)
│   │   ├── qr_decode.py    pyzbar + Pillow QR decoder
│   │   └── ocr_fallback.py Tesseract OCR fallback
│   ├── models/schemas.py   Pydantic v2 schemas (LLM output contract + API types)
│   ├── db/cache.py         Supabase cache (hash-only, parameterized)
│   ├── utils/              hashing.py, sanitize.py
│   ├── data/               tranco_top_domains.csv, suspicious_tlds.txt, etc.
│   ├── main.py             FastAPI app: CORS, rate limiting, security headers
│   └── requirements.txt
├── tests/
│   ├── test_heuristics.py      25 unit tests, known-bad + known-good domains
│   ├── test_safe_fetch.py      11 tests, all private IP ranges + scheme checks
│   └── test_schema_validation.py  13 tests, LLM output validation
├── docs/
│   ├── privacy.md
│   └── disclaimer.md
├── .env.example
├── .gitignore              (.env excluded from first commit)
├── pytest.ini
├── PROGRESS.md
└── README.md
```

---

## Security

See [`SECURITY.md`](SECURITY.md) for the full mandatory secure-coding requirements.
Key controls:
- **SSRF protection** — all user-URL fetches via `safe_fetch.py`, never raw `httpx`
- **Prompt injection defense** — user content always in delimited blocks; heuristics + VT provide independent checks
- **LLM output validation** — all LLM responses validated against Pydantic schema before use
- **No raw user content stored** — only SHA-256 hashes
- **Rate limiting** — per-IP via `slowapi`
- **CORS** — locked to `ALLOWED_ORIGIN`, no wildcard

---

## Deployment

- **Frontend** → Vercel (connect GitHub repo, set `VITE_API_URL` in project settings)
- **Backend** → Fly.io or Railway (containerized, set env vars as platform secrets)
- **Database** → Supabase (run the schema SQL above, configure RLS)

See [`PLAN.md §11`](PLAN.md) for full deployment notes.
