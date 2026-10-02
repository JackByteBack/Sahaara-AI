# AI Agent Instructions for Sahaara AI

## Project Context

Sahaara AI is a dual-purpose platform: a core decision-support tool for helpline operators and a research environment for evaluating AI-assisted victim vulnerability and trauma assessment (NHAA research).

## Core Rules

1.  **Preserve Feature Separation (Critical):**
    - **Original Requirements (1.1–1.15):** These represent the mandatory, production-ready features. This includes distress assessment, multilingual support (En/Hin/Marathi), review priority scoring, and case management.
    - **Additional Features (2.1–2.24):** These represent the NHAA research enhancements. Do not treat them as core functionality but as an extension layer.
    - **Action:** When implementing code or changing logic, explicitly reference the numbering scheme (e.g., "Feature 1.3" vs "Feature 2.9") to ensure the scope is respected.

2.  **Human-in-the-Loop Compliance:**
    - **Rule:** AI must never make autonomous decisions (diagnosis or clinical assessment).
    - **Rule:** All AI flags must be presented as "suggestions" with evidence. The final decision (escalate, dismiss, refer) must always be a human action.
    - **Rule:** The system must never fail silently; if AI is unavailable, it must fall back to "Human Assessment Mode" (Feature 1.14).

3.  **Data Privacy and Safety:**
    - **Rule:** Consent is mandatory for processing. Raw audio retention is _not_ default (Feature 1.10).
    - **Rule:** Implement "Safety Mode" protections for victims using potentially unsafe devices (Feature 2.23) to prevent eavesdropping or retaliation.

4.  **Language and Localization:**
    - **Core:** En, Hindi, Marathi.
    - **Future/Research:** Indian dialects (Bengali, Telugu, etc.) and code-switching handling (Feature 2.9) are part of the research scope, not the current release.

## Coding Conventions

- **Naming:** Use clear naming conventions for review priority vs. vulnerability scores (e.g., `ReviewPriorityScore` vs `VictimSafetyProfile`).
- **Evidence Tracking:** Every AI indicator (Feature 1.5) must be timestamped, linked to transcript text, and traceable to a specific model version.
- **Safety Overrides:** Safety rules (Feature 2.5) must take precedence over weighted priority scores.

## Workflow Restrictions

- **AI Failure:** If the AI provider (generative or rule-based) fails, the transcript display and basic case management (creation/status) must remain fully operational.
- **Demonstration Data:** The system must allow easy toggling of demonstration/simulated conversations (Feature 1.15) for testing purposes.
