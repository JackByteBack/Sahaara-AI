# Risk Assessment & Mitigation

## Risk 1: AI Hallucination

- **Description:** The AI invents facts about the victim or situation.
- **Probability:** Medium.
- **Impact:** High (Misleading operator).
- **Mitigation:**
  - Always display "AI Confidence Score".
  - Require "Human Confirmation" for any Referral or Escalation.
  - Use Strict Output Schema (JSON validation).

## Risk 2: Bias in Vulnerability Assessment

- **Description:** The model performs poorly on non-English or specific dialects (Feature 2.8).
- **Probability:** High.
- **Impact:** Medium (Missed victims).
- **Mitigation:**
  - Use diverse training data.
  - Log performance per language.
  - Implement Feature 2.24 (Continuous Monitoring).

## Risk 3: Data Leakage (Safe Exit Mode Failure)

- **Description:** The "Safe Exit" leaves data in clipboard or browser cache.
- **Probability:** Low.
- **Impact:** Critical (Victim safety risk).
- **Mitigation:**
  - Overwrite clipboard on exit.
  - Hard delete from IndexedDB on exit.
  - Encrypt local cache storage.
