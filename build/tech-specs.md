# Technical Specifications & Implementation Blueprint

## 1. Technology Stack Recommendation

- **Backend:** Python 3.10+ with FastAPI (Excellent for AI integrations and Async/IO).
- **Frontend:** React.js or Vue.js (Vanilla JS works for simple MVP).
- **Database:** PostgreSQL (Supports JSONB for complex flags and profiles).
- **Real-time Communication:** WebSocket (Socket.IO) for live transcription streaming.

## 2. Database Schema (PostgreSQL)

### Table: `users`

- `id` (UUID, PK)
- `username`
- `role` (enum: 'admin', 'operator', 'supervisor', 'counsellor')
- `password_hash`
- `created_at`

### Table: `cases`

- `id` (UUID, PK)
- `case_number` (String, unique)
- `status` (enum: 'active', 'reviewing', 'closed', 'referred')
- `created_by` (FK -> users.id)
- `priority_score` (Float) - _Derived from 1.4_
- `victim_safety_profile` (JSONB) - _Derived from 2.2_
  - `psych_distress`: {level, confidence}
  - `immediate_danger`: {value, reasoning}
  - `self_harm`: {value, reasoning}
- `ai_flags` (JSONB) - _Feature 1.5_
  - `distress_detected`: {value, evidence, confidence}
  - `coercion_indicated`: {value, evidence, confidence}
- `transcript` (Text)
- `final_decision` (JSONB) - _Feature 1.6 (Operator Action)_
- `created_at`
- `updated_at`

### Table: `audit_logs`

- `id` (UUID, PK)
- `case_id` (FK -> cases.id)
- `user_id` (FK -> users.id)
- `action` (enum: 'created', 'reviewed', 'escalated', 'flag_modified')
- `details` (Text)
- `timestamp`

## 3. API Endpoints Specification

### 3.1 Session Management

**POST** `/api/v1/cases/start`

- **Body:** `{ "initial_language": "en" }`
- **Response:** `{ "case_id": "uuid", "case_number": "SAH-2023-001", "token": "jwt_token" }`

### 3.2 Real-time Analysis (The Core)

**WS** `/api/v1/cases/{case_id}/stream`

- **Client sends:** Audio chunks.
- **Server responds (Stream):**
  1.  **Transcript:** `{ "type": "transcript", "text": "I am feeling scared.", "timestamp": 10.5 }`
  2.  **AI Flag (Pushed):** `{ "type": "flag", "category": "distress", "confidence": 0.85, "excerpt": "I am feeling scared" }`
  3.  **Safety Profile Update:** `{ "type": "profile_update", "immediate_danger": "high" }`

### 3.3 Human Review

**POST** `/api/v1/cases/{case_id}/review`

- **Body:** `{ "decision": "escalate", "override_ai": false, "notes": "Victim is in immediate physical danger." }`

## 4. Code Logic: Safety Override Engine (Feature 2.5)

```python
def calculate_final_priority(base_score, ai_flags):
    # 1. Base Score from AI (Feature 1.4)
    priority = base_score

    # 2. Check for Safety Overrides (Feature 2.5)
    safety_override_threshold = 0.9

    if ai_flags.get('immediate_danger') == 'HIGH':
        priority = 1.0 # Force Critical Priority
        print(f"[SAFETY OVERRIDE] Immediate danger detected. Priority set to Critical.")
    elif ai_flags.get('immediate_danger') == 'MEDIUM':
        priority = 0.8 # Force High Priority
    else:
        priority = priority # Default to AI calculation

    return priority
```
