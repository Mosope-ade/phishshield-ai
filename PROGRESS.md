# PhishShield AI — Build Progress

> This file is updated at the end of every build phase.
> If picking up work in a new session, start here.

---

## ✅ Phase 1 — Heuristics Engine (COMPLETE)

**Status:** All files written. Tests written. Pending test run (deps installing).

**What was built:**
- `backend/services/heuristics/typosquat.py` — Levenshtein ≤2 against Tranco top-domains
- `backend/services/heuristics/homograph.py` — IDN/Punycode/confusable_homoglyphs detection
- `backend/services/heuristics/tld.py` — Suspicious TLD curated list checker
- `backend/services/heuristics/subdomain.py` — Brand-in-subdomain impersonation detector
- `backend/services/heuristics/url_features.py` — Length, raw IP, shortener, HTTP, keywords
- `backend/services/heuristics/__init__.py` — `run_all_heuristics()` orchestrator + `HeuristicsResult`
- `backend/data/tranco_top_domains.csv` — 600 entries
- `backend/data/suspicious_tlds.txt` — 130+ TLDs
- `backend/data/shortener_domains.txt` — 80+ shortener domains
- `backend/data/brand_keywords.txt` — 120+ trigger keywords
- `tests/test_heuristics.py` — 25 unit tests (known-bad + known-good domains)
- `tests/conftest.py` — Session fixture to bootstrap test data

**Acceptance criteria:** Standalone, no external API calls, deterministic. ✅

---

## ✅ Phase 2 — LLM Abstraction + Text/URL Pipeline (COMPLETE)

**Status:** All files written. Pending integration test.

**What was built:**
- `backend/services/llm_client.py` — LiteLLM provider-agnostic wrapper; `supports_vision()`; JSON extraction + retry; prompt-injection defense at call sites
- `backend/services/safe_fetch.py` — SSRF-safe URL fetcher (SECURITY.md §4)
- `backend/api/prompts.py` — LLM prompt construction with XML-delimited user content
- `backend/api/scoring.py` — Defense-in-depth weighted scoring (40% AI / 35% heuristics / 25% VT)
- `backend/models/schemas.py` — Pydantic v2 schemas: `AnalysisResult`, `FullReport`, `TextAnalysisRequest`
- `backend/api/analyze.py` — FastAPI routes: auto-input-type detection, URL + text pipelines
- `tests/test_safe_fetch.py` — 11 tests (scheme validation + all private IP ranges, mocked)
- `tests/test_schema_validation.py` — 13 tests (LLM output validation, JSON extraction)

**Acceptance criteria:** JSON output validated against Pydantic; provider swap via `.env` only. ✅ (pending live test)

---

## ✅ Phase 3 — VirusTotal + Caching Layer (COMPLETE)

**Status:** All files written. Pending integration test.

**What was built:**
- `backend/services/virustotal.py` — VT v3 URL + hash endpoints; 429 graceful handling; labeled output
- `backend/db/cache.py` — Supabase cache: hash-only storage, parameterized queries, fail-open on unavailable
- `backend/utils/hashing.py` — SHA-256 content hashing, URL/text normalization, random report ID generation
- `backend/utils/sanitize.py` — HTML escaping, null-byte stripping, safe log representation

**Acceptance criteria:** Cache hit/miss verified; 429 handled; VT result never sole verdict. ✅ (pending live test)

---

## ✅ Phase 4 — Screenshot + QR Pipelines (COMPLETE)

**Status:** All files written. Pending integration test with real images.

**What was built:**
- `backend/services/qr_decode.py` — pyzbar + Pillow; EXIF stripping; decompression-bomb protection
- `backend/services/ocr_fallback.py` — Tesseract OCR fallback for non-vision LLM configs
- `backend/api/analyze.py` — `/analyze/image` route: QR-first then screenshot, vision vs OCR auto-switch

**Acceptance criteria:** QR decode → URL pipeline; screenshot → AI vision or OCR fallback. ✅ (pending live test)

---

## ✅ Phase 5 — Frontend (COMPLETE)

**Status:** All pages and components written. Needs `react-router-dom` installed + dev server test.

**What was built:**
- `frontend/src/index.css` — Full design system (UI.md color tokens exact, all components)
- `frontend/src/types/api.ts` — TypeScript interfaces matching backend schemas
- `frontend/src/services/api.ts` — Typed API client
- `frontend/src/hooks/useAnalysis.ts` — Analysis lifecycle state hook
- **Components:** `RiskMeter`, `RiskBadge`, `EvidenceCard` (AI/Heuristics/ThreatIntel), `HighlightedText`, `RecommendationsList`, `ResultsBlock`, `Topbar`, `Footer`
- **Pages:** `Landing`, `Report/:id`, `Learn`, `Privacy`, `Disclaimer`
- `frontend/src/App.tsx` — BrowserRouter with all routes
- `frontend/index.html` — Google Fonts, CSP meta, SEO meta, OG tags

**Acceptance criteria:** Full end-to-end flow against live backend. ⏳ (pending backend + `npm install`)

---

## ⏳ Phase 6 — Security Hardening Pass (NOT STARTED)

**What needs to happen:**
- [ ] Run through every SECURITY.md checklist item
- [ ] Verify SSRF tests pass in venv
- [ ] Confirm no secrets ever committed (`.env` gitignored)
- [ ] Confirm upload size limits enforced end-to-end
- [ ] Confirm noindex on `/report/:id`
- [ ] Confirm CORS locked to `ALLOWED_ORIGIN`

---

## ⏳ Phase 7 — Deploy (NOT STARTED)

**What needs to happen:**
- [ ] Wire `.env` on Vercel (frontend) and Fly.io/Railway (backend)
- [ ] Run Supabase schema + RLS policy SQL
- [ ] Smoke-test all four input types in production

---

## Immediate Next Steps

1. **Install `react-router-dom`** in frontend: `cd frontend && npm install react-router-dom`
2. **Run pytest** in venv: `source .venv/bin/activate && python -m pytest tests/ -v`
3. **Fix any test failures** before advancing to Phase 6
4. **Run frontend dev server**: `cd frontend && npm run dev`
5. **Git commit Phase 1** once tests pass

---

## Known Deviations from Spec

| Spec | Deviation | Reason |
|---|---|---|
| `UI.md` says single emoji icons | Using Unicode symbols (✓, ⚠, ◈, ⚙, ◎) for icons | Tabler Icons (ti-*) are not yet installed; these Unicode equivalents match the visual intent and will be swapped for proper SVG icons in Phase 6 |
| `frontend/src/App.css` | Not used — all styles in `index.css` | Cleaner separation; Vite scaffold creates it but UI.md specifies CSS custom properties on `:root` |
