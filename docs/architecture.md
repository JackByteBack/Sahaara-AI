# System Architecture

## High-Level Overview

Sahaara AI follows a modular architecture designed to separate core business logic from AI inference pipelines.

## Components

### 1. Frontend Interface

- **Role:** Operator & Reviewer Portal.
- **Tech:** Web-based (Vanilla JS/React) supporting Voice and Text modes.
- **Features:** Live audio capture, real-time transcript display, AI flag dashboard, case management forms.

### 2. Backend API

- **Role:** Orchestrator.
- **Tech:** Node.js or Python.
- **Responsibilities:**
  - Authentication (RBAC).
  - Case CRUD operations.
  - Request routing to AI Services.
  - Orchestrating the Summary generation (GenAI + Extractive fallback).

### 3. AI Inference Pipeline

- **Feature 1.9 (Summary):** Integrated LLM with a fallback rule-based summarizer.
- **Feature 1.1 (Distress):** Rule-based engine for immediate observable indicators.
- **Feature 2.1 (Vulnerability):** Multimodal analysis model.
- **Feature 2.9 (Code-Switching):** Language detection module (pre-processor).

### 4. Data Store

- **Case Data:** Transcripts, flags, notes, metadata.
- **User Data:** Role-based access control.

## Data Flow

1.  **Input:** Operator starts session -> Consent captured.
2.  **Capture:** Audio stream sent to ASR -> Text transcript generated.
3.  **Analysis:** Transcript sent to AI Models.
    - Models return Flags (Distress, Safety, Trauma).
    - Models return Scores (Priority, Vulnerability).
4.  **Display:** Dashboard updates with evidence and confidence.
5.  **Action:** Operator validates, adds notes, or creates referral.
6.  **Persist:** Case and logs saved to Database.
