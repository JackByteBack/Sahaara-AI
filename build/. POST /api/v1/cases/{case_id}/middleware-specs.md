---

#### `build/middleware-specs.md`

````markdown
# Middleware Implementation Details

## 1. Operator Validation Middleware

Checks if the user is actually logged in and allowed to view the case.

```python
from fastapi import HTTPException, status

async def validate_operator(request, call_next):
    user_id = request.headers.get("x-user-id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Missing User Token")

    # Check DB for user existence
    user_exists = db.query(User).filter(User.id == user_id).first()

    if not user_exists:
        raise HTTPException(status_code=403, detail="User not authorized")

    request.state.user = user_exists
    response = await call_next(request)
    return response
```
````

2. Safety Message Queue

Ensures high-priority flags don't get buried.

class SafetyQueue:
def **init**(self):
self.queue = []

    def add_alert(self, alert_data):
        # Safety alerts have a higher priority than regular logs
        self.queue.insert(0, alert_data)

    def get_alert(self):
        return self.queue.pop(0) if self.queue else None

# Usage in API

@app.post("/api/v1/stream")
async def stream_audio(request: Request):
safety_queue = SafetyQueue()

    # ... inside audio processing loop ...

    if detection == "CRITICAL_DANGER":
        safety_queue.add_alert({"priority": "CRITICAL", "msg": "Immediate Threat Detected"})

    # Continuously poll the queue to send websocket events
    while True:
        alert = safety_queue.get_alert()
        if alert:
            await websocket.send_json(alert)
