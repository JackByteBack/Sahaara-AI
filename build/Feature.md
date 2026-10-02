The Extractive Fallback (Feature 1.9)

When Generative AI fails (network error), use a simpler Python rule.

def generate_extractive_summary(transcript_text, danger_keywords):
sentences = transcript_text.split('. ')
flagged_sentences = []

    for sent in sentences:
        if any(word in sent.lower() for word in danger_keywords):
            flagged_sentences.append(sent.strip())

    if not flagged_sentences:
        return "No immediate distress indicators detected in transcript."

    return f"Extracted Summary:\n" + "\n".join(flagged_sentences)

2. Code-Switching Detection Algorithm (Feature 2.9)

Implementing this requires comparing text segments against language probability models.

from langdetect import detect, LangDetectException
def analyze_code_switching(transcript_segments):
"""
transcript_segments: List of {text: "...", timestamp: "..."}
"""
switch_detected = False
segments_info = []

    for i in range(len(transcript_segments) - 1):
        curr = transcript_segments[i]
        next_seg = transcript_segments[i+1]

        try:
            lang1 = detect(curr['text'])
            lang2 = detect(next_seg['text'])
        except LangDetectException:
            continue
        if lang1 != lang2:
            switch_detected = True
            segments_info.append({
                "from": curr['timestamp'],
                "to": next_seg['timestamp'],
                "language_1": lang1,
                "language_2": lang2
            })

    return switch_detected, segments_info

3. Real-Time Feature Extraction (Feature 2.4)

Instead of waiting for the whole transcript, analyze chunks (e.g., every 5 seconds).

def analyze_audio_chunk(audio_chunk, safety_keywords): # 1. Transcribe chunk
transcript = transcribe(audio_chunk)

    # 2. Check Volume (VAD)
    volume = calculate_volume(audio_chunk)
    is_shouting = volume > 85  # Threshold
    # 3. Check Content
    detected_threat = any(word in transcript for word in safety_keywords)
    # 4. Decision
    if is_shouting and detected_threat:
        return {
            "type": "CRITICAL_SAFETY",
            "message": "Potential immediate threat detected.",
            "suggestion": "Override Priority"
        }
    return None

---

### **build/security-hardening.md**

````markdown
# Security & Safe Exit Implementation (Feature 2.23)

## 1. The "Safe Exit" (Privacy Mode) Logic

Victims in dangerous situations may need to exit the app quickly without leaving obvious trace.

### Frontend Implementation

Add a global keyboard listener and a "Hidden Button" in the corner.

````javascript
// In React App
useEffect(() => {
  const handleKeyPress = (e) => {
    // Rule: Press 'Escape' twice rapidly within 2 seconds
    if (e.key === 'Escape') {
      const now = Date.now();

      if (!window.exitTimer) window.exitTimer = now;
      if (now - window.exitTimer < 2000) {
        // Safe Exit Triggered
        triggerSafeExit();
      }
      window.exitTimer = now;
    }
  };
  window.addEventListener('keydown', handleKeyPress);
  return () => window.removeEventListener('keydown', handleKeyPress);
}, []);
The triggerSafeExit Function

Hide UI: document.body.style.display = 'none' or cover with black div.
Kill WebSockets: Close all connections.
Stop Audio: Mute all audio elements.
Notification: Hide OS notifications (browser API). Note: Cannot fully block OS notifications, but can hide the app window if possible.
2. No Local Storage of Sensitive Data

When a case is closed, scrub the local browser cache.


const closeCase = async (caseId) => {
  // 1. Call Backend to delete sensitive data
  await axios.post(`/api/v1/cases/${caseId}/anonymize`);

  // 2. Clear Local Storage
  localStorage.clear();
  sessionStorage.clear();

  // 3. Reset UI
  window.location.reload();
};
3. API Rate Limiting

Prevent DoS attacks on the helpline infrastructure.


from fastapi import FastAPI, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
@app.post("/api/v1/cases/start")
@limiter.limit("5/minute") # Max 5 sessions per minute per IP
async def start_case(request: Request):
    # ...

---
### **build/frontend-ux-specs.md**
```markdown
# Frontend UX & Interaction Design
## 1. The "Safety Dashboard" (Visual Priority)
When the AI detects `Safety Override` (Feature 2.5), the UI must change instantly.
### State: NORMAL
*   Colors: White background, standard text.
*   Flags: Small yellow/orange badges appearing on the transcript.
### State: SAFETY OVERRIDE
*   **Animation:** The screen flashes Red for 300ms.
*   **Button Behavior:**
    *   "Escalate" button: Glows bright Red, takes 50% more click area.
    *   "Dismiss" button: Disabled or hidden.
*   **Autoplay Audio:** Automatically play a "Safe Exit" audio file (e.g., "I am here to help, stay on the line") to reassure the victim while the operator is notified.
## 2. Trauma-Informed Question Interface (Feature 2.13)
Restrict the number of open questions.
### Logic
If `Trauma Mode` is ON:
1.  **Auto-Advance:** Disable the "Next Question" button until the user has paused speaking for 3 seconds (calculated via `userSpeaking` state).
2.  **Soft Questions:** If the next standard question is "Why did that happen?", replace it with "What was the situation like?".
### Code Snippet
```javascript
const TraumaSafeQuestion = () => {
  const [userPaused, setUserPaused] = useState(false);

  // Check silence duration
  useEffect(() => {
    const interval = setInterval(() => {
      if (transcriptText.length > 0 && lastTranscriptTime) {
        const silence = (Date.now() - lastTranscriptTime) / 1000;
        if (silence > 2) setUserPaused(true);
      }
    }, 1000);
  }, [transcriptText, lastTranscriptTime]);
  return (
    <div>
      <button disabled={!userPaused && traumaMode}>
        Next Question
      </button>
      <p style={{color: userPaused ? 'green' : 'grey'}}>
        {userPaused ? 'Ready to proceed' : 'Please wait for a pause...'}
      </p>
    </div>
  );
};
3. Notification Handling

Only notify the operator if it is safe to notify.

Conditional Notification Logic


const showNotification = (alert) => {
  // Don't show notification if operator is 'typing' or 'reading' a previous flag
  if (isOperatorBusy) return;
  // Don't show if 'Safe Exit' was pressed
  if (isSafeExitMode) return;
  new Notification("Sahaara Alert", {
    body: alert.message,
    icon: "/bell-icon.png"
  });
};

---
### **build/data-management-logic.md**
```markdown
# Data Management & Anonymization
## 1. Case Lifecycle Workflow (Feature 1.7)
1.  **Creation:**
    *   Admin/Operator sets `status: 'active'`.
    *   System generates `case_id`.
2.  **Analysis:**
    *   AI pipelines run.
    *   `priority_score` updates.
    *   `victim_safety_profile` updates.
3.  **Review (The Critical Step):**
    *   Operator opens case.
    *   User must click "Confirm Analysis" (adds audit log entry).
    *   If operator changes a score, log the diff.
4.  **Referral (Feature 1.8):**
    *   If `status` changes to 'referred':
    *   System creates a "Referral Ticket" in the database (e.g., linked to Police, NGO, or Medical provider).
5.  **Closure:**
    *   `status: 'closed'`.
    *   Trigger `anonymize_data()` function.
## 2. Anonymization Logic (Feature 1.10)
Before closing, replace sensitive PII in the transcript.
```python
def anonymize_transcript(transcript, case_data):
    """
    Replaces names with placeholders.
    """
    name = case_data.get('victim_name', 'Unknown')

    # Simple Regex replacement
    # WARNING: In production, use a robust Named Entity Recognition (NER) model
    # to ensure you don't anonymize addresses (e.g., "123 Main St" -> "123 [Address]")

    replaced_text = transcript.replace(name, "[Name Anonymized]")

    # Add note
    log_action("case_anonymized", f"Replaced '{name}' with placeholder.")

    return replaced_text
3. Role-Based Data Access (Feature 1.11)

RBAC Middleware (Python/FastAPI)


from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = verify_jwt(credentials.credentials)
    return user
def check_permission(required_role):
    def wrapper(current_user):
        if current_user['role'] not in required_role:
            raise HTTPException(status_code=403, detail="Permission Denied")
        return current_user
    return wrapper
# Usage
@app.get("/api/v1/cases/{case_id}")
@check_permission(["operator", "supervisor", "admin"])
async def get_case(case_id: str, current_user = Depends(get_current_user)):
    return get_case_from_db(case_id)

### **build/deployment-guide.md**
```markdown
# Deployment Instructions
## 1. Environment Setup
*   **Docker Compose:** Create `docker-compose.yml`.
*   **Services:**
    *   `postgres`: Database.
    *   `backend`: FastAPI app.
    *   `frontend`: Nginx serving React build.
## 2. Nginx Configuration (Reverse Proxy)
Protect the `/api` endpoints.
```nginx
server {
    listen 80;
    server_name sahaara-ai.local;
    # Frontend
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    # API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
3. Caching Strategy

Cache the "Safe Exit" screen and static assets aggressively.
Cache victim_safety_profile responses for 30 seconds to save API calls during live conversation bursts.
4. Monitoring

Health Check: /health endpoint to ensure database is connected.
Log Aggregation: Send FastAPI logs to ELK stack or CloudWatch for Feature 2.24 (Research Monitoring).
````
````
