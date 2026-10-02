# Known Issues and Risks

## Issue 1: Lack of Validated Clinical Datasets

- **Severity:** High
- **Context:** Feature 2.18/2.20 requires evaluation metrics (AUROC, Calibration).
- **Problem:** No validated NHAA Trauma-Safety Dataset currently exists to test the model against ground truth.
- **Impact:** Risk of misclassifying trauma indicators or missing safety threats during initial deployment.
- **Status:** Planned (Feature 2.18).

## Issue 2: Multilingual and Dialect Accuracy

- **Severity:** Medium
- **Context:** Code-switching and Indian dialects (Feature 2.8).
- **Problem:** ASR accuracy may degrade significantly with code-switching (e.g., Marathi/Hindi mix) or regional dialects (Bengali, Tamil).
- **Impact:** Distress indicators or coercion signals might be missed if the transcript is garbled.
- **Status:** Research Gap (Feature 2.8).

## Issue 3: "Long Pause" Heuristic Interpretation

- **Severity:** Low-Medium
- **Context:** Feature 2.11.
- **Problem:** Original system identifies long pauses as trauma. Feature 2.11 warns this is unreliable.
- **Risk:** False positives where a speaker is simply reflecting or network delay is occurring.
- **Mitigation:** Implementation of context-aware filters (e.g., check network latency, intervening text) is required.

## Issue 4: Safety on Unsafe Devices

- **Severity:** Critical
- **Context:** Feature 2.23.
- **Problem:** If the victim's phone is near a perpetrator, standard notifications or UI cues can be dangerous.
- **Risk:** Retaliation if the perpetrator sees an app icon or notification.
- **Status:** Design consideration; implementation details pending.

## Issue 5: AI Generative Fallback Reliability

- **Severity:** Medium
- **Context:** Feature 1.9.
- **Problem:** Deterministic/extractive fallback may fail to capture complex nuances of trauma narratives if generative AI fails.
- **Impact:** Summary may be disjointed.
- **Status:** Standard resilience protocol required.
