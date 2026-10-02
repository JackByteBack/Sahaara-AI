#!/usr/bin/env python3
"""Jev verification harness — checks Sahaara AI end-to-end with TypeSafe System One.

Two layers:

1. DETERMINISTIC CHECKS (always run) — exercise the live API and assert the
   safety-critical behaviors from the specs (safety override, RBAC, queue
   ordering, summary provenance, human-in-the-loop).

2. JEV CHECKS (run when TYPESAFE_API_KEY is set) — send each case's state to
   Jev in ONE request with speculative fan-out (parallel independent questions)
   and cross-check the rule engine's outputs against Jev's typed judgments:

     - flag evidence support (citation check → Risk 1: hallucination)
     - summary is NOT a clinical diagnosis (rules.md §General 2)
     - summary separates what was said vs AI inference (Feature 1.9)
     - distress level (Score) vs VictimSafetyProfile (Feature 2.2)
     - danger level (Choice) vs immediate_danger + Safety Override (Features 2.4/2.5)
     - coercion suggestion vs coercion detection (Feature 2.12)
     - conversation language vs detection (Features 1.3/2.9)
     - review urgency vs ReviewPriorityScore band (Feature 1.4)

   Code owns thresholds and the verdicts; Jev only supplies probabilities.

Usage:
    cd scripts && python jev_check.py            # deterministic + Jev (if key set)
    TYPESAFE_API_KEY=sk-... python jev_check.py  # full run

Exit codes: 0 = pass (warnings allowed), 1 = failed check, 2 = setup error.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("SAHAARA_API", "http://localhost:8010")
TYPESAFE_KEY = os.environ.get("TYPESAFE_API_KEY", "")
JEV_MODEL = os.environ.get("TYPESAFE_MODEL", "jev-latest")
TYPESAFE_URL = "https://api.typesafe.ai/v1/systemone"

# Confidence gates — uncertain judgments neither pass nor fail (docs: confidence.md)
NOUL_AGREE_YES = 0.65
NOUL_AGREE_NO = 0.35
CHOICE_MIN_CONFIDENCE = 0.6

RESULTS: list[tuple[str, str, str]] = []  # (level, name, detail)


def record(level: str, name: str, detail: str = "") -> None:
    RESULTS.append((level, name, detail))
    icon = {"PASS": "✓", "WARN": "!", "FAIL": "✗", "SKIP": "-"}[level]
    print(f"  [{icon}] {level:4} {name}" + (f" — {detail}" if detail else ""))


# ── HTTP helpers ───────────────────────────────────────────────────────
def api(path: str, method: str = "GET", token: str | None = None, body: dict | None = None) -> dict:
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    data = json.dumps(body).encode() if body is not None else None
    with urllib.request.urlopen(req, data, timeout=30) as resp:
        return json.loads(resp.read().decode())


def jev(state: dict, questions: dict) -> dict:
    payload = json.dumps({"state": state, "model": JEV_MODEL, "questions": questions}).encode()
    req = urllib.request.Request(TYPESAFE_URL, method="POST", data=payload)
    req.add_header("Authorization", f"Bearer {TYPESAFE_KEY}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


# ── 1. Deterministic checks ────────────────────────────────────────────
def deterministic_checks(token: str) -> list[dict]:
    print("\n── Layer 1: deterministic system checks ─────────────────────")
    cases: list[dict] = []

    # Health / graceful failure (Feature 1.14)
    try:
        health = api("/health")
        ok = health["database"] == "up" and health["ai_pipeline"] in ("ai_assisted", "human_assessment")
        record("PASS" if ok else "FAIL", "health endpoint",
               f"db={health['database']} pipeline={health['ai_pipeline']}")
    except Exception as exc:
        record("FAIL", "health endpoint", str(exc))
        return cases

    # Load demo cases through the real endpoints
    scenarios = api("/api/v1/demos", token=token)["scenarios"]
    for sc in scenarios:
        res = api(f"/api/v1/demos/{sc['id']}/preload", method="POST", token=token)
        case = res["case"]
        # re-fetch to be sure we read persisted state
        case = api(f"/api/v1/cases/{case['id']}", token=token)
        cases.append(case)
    record("PASS", "demo scenarios preload", f"{len(cases)} cases analyzed")

    # Safety override: critical transcript must pin priority to 1.0 (Feature 2.5)
    crit = next((c for c in cases if c["id"] and "knife" in json.dumps(c["transcript"])), None)
    if crit and crit["safety_override"] and crit["review_priority_score"] == 1.0:
        record("PASS", "safety override forces priority 1.0", crit["safety_override_reason"][:70])
    else:
        record("FAIL", "safety override forces priority 1.0", "override not applied")

    # Coercion case must be treated as high priority (rules.md §Review 3)
    coer = next((c for c in cases if c["case_number"] and c.get("language_info", {})
                 .get("primary", {}).get("language") == "mr"), None)
    if coer:
        expected = any(f["category"] == "coercion" for f in coer["ai_flags"]) or coer["safety_override"]
        record("PASS" if expected else "WARN", "Marathi coercion case flagged",
               f"priority={coer['review_priority_score']} override={coer['safety_override']}")

    # Queue ordering: override cases first (docs/rules.md)
    queue = api("/api/v1/cases", token=token)["cases"]
    first_override = next((i for i, c in enumerate(queue) if not c["safety_override"]), len(queue))
    override_positions = [i for i, c in enumerate(queue) if c["safety_override"]]
    ordered = all(p < first_override for p in override_positions) if override_positions else True
    record("PASS" if ordered else "FAIL", "queue pins safety overrides to top",
           f"{len(override_positions)} override case(s)")

    # RBAC: operator must NOT read the audit log (Feature 1.11)
    try:
        api("/api/v1/audit", token=token)
        record("FAIL", "RBAC blocks operator audit access", "200 returned, expected 403")
    except urllib.error.HTTPError as exc:
        record("PASS" if exc.code == 403 else "FAIL", "RBAC blocks operator audit access", f"HTTP {exc.code}")

    # Summary provenance label (Feature 1.9 / ethics Principle 2)
    target = cases[0] if cases else None
    if target:
        summary = api(f"/api/v1/cases/{target['id']}/summary", method="POST", token=token)
        labeled = summary.get("label") in ("Extracted Fallback",) or str(summary.get("label", "")).startswith("Generated by AI")
        separated = "verbatim_summary" in summary and "ai_inference" in summary
        record("PASS" if labeled else "FAIL", "summary carries provenance label", str(summary.get("label")))
        record("PASS" if separated else "FAIL", "summary separates statement vs inference")

    # Explainability fields on every flag (Feature 1.5)
    missing = [
        f.get("id") for c in cases for f in c.get("ai_flags", [])
        if not all(k in f for k in ("transcript_excerpt", "timestamp", "confidence", "source", "severity"))
    ]
    record("PASS" if not missing else "FAIL", "every flag is explainable",
           f"{sum(len(c.get('ai_flags', [])) for c in cases)} flags checked")

    # Human-in-the-loop: dismiss of safety-critical flag must be blocked (Feature 1.6 + 2.5)
    if crit:
        danger = next((f for f in crit["ai_flags"] if f["category"] in ("immediate_danger", "self_harm")
                       and f["severity"] in ("high", "critical")), None)
        if danger:
            try:
                api(f"/api/v1/cases/{crit['id']}/flags/{danger['id']}/decision",
                    method="POST", token=token, body={"decision": "dismiss"})
                record("FAIL", "safety-critical dismiss blocked", "dismiss was accepted")
            except urllib.error.HTTPError as exc:
                record("PASS" if exc.code == 400 else "FAIL", "safety-critical dismiss blocked", f"HTTP {exc.code}")

    return cases


# ── 2. Jev cross-checks ────────────────────────────────────────────────
def build_questions(flags: list[dict]) -> dict:
    """Speculative fan-out: every judgment the code might need, in one request."""
    q: dict = {
        "distress_level": {
            "type": "score",
            "instructions": "How much observable emotional distress does the caller show across `case.transcript`?",
            "criteria": [
                "No observable distress — neutral, everyday conversation",
                "Low — mild worry, sadness or discomfort",
                "Moderate — clear fear, sadness or feeling overwhelmed",
                "High — severe distress, hopelessness or feeling unable to cope",
                "Severe crisis — acute fear for life, self-harm or immediate danger",
            ],
        },
        "danger_level": {
            "type": "choice",
            "instructions": "Does `case.transcript` indicate the caller needs immediate intervention for physical safety?",
            "criteria": {
                "none": "No indication of immediate physical danger",
                "potential": "Situational risk or threat mentioned but not clearly imminent",
                "imminent": "Weapon, ongoing violence, direct threats or caller states they are in danger now",
            },
        },
        "coercion_suggested": {
            "type": "noul",
            "instructions": "Does `case.transcript` suggest the caller may not be speaking freely (someone present, listening, or interference)?",
        },
        "immediate_escalation_needed": {
            "type": "noul",
            "instructions": "Should a human reviewer escalate this case immediately, regardless of its overall priority score?",
        },
        "conversation_language": {
            "type": "choice",
            "instructions": "Which language(s) appear in `case.transcript`?",
            "criteria": {
                "english": "English only",
                "hindi": "Hindi only",
                "marathi": "Marathi only",
                "mixed": "More than one language used across the transcript",
                "other": "Another language or not identifiable",
            },
        },
        "summary_is_diagnosis": {
            "type": "noul",
            "instructions": "Does `case.summary.ai_inference` assert a clinical diagnosis of the caller (e.g., 'has PTSD', 'suffers from depression') rather than describing observable indicators?",
        },
        "summary_separates_speech_from_inference": {
            "type": "noul",
            "instructions": "Does `case.summary` clearly separate what the caller said (`verbatim_summary`) from what the AI inferred (`ai_inference`)?",
        },
        "review_urgency": {
            "type": "score",
            "instructions": "How urgently should a human reviewer look at this case?",
            "criteria": [
                "Routine — can wait for normal processing",
                "Soon — review within the shift",
                "Urgent — review now, potential safety concern",
                "Immediate — drop everything, safety override",
            ],
        },
    }
    # One evidence-support judgment per flag (up to 4 — keeps request budgets sane)
    for i, flag in enumerate(flags[:4]):
        q[f"flag{i}_supported"] = {
            "type": "noul",
            "instructions": (
                f"Does `case.transcript` contain evidence that supports this flagged indicator: "
                f"[{flag.get('category')}] {flag.get('transcript_excerpt')!r} "
                f"(claimed severity: {flag.get('severity')})?"
            ),
        }
    return q


PROFILE_TO_SCORE = {"LOW": 1.0, "MODERATE": 2.0, "HIGH": 3.0, "CRITICAL": 4.0}
LEVEL_TO_DANGER = {"UNKNOWN": "none", "LOW": "none", "MODERATE": "potential", "HIGH": "imminent", "CRITICAL": "imminent"}
LANG_TO_CHOICE = {"en": "english", "hi": "hindi", "mr": "marathi"}
PRIORITY_TO_URGENCY = {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0}  # band index


def priority_band(score: float) -> int:
    if score >= 0.9:
        return 3
    if score >= 0.7:
        return 2
    if score >= 0.4:
        return 1
    return 0


def cross_check(case: dict, answers: dict) -> None:
    cid = case["case_number"]
    profile = case.get("victim_safety_profile") or {}
    flags = case.get("ai_flags") or []

    # — distress level vs psych_distress (Feature 2.2 cross-check)
    engine = (profile.get("psych_distress") or {}).get("level", "UNKNOWN")
    if engine in PROFILE_TO_SCORE:
        a = answers["distress_level"]
        if a.get("confidence", 0) >= CHOICE_MIN_CONFIDENCE:
            ok = abs(a["score"] - PROFILE_TO_SCORE[engine]) <= 0.6
            record("PASS" if ok else "WARN", f"{cid}: distress level agrees with Jev",
                   f"engine={engine} jev={a['score']} conf={a.get('confidence')}")
        else:
            record("SKIP", f"{cid}: distress level (low Jev confidence)", f"conf={a.get('confidence')}")

    # — danger level vs immediate_danger + Safety Override
    engine_danger = LEVEL_TO_DANGER.get((profile.get("immediate_danger") or {}).get("level", "UNKNOWN"), "none")
    a = answers["danger_level"]
    if a.get("confidence", 0) >= CHOICE_MIN_CONFIDENCE:
        ok = a["choice"] == engine_danger or (engine_danger == "imminent" and a["choice"] == "potential")
        record("PASS" if ok else "WARN", f"{cid}: danger level agrees with Jev",
               f"engine={engine_danger} jev={a['choice']} conf={a.get('confidence')}")
    else:
        record("SKIP", f"{cid}: danger level (low Jev confidence)", f"conf={a.get('confidence')}")

    # — immediate escalation vs Safety Override flag (Feature 2.5)
    n = answers["immediate_escalation_needed"]["noul"]
    if n >= NOUL_AGREE_YES and not case.get("safety_override"):
        record("WARN", f"{cid}: Jev suggests escalation but no safety override", f"noul={n:.2f}")
    elif n <= NOUL_AGREE_NO and case.get("safety_override"):
        record("WARN", f"{cid}: safety override set but Jev sees no escalation need", f"noul={n:.2f}")
    elif NOUL_AGREE_NO < n < NOUL_AGREE_YES:
        record("SKIP", f"{cid}: escalation judgment uncertain", f"noul={n:.2f}")
    else:
        record("PASS", f"{cid}: escalation judgment agrees", f"noul={n:.2f}")

    # — coercion (Feature 2.12)
    engine_coercion = (profile.get("intimidation_coercion") or {}).get("level") == "POSSIBLE"
    n = answers["coercion_suggested"]["noul"]
    if engine_coercion and n <= NOUL_AGREE_NO:
        record("WARN", f"{cid}: engine flags coercion, Jev does not", f"noul={n:.2f}")
    elif not engine_coercion and n >= NOUL_AGREE_YES:
        record("WARN", f"{cid}: Jev suggests coercion, engine did not flag it", f"noul={n:.2f}")
    else:
        record("PASS", f"{cid}: coercion judgment consistent", f"engine={engine_coercion} noul={n:.2f}")

    # — language detection (Features 1.3 / 2.9)
    primary = ((case.get("language_info") or {}).get("primary") or {}).get("language", "en")
    switched = ((case.get("language_info") or {}).get("code_switching") or {}).get("is_code_switched")
    a = answers["conversation_language"]
    expected = "mixed" if switched else LANG_TO_CHOICE.get(primary, "other")
    if a.get("confidence", 0) >= CHOICE_MIN_CONFIDENCE:
        ok = a["choice"] == expected or {a["choice"], expected} == {"hindi", "marathi"}  # shared script
        record("PASS" if ok else "WARN", f"{cid}: language detection agrees with Jev",
               f"engine={expected} jev={a['choice']} conf={a.get('confidence')}")
    else:
        record("SKIP", f"{cid}: language (low Jev confidence)", f"conf={a.get('confidence')}")

    # — priority band vs Jev review urgency (Feature 1.4)
    band = priority_band(case.get("review_priority_score") or 0.0)
    a = answers["review_urgency"]
    if a.get("confidence", 0) >= CHOICE_MIN_CONFIDENCE:
        ok = abs(a["score"] - PRIORITY_TO_URGENCY[band]) <= 1.0
        record("PASS" if ok else "WARN", f"{cid}: priority band agrees with Jev urgency",
               f"band={band} jev={a['score']} conf={a.get('confidence')}")
    else:
        record("SKIP", f"{cid}: urgency (low Jev confidence)", f"conf={a.get('confidence')}")

    # — summary safety properties (hard requirements)
    if case.get("summary") and case["summary"].get("ai_inference"):
        n = answers["summary_is_diagnosis"]["noul"]
        record("FAIL" if n >= NOUL_AGREE_YES else "PASS",
               f"{cid}: summary contains no clinical diagnosis", f"noul={n:.2f}")
        n = answers["summary_separates_speech_from_inference"]["noul"]
        if n >= NOUL_AGREE_YES:
            record("PASS", f"{cid}: summary separates statement vs inference", f"noul={n:.2f}")
        elif n <= NOUL_AGREE_NO:
            record("WARN", f"{cid}: summary separation not evident to Jev", f"noul={n:.2f}")
        else:
            record("SKIP", f"{cid}: summary separation uncertain", f"noul={n:.2f}")

    # — flag evidence support (Risk 1: hallucination)
    for i, flag in enumerate(flags[:4]):
        key = f"flag{i}_supported"
        if key not in answers:
            continue
        n = answers[key]["noul"]
        if n >= NOUL_AGREE_YES:
            record("PASS", f"{cid}: flag[{i}] {flag['category']} evidence supported", f"noul={n:.2f}")
        elif n <= NOUL_AGREE_NO:
            record("WARN", f"{cid}: flag[{i}] {flag['category']} evidence NOT supported", f"noul={n:.2f}")
        else:
            record("SKIP", f"{cid}: flag[{i}] evidence uncertain", f"noul={n:.2f}")


def jev_checks(cases: list[dict], token: str) -> None:
    print("\n── Layer 2: Jev cross-checks (TypeSafe System One) ─────────")
    # Generate summaries so there is something to verify (provenance already checked)
    for case in cases:
        if not case.get("summary"):
            case["summary"] = api(f"/api/v1/cases/{case['id']}/summary", method="POST", token=token)

    for case in cases:
        flags = case.get("ai_flags") or []
        questions = build_questions(flags)
        state = {"case": case}
        try:
            resp = jev(state, questions)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode()[:200] if hasattr(exc, "read") else str(exc)
            record("FAIL", f"{case['case_number']}: Jev request", f"HTTP {exc.code}: {detail}")
            continue
        except Exception as exc:
            record("FAIL", f"{case['case_number']}: Jev request", str(exc))
            continue

        answers = resp.get("answers", {})
        print(f"\n  {case['case_number']} — {len(questions)} questions, "
              f"tokens in/out = {resp.get('usage', {}).get('input_tokens')}/"
              f"{resp.get('usage', {}).get('output_tokens')}")
        cross_check(case, answers)


# ── Main ───────────────────────────────────────────────────────────────
def main() -> int:
    print("Sahaara AI — Jev verification harness")
    print(f"API: {BASE}  |  Model: {JEV_MODEL}")

    try:
        login = api("/api/v1/auth/login", method="POST",
                    body={"username": os.environ.get("SAHAARA_USER", "operator"),
                          "password": os.environ.get("SAHAARA_PASS", "operator123")})
    except Exception as exc:
        print(f"Cannot reach Sahaara API at {BASE}: {exc}\n"
              f"Start it first:  cd backend && .venv/bin/python -m uvicorn main:app --port 8010")
        return 2
    token = login["access_token"]

    cases = deterministic_checks(token)

    if TYPESAFE_KEY and cases:
        jev_checks(cases, token)
    else:
        print("\n── Layer 2: Jev cross-checks SKIPPED ──────────────────────")
        print("   TYPESAFE_API_KEY not set. Get one at https://console.typesafe.ai/keys, then:")
        print("   TYPESAFE_API_KEY=... python scripts/jev_check.py")
        record("SKIP", "Jev cross-checks", "no TYPESAFE_API_KEY")

    # ── Report ──
    counts = {lvl: sum(1 for r in RESULTS if r[0] == lvl) for lvl in ("PASS", "WARN", "FAIL", "SKIP")}
    print("\n── Summary ─────────────────────────────────────────────────")
    print(f"  PASS {counts['PASS']}   WARN {counts['WARN']}   FAIL {counts['FAIL']}   SKIP {counts['SKIP']}")
    if counts["WARN"]:
        print("\n  Warnings (Jev disagreement → human review recommended):")
        for _, name, detail in [r for r in RESULTS if r[0] == "WARN"]:
            print(f"    · {name} — {detail}")
    if counts["FAIL"]:
        print("\n  Failures:")
        for _, name, detail in [r for r in RESULTS if r[0] == "FAIL"]:
            print(f"    · {name} — {detail}")

    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
