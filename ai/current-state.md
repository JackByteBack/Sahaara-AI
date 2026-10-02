# Current State Documentation

## Project Purpose

Sahaara AI is an AI-assisted decision support and case management platform for helpline operators, designed to assess distress and route victims to appropriate support services. It currently serves as a foundation for NHAA (National Human Rights Authority) research into AI-assisted victim vulnerability assessment.

## Technology Stack (Inferred from Requirements)

- **Frontend:** Voice and Text-based interaction interface (Web or Mobile application).
- **Backend:** API server handling voice capture, transcript processing, and case management logic.
- **AI Services:** LLMs (Generative) and Rule-based engines (Deterministic/Extractive) for analysis.
- **ASR:** Speech-to-Text engine for real-time conversion.
- **Database:** Relational or Document store for storing cases, transcripts, and user roles.

## Architecture

- **Input:** Live voice (audio), Simulated voice, Typed text.
- **Processing:**
  1.  Capture/Transcribe.
  2.  Language Detection (En/Hin/Marathi + Dialects).
  3.  Feature Extraction (Distress, Trauma, Safety, Coercion).
  4.  Scoring (Review Priority vs. Victim Safety Profile).
- **Output:** AI Flags, Summaries, Referral Suggestions.
- **Review:** Human Operator validates or modifies AI findings.

## Core Features Status

- **1.1 - 1.15:** Defined and structured as "Original Requirements". These are considered the base implementation set.
- **1.6 (Human-in-the-loop):** Defined as a strict constraint (must be implemented).
- **2.1 - 2.24:** Defined as "Research Enhancements". While capabilities are defined, the full implementation depth (e.g., Dataset creation, Longitudinal monitoring hooks) is considered "Future Work" or "Research Phase".

## Data Flow

1.  User enters helpline session.
2.  Consent is obtained.
3.  Audio is captured (or text typed).
4.  Transcription and AI analysis occur (generative + extractive).
5.  Flags and Summaries displayed.
6.  Human operator reviews and makes final decision.
7.  Case saved to database with audit logs.

## Limitations

- **Validation:** Currently lacks real-world validation datasets (synthetic/demo data used).
- **Languages:** Currently supports English, Hindi, Marathi. Research suggests expansion to other Indian languages.
- **Privacy:** No retention of raw audio in default mode; relies on anonymization.
