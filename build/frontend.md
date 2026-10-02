5. Frontend Component Architecture

AudioRecorder: Uses Web Audio API to capture input and send chunks via WebSocket.
LiveTranscript: Updates DOM with text as it arrives from WS.
FlagOverlay: Visual indicators (Red/Yellow/Green) appearing next to the transcript as flags are detected.
CaseManager: Form to edit VictimSafetyProfile, add Notes, and perform Escalation

---

#### `build/setup-guide.md`

````markdown
# Setup Guide: How to Run Sahaara AI

## Prerequisites

- Node.js (v18+)
- Python (v3.10+)
- PostgreSQL (v14+)
- Docker (Optional, for local dev database)

## Step 1: Directory Structure

Create the following folders:

```text
sahaara-ai/
├── backend/          # Python/FastAPI
├── frontend/         # React/Vue
├── database/         # SQL Scripts
├── docs/             # Existing docs
└── build/            # Existing build docs
```
````

Step 2: Backend Setup (Python/FastAPI)

Install dependencies:

cd backend
pip install fastapi uvicorn python-multipart sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] websockets openai
Configure .env:

DATABASE_URL=postgresql://user:password@localhost:5432/sahaara
SECRET_KEY=your_super_secret_key_here
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
Initialize DB:
Run the SQL schema from build/tech-specs.md inside your PostgreSQL client (e.g., pgAdmin or DBeaver).
Run Server:
uvicorn main:app --reload

Step 3: Frontend Setup (React)

Install dependencies:

cd frontend
npm create vite@latest . -- --template react
npm install axios socket.io-client react-live-clock
API Service:
Create src/services/api.js:

import axios from 'axios';
const API_URL = 'http://localhost:8000/api/v1';
export const startCase = async () => {
const res = await axios.post(`${API_URL}/cases/start`);
return res.data;
};
WebSocket Connection:
Create src/hooks/useLiveAnalysis.js:

import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';
export const useLiveAnalysis = (caseId) => {
const [flags, setFlags] = useState([]);
useEffect(() => {
const socket = io('ws://localhost:8000/api/v1/cases/' + caseId + '/stream');

    socket.on('flag', (data) => {
      setFlags(prev => [...prev, data]);
    });
    return () => socket.disconnect();

}, [caseId]);
return flags;
};
Step 4: Running the Project

Start PostgreSQL.
Start Backend: python backend/main.py
Start Frontend: npm run dev (in frontend folder)
Open http://localhost:5173 (or port specified in vite).

---

#### `build/implementation-logic.md`

```markdown
# Detailed Logic Flow for Key Features

## Feature 1.3: Multilingual Support Logic

**Implementation Steps:**

1.  **ASR (Speech-to-Text):** Use OpenAI Whisper API or Google Cloud Speech-to-Text.
    - _Input:_ Audio Buffer.
    - _Processing:_ Send to API.
    - _Output:_ `transcript_text`, `language_code`, `confidence`.
2.  **Second Pass (Validation):** Pass the transcript text to a Language Detection model (e.g., fasttext or HuggingFace `langdetect`).
3.  **Code-Switching Logic (Feature 2.9):**
    - If the ASR output contains a mix of Hindi (hi) and English (en) in close proximity, set `is_code_switched = true`.
    - _Display:_ Show the transcript split by sentences, tagging the language of each sentence.

## Feature 2.4: Immediate Safety Assessment

**Implementation Steps:**

1.  **Keyword/Metric Filtering:**
    - Create a keyword list for "Immediate Danger": "threaten", "gun", "knife", "hurt me now", "alive".
2.  **Tone Analysis:**
    - Use VAD (Voice Activity Detection) to identify spikes in volume or shouting.
3.  **Alert Logic:**
    - If (Keywords Found OR Volume Spike > Threshold) AND (User hasn't interrupted) THEN -> Trigger Safety Override.
    - _UI Action:_ Flash screen RED. Disable "Dismiss" button.

## Feature 2.13: Trauma-Informed Conversation Mode

**Implementation Steps (Frontend):**

1.  **UI Toggle:** A switch in the session controls: "Trauma-Informed Mode: ON".
2.  **Logic:**
    - **Do Not Ask "Why?":** Filter out questions starting with "Why".
    - **Reassurance:** Add a pre-defined "Reassurance" button: _"It's not your fault. You are safe here."_
    - **Question pacing:** If the user speaks, disable the "Next Question" auto-trigger to give them time.
3.  **Backend:** Send a `context_param` with every query: `{ "trauma_mode": true }` to the AI provider.

## Feature 1.9: AI-Generated Summaries (Fallback)

**Implementation Steps:**

1.  **Primary:** Call OpenAI API with prompt: "Summarize this transcript focusing on distress and needs."
2.  **Fallback (Failure Mode):**
    - If OpenAI fails (timeout/limit) OR return error:
    - Extract key sentences where "distress" or "danger" keywords appear.
    - Generate a "Extractive Summary": List the sentences: "1. Victim feels unsafe. 2. Suspect is present."
3.  **Storage:** Store both in DB under `summary_primary` and `summary
```
