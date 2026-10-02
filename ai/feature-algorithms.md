---

#### `ai/feature-algorithms.md`

````markdown
# Feature: Review Priority Calculation (Feature 1.4 & 2.3)

## The Weighted Formula

The `Review Priority Score` is not just AI confidence; it's a heuristic weighted by context.

```python
def calculate_review_priority(case):
    score = 0.0

    # 1. Linguistic Indicators (20% weight)
    # Count negative sentiment words in transcript
    negative_words = ["sad", "scared", "hate", "abuse"]
    score += len([w for w in case.transcript.split() if w.lower() in negative_words]) * 0.05

    # 2. Contextual Indicators (30% weight)
    # Length of conversation (longer = more detail)
    score += len(case.transcript) / 1000 * 0.1

    # 3. Conversation Indicators (30% weight)
    # Number of AI flags detected
    if len(case.ai_flags) > 0:
        score += min(len(case.ai_flags) * 0.1, 0.5)

    # 4. Safety Override (Feature 2.5)
    # MUST override the score
    if case.victim_safety_profile.get('immediate_danger') == 'HIGH':
        return 1.0 # Critical

    # Clamp score between 0.0 and 1.0
    return round(min(max(score, 0.0), 1.0), 2)
```
````
