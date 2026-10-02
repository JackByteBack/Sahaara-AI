# Sahaara AI — About the Tool (SEO Copy)

> Source of truth for the public landing page copy (`frontend/src/pages/Landing.jsx`).
> Target: 800–1200 words. Primary keywords: AI distress detection, helpline case
> management, multilingual (English/Hindi/Marathi) analysis, human-in-the-loop AI,
> victim safety assessment, explainable AI flags.

## Sahaara AI: AI-Assisted Distress Assessment and Case Management for Helplines

Every day, helpline operators listen to people on the worst day of their lives. A caller
may speak softly, switch between languages, pause mid-sentence, or describe a threat so
quietly that its seriousness is easy to miss. Sahaara AI is a decision-support platform
built for exactly that moment. It listens alongside the operator, surfaces observable
distress and safety indicators in real time, and organises the work that follows —
review, referral, follow-up — while leaving every consequential decision in human hands.

### Decision support, not diagnosis

Sahaara AI identifies indicators, never disorders. Its purpose is to help a trained
reviewer notice what was said, how urgent it is, and what deserves attention first. The
system never concludes that a caller "has" a condition, never issues a clinical label,
and never acts on its own: escalation, referral, dismissal and closure are always human
actions recorded in an audit trail. This human-in-the-loop design is not a fallback
philosophy — it is enforced in the product. AI flags arrive as suggestions with the
supporting transcript excerpt, timestamp, confidence and source model attached, so a
reviewer can see exactly why something was flagged before confirming, modifying,
escalating or dismissing it.

### Real-time, explainable analysis

When a session begins — by voice or typed text — audio and messages stream through a
live pipeline. Language is detected first, then the conversation is scanned for
observable indicators: expressions of fear or hopelessness, self-harm concerns,
immediate-danger language, trauma narratives, and signals that a caller may not be
speaking freely. Each detection becomes an explainable flag linked to its evidence.
Nothing appears on screen without a reason attached to it, because in a high-stakes
environment an unexplained alert is worse than no alert at all.

If generative AI is unavailable or a provider fails, Sahaara does not go dark. The
deterministic rule engine, transcript display, case creation and full review workflow
continue to operate in Human Assessment Mode, with a visible banner telling the operator
exactly what changed. Graceful degradation is a safety requirement, not a convenience.

### Two scores that are never confused

Most triage tools collapse everything into a single number. Sahaara deliberately does
not. The Review Priority Score answers one operational question — how urgently should a
human look at this case — and is built from weighted linguistic, contextual, conversation
and speech components. The Victim Safety & Wellbeing Profile answers a different
question — what might this person need — across eight dimensions including psychological
distress, trauma indicators, immediate danger, self-harm concern, coercion, and social,
medical and legal vulnerability. Keeping the two apart stops an operational queue metric
from being misread as a psychological measurement.

Crucially, explicit safety rules can override the score entirely. If the transcript
indicates an immediate physical threat, a self-harm concern, possible coercion, or an
alarming change in voice volume, the case is pinned to the top of the queue, safety-critical
flags cannot be dismissed, and the interface itself changes to demand attention. A critical
signal must never be hidden by an average.

### Built for Indian helplines

India's helplines operate across languages, often within a single conversation. Sahaara
ships with English, Hindi and Marathi support — detection, confidence scoring,
original-language transcripts and optional English glosses — and detects mixed-language
speech, tagging switch points rather than misreading them as silence. Additional Indian
languages are recognised at script level as the research programme expands coverage.
Code-switched speech like "Mala khup bhiti vatate… they are threatening me" is treated as
one continuous account, preserving the caller's own words throughout.

### Trauma-informed by default

The interface can operate in a trauma-informed mode that asks fewer questions, avoids
"why" prompts that can sound like blame, follows the caller's pauses instead of rushing
them, and puts reassurance one tap away. For victims using a potentially unsafe device,
a discreet Safe Exit — double-press Escape — wipes local storage, clipboard and cached
data and leaves to a neutral page.

### From conversation to support pathway

Analysis flows into full case management: consent capture, status lifecycle, notes,
longitudinal follow-ups, and referral pathways spanning counselling, medical aid, legal
aid, protection, shelter and welfare. AI may suggest a pathway; only a confirmed human
creates or confirms it. Summaries separate what the caller said from what the system
inferred, and always carry a provenance label — "Generated by AI (Confidence: x)" or
"Extracted Fallback" — so no one is ever unsure who wrote a sentence.

### Security, privacy and accountability

Consent gates every session, raw audio is discarded after processing by default, and
closing a case scrubs names, phone numbers and locations from the record. Access runs
through role-based permissions — administrator, supervisor, counsellor and operator each
see only what their role requires — while login, transcript access, AI analysis,
modifications, escalations, referrals, exports and deletions are written to a durable
audit log. Sensitive mental-health and potentially criminal information should never
travel through a tool that cannot account for who looked at it and when.

### A research foundation

Sahaara doubles as a research environment for evaluating AI-assisted victim safety
assessment: evaluation metrics from sensitivity and specificity to AUROC and calibration,
fairness reporting across languages, human-AI agreement tracking, and a monitoring layer
designed to surface model drift and subgroup disparities before they matter. Synthetic,
scripted demonstrations in multiple languages make training and evaluation repeatable
without exposing a single real caller to risk.

### Getting started

Sahaara AI runs anywhere a helpline already works: a FastAPI backend with SQLite for
evaluation or PostgreSQL for production, and a browser-based console that needs nothing
beyond a modern device and a connection. Sign in with a role, open a session with consent,
and the queue does the rest — safety-override cases first, everything else ordered by
review priority. Operators who have never used an AI tool before will find the interface
familiar: a transcript, a set of flagged suggestions, and buttons that make clear the
final decision is theirs to make.
