# Sahaara AI

Multilingual, real-time **decision-support** platform for helpline operators — AI-assisted
distress & victim-safety assessment with mandatory human review, case management, referral
routing and operational analytics.

> **AI as support, never as decision-maker.** Sahaara identifies *observable indicators* and
> prioritises human review. It never diagnoses, never acts autonomously, and remains fully
> usable when AI providers are down (**Human Assessment Mode** — Feature 1.14).

---

## What was built

### Phase 1 — Core (Original Requirements 1.1–1.15)

| Feature | Where |
|---|---|
| 1.1 Distress assessment (rule engine, evidence-linked) | `backend/app/ai/analysis.py` |
| 1.2 Voice + text intake (WS stream, browser ASR, audio chunks) | `backend/app/routers/stream.py`, `frontend/src/hooks/useSpeech.js` |
| 1.3 Multilingual (English, हिन्दी, मराठी + confidence + override) | `backend/app/ai/language.py` |
| 1.4 Review Priority Score (weighted, explainable) | `backend/app/ai/priority.py` |
| 1.5 Explainable indicators (evidence, excerpt, timestamp, confidence, source) | `backend/app/ai/analysis.py`, `frontend/src/components/FlagsPanel.jsx` |
| 1.6 Human-in-the-loop (confirm / modify / escalate / dismiss + notes) | `backend/app/routers/cases.py`, review UI |
| 1.7 Case management (lifecycle, consent, timeline, notes, follow-ups) | `backend/app/models.py`, `frontend/src/pages/CaseDetail.jsx` |
| 1.8 / 2.16 Referral pathways — AI suggests, humans confirm | `backend/app/routers/cases.py` |
| 1.9 Summaries — generative + **extractive fallback**, provenance label | `backend/app/ai/summary.py`, `backend/app/ai/llm.py` |
| 1.10 Privacy — consent-first, anonymization, no raw-audio retention | `backend/app/ai/anonymize.py`, `backend/app/config.py` |
| 1.11 RBAC (admin / operator / supervisor / counsellor) | `backend/app/deps.py`, `frontend/src/api/roles.js` |
| 1.12 Analytics (cases/day, languages, priorities, AI-vs-human) | `backend/app/routers/analytics.py`, `frontend/src/pages/Analytics.jsx` |
| 1.13 Auditability | `backend/app/audit.py`, `backend/app/routers/audit.py`, Audit page |
| 1.14 Graceful AI failure → Human Assessment Mode | `backend/app/ai/llm.py`, mode banner in UI |
| 1.15 Scripted multilingual demonstrations | `backend/app/routers/demos.py`, demo cards on Queue |

### Phase 2 — NHAA research enhancements (2.x, implemented layer)

- **2.1/2.2** Multidimensional Victim Safety & Wellbeing Profile (8 dimensions)
- **2.4** Immediate safety assessment (keywords + volume evidence)
- **2.5** **Safety Override Engine** — rules beat weighted score; dismiss blocked, queue pinned
- **2.6** Self-harm screening pathway · **2.7** trauma indicators
- **2.9** Code-switching detection with switch points (never treated as silence)
- **2.10** Uncertainty-aware assessment (confidence, evidence quality, missing info, abstain)
- **2.11** Context-aware speech interpretation (alternative explanations recorded)
- **2.12** Possible coercion/interference (always non-definitive)
- **2.13** Trauma-informed mode (no “Why” questions, pause-paced prompts, reassurance)
- **2.17** Longitudinal follow-ups (intervention → follow-up → reassessment)
- **2.20/2.21/2.24** Evaluation metrics (sensitivity, specificity, F1, AUROC, AUPRC,
  calibration, fairness-by-language) + research monitor — `backend/app/ai/metrics.py`

### Operations toolkit (added console functions)

| Function | Where |
|---|---|
| Case export — CSV/JSON, sanitized (no transcript/notes), **audited** | `GET /api/v1/cases/export`, Export buttons on Cases |
| Queue filters — status, language, safety-only, assigned to me / unassigned | `GET /api/v1/cases?language=&safety=&assigned=` |
| Case assignment workflow — supervisor/counsellor assigns, operator self-assigns, always audited | `PATCH /api/v1/cases/{id}` (`assigned_to`), Assignment card |
| Notification centre — derived feed of safety overrides, due/overdue follow-ups, pending referrals, assignments (60 s poll, client-side read state) | `backend/app/routers/notifications.py`, bell in nav pill |
| Follow-up reminders — due dates, overdue highlighting, one-click “Mark done” | `POST/PATCH /api/v1/cases/{id}/followups[/{fid}]`, CaseDetail |
| Settings page — display name, interface language, password change (audited), system health | `PATCH /api/v1/auth/me`, `frontend/src/pages/Settings.jsx` |
| Assignable-user directory (scoped: admin/supervisor/counsellor only) | `GET /api/v1/users/assignable` |
| Friendly API index at `/` (replaces FastAPI's `{"detail":"Not Found"}`) | `backend/main.py` |

## Stack

- **Backend:** Python · FastAPI · SQLAlchemy (SQLite dev / PostgreSQL prod) · JWT + RBAC · WebSocket
- **Frontend:** React (Vite) · design system generated with [`getdesign`](https://getdesign.md)
  (`npx getdesign@latest add starbucks --out ./docs/DESIGN.md`) and adapted into
  `frontend/src/styles/tokens.css` — warm cream canvas, four-tier Starbucks-green brand system,
  House-Green dark bands/footer, 12px cards, full-pill buttons with the signature press,
  Inter substituting the proprietary SoDoSans, red reserved for safety states only
- **AI:** deterministic rule engine always available; optional OpenAI (LLM summaries + Whisper ASR)
  with transparent failover

## Run it

### 1. Backend (port 8010)

```bash
cd backend
uv venv --python 3.12 .venv            # or: python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env                   # optional: add OPENAI_API_KEY for generative AI
.venv/bin/python -m uvicorn main:app --port 8010
```

> Port 8000 is intentionally avoided here (commonly occupied); change freely via `--port`.
> The DB schema bootstraps automatically (`database/schema.sql` is the PostgreSQL reference).

### 2. Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev        # open http://localhost:5173
```

`VITE_API_URL` (env) points the UI at a non-default backend.

### 3. Sign in

| Username | Password | Role |
|---|---|---|
| `operator` | `operator123` | Operator |
| `counsellor` | `counsel123` | Counsellor / Reviewer |
| `supervisor` | `super123` | Supervisor |
| `admin` | `admin123` | Administrator |

**Try it:** Queue → *New session* (consent required) → type/voice lines, or run one of the
scripted **demo scenarios** (English danger, Hindi distress, Marathi coercion, code-switching).

### 4. Deploy the frontend to Vercel

A root `vercel.json` is included:

```jsonc
{
  "framework": "vite",
  "installCommand": "cd frontend && npm ci",
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]  // SPA fallback
}
```

1. Import the repo in Vercel (framework preset auto-detected) — the config above builds
   `frontend/` and serves the SPA with history fallback; `robots.txt`/`sitemap.xml` ship
   from `frontend/public/`.
2. Set **`VITE_API_URL`** to your hosted backend origin (the UI reads it at build time;
   WebSockets derive from it automatically).
3. The FastAPI backend runs anywhere Python runs (Render, Railway, Fly, a VPS):
   `uvicorn main:app --port 8010`. SQLite is dev-only — set `DATABASE_URL` to
   PostgreSQL (`database/schema.sql` is the reference DDL).
4. Replace the placeholder domain `https://sahaara.ai` in `frontend/index.html`,
   `frontend/src/lib/seo.js`, `frontend/public/robots.txt` and
   `frontend/public/sitemap.xml` with your real origin.

`GET /` on the API returns a friendly index (name, health, endpoint map, demo logins) —
`/health` stays the liveness probe and `/docs` serves the OpenAPI explorer.

## Tests

```bash
cd backend
.venv/bin/python -m pytest tests -q
```

32 → **41** tests cover: safety-override precedence, priority clamping, language detection,
code-switching, anonymization, evaluation metrics, RBAC, the full case lifecycle,
audit trail presence and graceful AI fallback (per `build/test-plan.md`) — plus the
operations toolkit: sanitized/audited export, queue filters, assignment round-trip,
follow-up reminders + notification feed, profile/password settings, root API index,
and a regression test for JSON change-tracking (flag decisions & follow-ups persist).

## Verification harness (with Jev / TypeSafe)

`scripts/jev_check.py` checks the whole system in two layers:

1. **Deterministic** (always runs) — health, safety-override, queue pinning, RBAC,
   summary provenance, flag explainability, dismiss-blocking against the live API.
2. **Jev cross-checks** (needs a TypeSafe API key) — each case is sent to Jev in
   **one request with speculative fan-out**; typed judgments are compared with the
   rule engine: flag evidence support, no-diagnosis safety property, statement/inference
   separation, distress & danger levels, coercion, language, urgency vs priority band.
   Code holds all thresholds (noul ≥ 0.65 agree / ≤ 0.35 contradict / in-between =
   uncertain→skip; Choice confidence ≥ 0.6), so uncertain judgments never pass or fail.

```bash
# Layer 1 only (no key needed):
python scripts/jev_check.py

# Full run with Jev:
#   1. get a key at https://console.typesafe.ai/keys
#   2. TYPESAFE_API_KEY=... python scripts/jev_check.py
```

Exit code 0 = pass (warnings list Jev disagreements for human review), 1 = failed check.

## Safety design notes

- **Dual-layer scores** (Decision 1): `ReviewPriorityScore` (operational queue) is always
  shown separately from `VictimSafetyProfile` (analytical) — neither is a clinical measure.
- **Safety Override** (2.5): immediate-danger / self-harm / coercion / volume-spike rules force
  top priority; safety-critical flags cannot be dismissed while active.
- **Safe Exit** (2.23): press `Esc` twice → wipes storage/clipboard/indexedDB and leaves to a
  neutral page (discreet ✕ button also available).
- **Transparency** (ethics doc): summaries are labelled “Generated by AI (Confidence: x)”
  or “Extracted Fallback”.

## Public site, SEO & legal pages

Logged-out visitors get a public marketing site (authenticated users landing on `/` go
straight to the queue):

- **`/`** — landing page with hero, stats and the SEO article about the tool
  (988 words, source of truth in `docs/seo-copy.md`), plus an 8-question **FAQ section**
  with `FAQPage` JSON-LD structured data.
- **`/about`**, **`/privacy`**, **`/terms`**, **`/contact`** — content pages with
  per-page titles, meta descriptions and canonical URLs (see `src/lib/seo.js`).
- **Error pages** — `404` catch-all route and a `500` page rendered by the app-wide
  `ErrorBoundary` on uncaught errors.
- **`frontend/public/robots.txt`** (disallows `/api/`, `/login` and all console routes)
  and **`frontend/public/sitemap.xml`**.
- `index.html` carries the full base meta set: description, keywords, Open Graph,
  Twitter card, canonical and `SoftwareApplication` JSON-LD — so non-JS crawlers still
  see complete metadata.

Mobile responsiveness: breakpoints at 900/840/720/520 px (grid collapse, compact
scrollable nav pill, stacked stats, horizontally scrollable data tables, reduced
typography). Verified at a true 390 px viewport — every route has zero horizontal
overflow (`scripts/` probe used headless Chrome + puppeteer-core).

> Before deploying: replace the placeholder domain `https://sahaara.ai` in
> `index.html`, `src/lib/seo.js`, `robots.txt` and `sitemap.xml` with your real origin.
