# Testing Plan

## Unit Tests

- **Backend:** Test `calculate_final_priority` function with dummy inputs to ensure Safety Override works.
- **Frontend:** Test `useLiveAnalysis` hook to ensure it disconnects properly on unmount.

## Integration Tests

- **End-to-End Flow:**
  1.  Start session -> Create Case.
  2.  Send Audio -> Verify Transcript appears in DB.
  3.  Verify AI Flag appears in DB.
  4.  Review Case -> Verify Status changes to "Closed".

## User Acceptance Tests (Manual)

- **Scenario A (Normal Distress):** Operator enters "I am sad." -> System flags "Distress: Low" -> Operator dismisses. Verify No alert logged.
- **Scenario B (Safety Override):** Operator sends audio of shouting "He is hitting me" -> System flags "Danger: High" -> Operator cannot dismiss easily -> Operator escalates.
- **Scenario C (Multilingual):** Operator speaks Marathi -> Verify Transcript is in Marathi and not broken English.
