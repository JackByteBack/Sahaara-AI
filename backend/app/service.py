"""Shared case-analysis service: runs the pipeline, persists, and notifies the UI."""
from __future__ import annotations

from sqlalchemy.orm import Session

from .ai import analyze
from .audit import log_action
from .models import Case
from .ws import manager


def apply_analysis(
    db: Session,
    case: Case,
    speech_features: dict | None = None,
    actor_id: str | None = None,
    notify: bool = True,
) -> dict:
    """Run Feature 1.1/1.4/2.1/2.2/2.5/2.10 analysis over the case transcript and persist results."""
    result = analyze(case.transcript or [], speech_features, trauma_mode=case.trauma_mode)

    # Merge flags: preserve human decisions on indicators we've already seen (Feature 1.6)
    existing = {(f.get("category"), f.get("transcript_excerpt")): f for f in (case.ai_flags or [])}
    merged, fresh = [], []
    for flag in result["flags"]:
        key = (flag["category"], flag["transcript_excerpt"])
        prev = existing.get(key)
        if prev:
            flag = {
                **flag,
                "id": prev.get("id", flag["id"]),
                "status": prev.get("status", "suggested"),
                "human_decision": prev.get("human_decision"),
                "decision_notes": prev.get("decision_notes", ""),
                "decided_by": prev.get("decided_by"),
                "decided_at": prev.get("decided_at"),
            }
        else:
            fresh.append(flag)
        merged.append(flag)

    case.ai_flags = merged
    case.victim_safety_profile = result["victim_safety_profile"]
    case.uncertainty = result["uncertainty"]
    case.language_info = result["language_info"]
    case.review_priority_score = result["review_priority_score"]
    case.safety_override = result["safety_override"]
    case.safety_override_reason = result["safety_override_reason"]
    case.assessment_confidence = result["uncertainty"].get("assessment_confidence", 0.0)

    if case.status == "active" and (merged or result["safety_override"]):
        case.status = "reviewing"

    log_action(
        db,
        "ai_analysis",
        (
            f"pipeline={result['mode']} flags={len(merged)} new={len(fresh)} "
            f"priority={case.review_priority_score} override={case.safety_override}"
        ),
        case_id=case.id,
        user_id=actor_id,
    )
    db.commit()

    if notify:
        payload = _case_event_payload(case)
        for flag in fresh:
            _notify(case, {
                "type": "ai_flag",
                "case_id": case.id,
                "category": flag["category"],
                "confidence": flag["confidence"],
                "severity": flag["severity"],
                "text": flag["transcript_excerpt"],
                "description": flag["description"],
                "timestamp": flag["timestamp"],
                "source": flag["source"],
                "flag_id": flag["id"],
            })
        _notify(case, payload)
        if case.safety_override:
            _notify(case, {
                "type": "status_update",
                "case_id": case.id,
                "priority": case.review_priority_score,
                "mode": "safety_override",
                "reason": case.safety_override_reason,
                "safety_override": True,
            })
    return result


def _notify(case: Case, message: dict) -> None:
    import asyncio

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast(case.id, message))
    except RuntimeError:
        # running in a sync worker without a loop (e.g. CLI/seed) — skip broadcast
        pass


def _case_event_payload(case: Case) -> dict:
    return {
        "type": "profile_update",
        "case_id": case.id,
        "review_priority_score": case.review_priority_score,
        "safety_override": case.safety_override,
        "safety_override_reason": case.safety_override_reason,
        "victim_safety_profile": case.victim_safety_profile,
        "uncertainty": case.uncertainty,
        "language_info": case.language_info,
        "mode": "human_assessment" if not _ai_on() else "ai_assisted",
        "flag_count": len(case.ai_flags or []),
    }


def _ai_on() -> bool:
    from .ai.llm import ai_available

    return ai_available()


async def broadcast(case_id: str, message: dict) -> None:
    await manager.broadcast(case_id, message)
