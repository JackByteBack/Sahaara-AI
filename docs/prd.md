# Product Requirements Document: Sahaara AI

## 1. Executive Summary

Sahaara AI is a multilingual, real-time decision support platform for helpline operators. It combines voice/text processing, AI-assisted distress and vulnerability assessment, and case management. The system is designed as a hybrid tool: a production-ready case management interface and a research environment for validating AI models for victim safety and trauma assessment.

## 2. Core Functionality (Original Requirements)

- **Voice & Text Interaction:** Supports live voice capture (ASR) and typed sessions, including demo simulations.
- **Multilingual Support:** Detects and processes English, Hindi, and Marathi with confidence scores.
- **AI-Assisted Distress Assessment:** Real-time analysis of conversations to flag observable distress indicators with evidence and confidence levels.
- **Review Priority Scoring:** Calculates a weighted score to determine human review urgency.
- **Explainable AI:** Provides timestamps, transcript excerpts, and model sources for every AI flag.
- **Human-in-the-Loop:** Mandatory human review and action (Confirm, Modify, Escalate, Dismiss).
- **Case Management:** Full lifecycle management including creation, consent, timeline, notes, referrals, closure, and anonymization.
- **Privacy & Security:** Consent-first processing, role-based access (Admin, Operator, Supervisor, Counsellor), and audit logging.

## 3. Research Enhancements (Additional Features)

- **Victim Vulnerability Profile:** A multidimensional assessment beyond distress (including legal, social, and medical vulnerability).
- **Safety Override Engine:** Explicit rules to override priority scores when immediate physical danger is detected.
- **Trauma & Coercion Detection:** Specialized indicators for trauma exposure and possible coercion/interference.
- **Code-Switching Detection:** Ability to identify and process mixed-language conversations (e.g., Marathi/Hindi).
- **Trauma-Informed Mode:** A specialized conversation mode minimizing traumatic disclosure.
- **Longitudinal Monitoring:** Ability to track cases over time (Assessment -> Intervention -> Follow-up).
- **Expanded Evaluation:** Formal benchmarks for AI performance (Sensitivity, Specificity, Fairness across languages/genders).

## 4. Non-Functional Requirements

- **Graceful Failure:** Must continue functioning in "Human Assessment Mode" if AI services are down.
- **Security:** Audit trails for all actions; data minimization; raw audio not retained by default.
- **Performance:** Real-time transcription and analysis capability.
