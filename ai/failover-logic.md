---

#### `ai/failover-logic.md`

````markdown
# AI Failure Handling & Graceful Fallback (Feature 1.14)

## Architecture

The application has two pipelines:

1.  **Primary Pipeline:** Generative AI (High quality, slower, expensive).
2.  **Fallback Pipeline:** Rule-Based Engine (Fast, free, less nuanced).

## Code Logic (Python)

```python
def analyze_transcript(transcript_text, context):
    # 1. Try Primary (LLM)
    try:
        response = call_openai_api(transcript_text, context)
        return response
    except APIError as e:
        print(f"[LOG] AI Provider Error: {e}. Switching to Fallback.")

    # 2. Execute Fallback (Rule-Based)
    return run_rule_based_engine(transcript_text)

def run_rule_based_engine(text):
    """
    Performs simple keyword matching for safety features.
    """
    low_confidence_flags = []

    # Check for immediate danger keywords
    danger_words = ["gun", "knife", "stop", "help me", "hurt"]
    found_danger = [word for word in danger_words if word in text.lower()]

    if found_danger:
        low_confidence_flags.append({
            "type": "immediate_danger",
            "description": "Keyword match detected",
            "confidence": 0.4, # Low confidence because it's heuristic
            "source": "rule_based_fallback"
        })

    return {
        "flags": low_confidence_flags,
        "is_fallback": True # Flag to frontend for transparency
    }
```
````
