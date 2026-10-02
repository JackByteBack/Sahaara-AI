# Technical Decisions Log

## Decision 1: Dual-Layer Assessment Architecture

- **Why:** The original single "Review Priority Score" (1.4) was conflating operational urgency with clinical risk. Research indicated that high vulnerability doesn't always mean urgent review, and vice versa.
- **Implementation:** Separation of `ReviewPriorityScore` (Operational) from `VictimSafetyProfile` (Clinical/Research).
- **Trade-off:** Increases UI complexity (two different scoring metrics) but provides more granular control for human reviewers.

## Decision 2: Separation of Generative and Extractive Summaries

- **Why:** Relying solely on Generative AI for summaries poses a hallucination risk in high-stakes environments. Feature 1.9 mandates a deterministic fallback.
- **Implementation:** Pipeline structure requiring a generative component, but a "Flag/Extract" component as the mandatory backup.
- **Trade-off:** Extractive summaries may be less concise than generative ones, but significantly more auditable.

## Decision 3: Voice-First Interaction with Text Fallback

- **Why:** Helplines operate in low-bandwidth or noisy environments where typing is difficult (Feature 1.2).
- **Implementation:** Live voice capture with Speech-to-Text (ASR) as the primary input method.
- **Trade-off:** Depends heavily on the ASR engine's ability to handle dialects and code-switching (Feature 2.9).

## Decision 4: Role-Based Access Control (RBAC) Scope

- **Why:** The system handles sensitive mental health and potentially illegal activities (trauma/coercion).
- **Implementation:** Roles include Admin, Operator, Supervisor, and Counsellor (Feature 1.11).
- **Trade-off:** More complex permission management than a simple "staff" role, necessary for audit trails (Feature 1.13).
