# Operational Rules

## General Guidelines

1.  **AI as Support:** AI tools are advisory only. The human operator is the final arbiter of decision-making.
2.  **No Diagnosis:** The system cannot diagnose clinical conditions. It identifies _indicators_ that suggest distress or risk.
3.  **Privacy First:** Do not share data outside of the secured Sahaara environment.

## Review Priorities

1.  **Standard:** Cases are routed by the `Review Priority Score`.
2.  **Safety Override:** If the `Safety Override Engine` flags an indicator (Feature 2.5), it must be pushed to the top of the queue regardless of the score.
3.  **Coercion:** If `Possible Coercion` is flagged (Feature 2.12), the case is treated as high-priority and requires immediate human review.

## Data Handling

1.  **Anonymization:** Once a case is closed or in the "Privacy Mode" (Feature 1.10), raw identifiers are removed.
2.  **Retention:** Audit logs are retained for compliance, but raw audio is deleted after processing unless explicitly requested for rare legal cases.

## Multilingual Protocols

1.  **Code-Switching:** Do not flag speech pausing as "silence" if a language switch occurs in the middle of a sentence.
2.  **Interpreter Mode:** If the operator does not speak the detected language, the system should prioritize English interpretation or immediate operator dispatch.
