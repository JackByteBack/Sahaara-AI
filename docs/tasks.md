# Development Roadmap

## Phase 1: Core Implementation (Original Requirements)

- [x] **1.2 & 1.3:** Set up Voice (WebRTC/browser ASR) and Text intake interfaces. — `routers/stream.py`, `hooks/useSpeech.js`, session console
- [x] **1.1 & 1.5:** Implement Distress Detection and Explainable AI Flagging. — `ai/analysis.py`, `FlagsPanel.jsx`
- [x] **1.6:** Implement Human-in-the-Loop UI (Approve/Modify/Dismiss). — `routers/cases.py` (flag + case decisions), review UI
- [x] **1.7:** Build Case Management CRUD. — `models.py`, `routers/cases.py`, `CaseDetail.jsx`
- [x] **1.10:** Implement Privacy/Anonymization and Encryption. — `ai/anonymize.py`, consent-first sessions, JWT, PBKDF2 hashing, no raw-audio retention
- [x] **1.14:** Implement Graceful Failure (Human Mode fallback). — `ai/llm.py` failover, mode banner, rule engine always available

## Phase 2: Research Enhancements (NHAA)

- [x] **2.1, 2.2, 2.4:** Build Multidimensional Vulnerability and Safety Profile models. — 8-dimension profile in `ai/analysis.py`
- [x] **2.5:** Implement Safety Override Engine logic. — `ai/priority.py` (+ tests, UI dismiss-block, queue pinning)
- [ ] **2.9, 2.8:** Research and implement Code-Switching and Indian Dialect support.
  - [x] Code-switching detection + switch points (`ai/language.py`, Feature 2.9)
  - [x] Script-level detection for 8 additional Indian languages (Feature 2.8 groundwork)
  - [ ] ASR accuracy evaluation for dialects — needs real datasets (blocked on 2.18)
- [x] **2.14, 2.15:** Implement Narrative Continuity and Role-based Data Sharing.
  - [x] Role-based access scoping (`deps.py` capability map — need-to-know)
  - [ ] Structured narrative hand-off view across counsellor/legal/medical — future work
- [x] **2.20, 2.21:** Set up Evaluation Framework (Metrics, Human-AI agreement analysis). — `ai/metrics.py`, `/api/v1/research/evaluate`, AI-vs-human analytics panel

## Phase 3: Evaluation & Dataset

- [ ] **2.18:** Curate NHAA Trauma-Safety Dataset. — future work (ethics/consent-dependent)
- [ ] **2.19:** Establish Multimodal Benchmark. — future work

## Delivered in this build

- FastAPI backend (JWT/RBAC, WebSocket live stream, audit trail, rate limiting, seeded demos)
- React console (queue, live session, case review, analytics, audit, safe exit)
- Design system from `docs/DESIGN.md` — **Starbucks template installed via
  `npx getdesign@latest`** and adapted into `frontend/src/styles/tokens.css`
  (cream canvas, green brand system, dark-green bands/footer, pill press states)
- Operations toolkit: audited CSV/JSON case export, queue filters
  (status/language/safety/assignment), case assignment workflow, notification centre
  (safety overrides, due follow-ups, pending referrals, assignments),
  follow-up due dates + completion, Settings page (profile/language/password,
  audited), friendly API index at `/`
- `database/schema.sql` (PostgreSQL reference), README with run instructions
  + Vercel deployment guide (`vercel.json` included)
- **41 passing tests** (`backend/tests`), incl. JSON change-tracking regressions
  (flag decisions & follow-ups persist)
- Public site & SEO: landing page (988-word article in `docs/seo-copy.md`), FAQ section
  with FAQPage JSON-LD, About/Privacy/Terms/Contact pages, per-page meta tags,
  robots.txt, sitemap.xml, 404 + 500 error pages (ErrorBoundary)
- Mobile-responsive pass: 900/840/720/520 px breakpoints, scrollable nav pill and
  data tables, verified zero horizontal overflow at 390 px on every route
