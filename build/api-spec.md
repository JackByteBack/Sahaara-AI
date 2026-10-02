# API Specifications & JSON Schemas

## 1. WebSocket Message Structure

**Endpoint:** `ws://localhost:8000/api/v1/stream/{case_id}`

### Message Types

- **Client -> Server:**
  - `{ "type": "audio_chunk", "data": "base64_string" }`
  - `{ "type": "typing", "is_typed": boolean }`

- **Server -> Client:**
  - `{ "type": "transcript", "text": "Hello", "timestamp": 12.5 }`
  - `{ "type": "ai_flag", "category": "distress", "confidence": 0.8, "text": "I feel sad" }`
  - `{ "type": "status_update", "priority": 0.9, "mode": "review" }`

## 2. POST /api/v1/cases/start Request

```json
{
  "operator_id": "550e8400-e29b-41d4-a716-446655440000",
  "initial_language": "en"
}
```
