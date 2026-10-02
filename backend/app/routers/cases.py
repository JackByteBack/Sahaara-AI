"""Case management endpoints (Features 1.6, 1.7, 1.8, 1.9, 1.10, 2.16, 2.17)."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from ..ai.anonymize import anonymize_case
from ..ai.llm import generate
from ..ai.summary import build_summary
from ..audit import log_action
from ..database import get_db
from ..deps import require
from ..models import AuditLog, Case, Referral, User
from ..ratelimit import check_rate_limit
from ..schemas import (
    AnonymizeRequest,
    CaseUpdate,
    FlagDecisionRequest,
    FollowupCreate,
    FollowupUpdate,
    NoteCreate,
    ReferralCreate,
    ReviewRequest,
    SegmentIn,
    StartCaseRequest,
)
from ..service import apply_analysis

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])


def _next_case_number(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    count = db.query(Case).count() + 1
    while True:
        candidate = f"SAH-{year}-{count:04d}"
        if db.query(Case).filter(Case.case_number == candidate).first() is None:
            return candidate
        count += 1


def serialize_case(case: Case, include_transcript: bool = True) -> dict:
    data = {
        "id": case.id,
        "case_number": case.case_number,
        "status": case.status,
        "created_by": case.created_by,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        "review_priority_score": case.review_priority_score,
        "assessment_confidence": case.assessment_confidence,
        "safety_override": case.safety_override,
        "safety_override_reason": case.safety_override_reason,
        "ai_flags": case.ai_flags or [],
        "victim_safety_profile": case.victim_safety_profile or {},
        "uncertainty": case.uncertainty or {},
        "language_info": case.language_info or {},
        "summary": case.summary or {},
        "final_decision": case.final_decision,
        "consent": case.consent or {},
        "notes": case.notes or [],
        "followups": case.followups or [],
        "session_mode": case.session_mode,
        "trauma_mode": case.trauma_mode,
        "is_demo": case.is_demo,
        "anonymized": case.anonymized,
        "assigned_to": case.assigned_to,
        "assigned_to_username": case.assignee.username if case.assignee else None,
        "referrals": [
            {
                "id": r.id,
                "referral_type": r.referral_type,
                "status": r.status,
                "ai_suggested": r.ai_suggested,
                "notes": r.notes,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in case.referrals
        ],
    }
    if include_transcript:
        data["transcript"] = case.transcript or []
    return data


# ── Session start (tech-specs.md §3.1) ────────────────────────────────
@router.post("/start")
def start_case(
    body: StartCaseRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_create")),
):
    check_rate_limit(db, f"start:{user.id}", max_requests=5, window_seconds=60)
    case = Case(
        case_number=_next_case_number(db),
        status="active",
        created_by=user.id,
        session_mode=body.mode,
        trauma_mode=body.trauma_mode,
        consent={
            "given": body.consent,
            "scope": body.consent_scope,
            "given_at": datetime.now(timezone.utc).isoformat(),
        },
        language_info={"primary": {"language": body.initial_language, "confidence": 1.0},
                       "operator_override": body.language_override},
    )
    db.add(case)
    db.flush()
    log_action(db, "created", f"Case started mode={body.mode} consent={body.consent}", case_id=case.id, user_id=user.id)
    db.commit()
    return serialize_case(case)


# ── Queue listing ─────────────────────────────────────────────────────
def _primary_language(case: Case) -> str:
    return ((case.language_info or {}).get("primary") or {}).get("language", "en")


@router.get("")
def list_cases(
    status: str | None = Query(None),
    q: str | None = Query(None),
    language: str | None = Query(None, description="Filter by primary language (en|hi|mr)"),
    safety: bool | None = Query(None, description="true = safety-override cases only"),
    assigned: str | None = Query(None, description="mine | unassigned"),
    min_priority: float | None = Query(None, ge=0, le=1),
    include_closed: bool = True,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_read")),
):
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    elif not include_closed:
        query = query.filter(Case.status != "closed")
    if q:
        query = query.filter(Case.case_number.ilike(f"%{q}%"))
    cases = query.all()

    # JSON/python-side filters (dataset sizes are pilot-scale)
    if language:
        cases = [c for c in cases if _primary_language(c) == language]
    if safety is not None:
        cases = [c for c in cases if bool(c.safety_override) == safety]
    if assigned == "mine":
        cases = [c for c in cases if c.assigned_to == user.id]
    elif assigned == "unassigned":
        cases = [c for c in cases if not c.assigned_to]
    if min_priority is not None:
        cases = [c for c in cases if (c.review_priority_score or 0) >= min_priority]

    # Safety override pins to the top of the queue (docs/rules.md §Review Priorities 2-3)
    cases.sort(
        key=lambda c: (
            0 if c.safety_override else 1,
            0 if any(f.get("category") == "coercion" for f in (c.ai_flags or [])) else 1,
            -c.review_priority_score,
            -(c.created_at.timestamp() if c.created_at else 0),
        )
    )
    return {"cases": [serialize_case(c, include_transcript=False) for c in cases]}


EXPORT_COLUMNS = [
    "case_number", "status", "review_priority_score", "safety_override",
    "safety_override_reason", "language", "flag_count", "flags_decided",
    "final_decision", "assigned_to", "session_mode", "trauma_mode",
    "is_demo", "anonymized", "created_at", "updated_at",
]


def _export_row(case: Case, db: Session) -> dict:
    """Sanitized export row — transcript/notes are deliberately NOT exported (data minimization)."""
    flags = case.ai_flags or []
    assigned = None
    if case.assigned_to:
        assignee = db.get(User, case.assigned_to)
        assigned = assignee.username if assignee else case.assigned_to
    return {
        "case_number": case.case_number,
        "status": case.status,
        "review_priority_score": case.review_priority_score,
        "safety_override": case.safety_override,
        "safety_override_reason": case.safety_override_reason,
        "language": _primary_language(case),
        "flag_count": len(flags),
        "flags_decided": sum(1 for f in flags if f.get("human_decision")),
        "final_decision": (case.final_decision or {}).get("decision", ""),
        "assigned_to": assigned or "",
        "session_mode": case.session_mode,
        "trauma_mode": case.trauma_mode,
        "is_demo": case.is_demo,
        "anonymized": case.anonymized,
        "created_at": case.created_at.isoformat() if case.created_at else "",
        "updated_at": case.updated_at.isoformat() if case.updated_at else "",
    }


@router.get("/export")
def export_cases(
    format: str = Query("csv", pattern="^(csv|json)$"),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require("case_read")),
):
    """Audited, sanitized case export (no transcript/notes — Feature 1.13)."""
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    cases = query.order_by(Case.created_at.desc()).all()
    rows = [_export_row(c, db) for c in cases]

    log_action(
        db, "exported",
        f"format={format} count={len(rows)}" + (f" status={status}" if status else ""),
        user_id=user.id, commit=True,
    )

    if format == "json":
        return JSONResponse(
            content={"exported_at": datetime.now(timezone.utc).isoformat(),
                     "count": len(rows), "cases": rows},
            headers={"Content-Disposition": 'attachment; filename="sahaara-cases.json"'},
        )

    import csv
    import io

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=EXPORT_COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="sahaara-cases.csv"'},
    )


@router.get("/{case_id}")
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_read")),
):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    log_action(db, "case_access", f"transcript access by {user.username}", case_id=case.id, user_id=user.id)
    db.commit()
    return serialize_case(case)


@router.patch("/{case_id}")
def update_case(
    case_id: str,
    body: CaseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_read")),
):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    changes = []
    if body.status:
        if body.status not in ("active", "reviewing", "referred", "closed"):
            raise HTTPException(status_code=400, detail="Invalid status")
        if case.status == "closed":
            raise HTTPException(status_code=400, detail="Closed cases cannot be reopened; create a new case.")
        changes.append(f"status {case.status}->{body.status}")
        case.status = body.status
    if body.trauma_mode is not None:
        changes.append(f"trauma_mode {case.trauma_mode}->{body.trauma_mode}")
        case.trauma_mode = body.trauma_mode
    if body.language_override:
        li = dict(case.language_info or {})  # copy — JSON change tracking (see decide_flag)
        li["operator_override"] = body.language_override
        case.language_info = li
        changes.append(f"language_override={body.language_override}")
    if body.assigned_to is not None:
        if body.assigned_to == "":
            if case.assigned_to:
                changes.append("assignment cleared")
            case.assigned_to = None
        else:
            # Operators may assign to themselves only; supervisors/counsellors/admins may assign anyone.
            if body.assigned_to != user.id and user.role not in ("admin", "supervisor", "counsellor"):
                raise HTTPException(status_code=403, detail="Only supervisors, counsellors or admins can assign cases to others.")
            assignee = db.get(User, body.assigned_to)
            if assignee is None:
                raise HTTPException(status_code=400, detail="Unknown assignee")
            case.assigned_to = assignee.id
            changes.append(f"assigned to {assignee.username}")
    log_action(db, "modified", "; ".join(changes) or "no-op", case_id=case.id, user_id=user.id)
    db.commit()
    return serialize_case(case)


# ── Transcript ingestion (drives real-time analysis) ──────────────────
@router.post("/{case_id}/segments")
async def add_segment(
    case_id: str,
    body: SegmentIn,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_read")),
):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.status == "closed":
        raise HTTPException(status_code=400, detail="Case is closed (anonymized).")

    segment = {
        "text": body.text,
        "speaker": body.speaker,
        "timestamp": body.timestamp,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "by_user": user.id,
    }
    case.transcript = list(case.transcript or []) + [segment]

    from ..ws import manager

    await manager.broadcast(case_id, {
        "type": "transcript",
        "case_id": case_id,
        "text": body.text,
        "speaker": body.speaker,
        "timestamp": body.timestamp,
        "language": (body.text and (case.language_info or {}).get("primary", {}) or {}).get("language", "en"),
    })

    feats = body.speech.model_dump() if body.speech else None
    result = apply_analysis(db, case, speech_features=feats, actor_id=user.id)
    return {
        "ok": True,
        "segment": segment,
        "review_priority_score": result["review_priority_score"],
        "safety_override": result["safety_override"],
        "new_flags": len(result["flags"]),
        "mode": result["mode"],
    }


# ── Human-in-the-loop review (Feature 1.6) ────────────────────────────
@router.post("/{case_id}/review")
def review_case(
    case_id: str,
    body: ReviewRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_review")),
):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    if body.decision not in ("confirm", "modify", "escalate", "dismiss"):
        raise HTTPException(status_code=400, detail="decision must be confirm|modify|escalate|dismiss")
    if body.decision == "escalate" and user.role == "operator":
        raise HTTPException(status_code=403, detail="Escalation requires supervisor/counsellor/admin.")
    if body.decision == "dismiss" and case.safety_override and not body.override_ai:
        raise HTTPException(
            status_code=400,
            detail="Safety Override active — dismiss requires explicit override_ai=true and supervisor role.",
        )

    original_score = case.review_priority_score
    if body.final_priority is not None:
        if not 0 <= body.final_priority <= 1:
            raise HTTPException(status_code=400, detail="final_priority must be 0..1")
        case.review_priority_score = round(body.final_priority, 2)

    case.final_decision = {
        "decision": body.decision,
        "override_ai": body.override_ai,
        "notes": body.notes,
        "original_score": original_score,
        "final_score": case.review_priority_score,
        "decided_by": user.username,
        "decided_role": user.role,
        "decided_at": datetime.now(timezone.utc).isoformat(),
    }

    if body.decision == "escalate":
        case.status = "reviewing"
    elif body.decision == "confirm" and case.status == "active":
        case.status = "reviewing"

    action = {"confirm": "reviewed", "modify": "flag_modified", "escalate": "escalated", "dismiss": "dismissed"}[body.decision]
    log_action(
        db, action,
        f"decision={body.decision} override_ai={body.override_ai} score {original_score}->{case.review_priority_score} notes={body.notes}",
        case_id=case.id, user_id=user.id,
    )
    db.commit()
    return serialize_case(case)


@router.post("/{case_id}/flags/{flag_id}/decision")
def decide_flag(
    case_id: str,
    flag_id: str,
    body: FlagDecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_review")),
):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    if body.decision not in ("confirm", "modify", "escalate", "dismiss"):
        raise HTTPException(status_code=400, detail="decision must be confirm|modify|escalate|dismiss")

    # Copy before mutating: SQLAlchemy skips JSON updates when old/new compare equal
    # (in-place mutation of the loaded value is invisible to the change tracker).
    flags = [dict(f) for f in (case.ai_flags or [])]
    flag = next((f for f in flags if f.get("id") == flag_id), None)
    if flag is None:
        raise HTTPException(status_code=404, detail="Flag not found")

    critical = flag.get("category") in ("immediate_danger", "self_harm") and flag.get("severity") in ("high", "critical")
    if body.decision == "dismiss" and critical and case.safety_override:
        raise HTTPException(
            status_code=400,
            detail="Safety-critical flag cannot be dismissed while Safety Override is active — confirm or escalate.",
        )
    if body.decision == "escalate" and user.role == "operator":
        raise HTTPException(status_code=403, detail="Escalation requires supervisor/counsellor/admin.")

    flag["human_decision"] = body.decision
    flag["status"] = {"confirm": "confirmed", "modify": "modified", "escalate": "escalated", "dismiss": "dismissed"}[body.decision]
    flag["decision_notes"] = body.notes
    flag["decided_by"] = user.username
    flag["decided_at"] = datetime.now(timezone.utc).isoformat()
    if body.modified_severity:
        flag["severity"] = body.modified_severity

    case.ai_flags = flags
    if body.decision == "escalate":
        case.status = "reviewing"

    log_action(db, "flag_modified", f"flag={flag_id} {body.decision} sev={flag['severity']} notes={body.notes}",
               case_id=case.id, user_id=user.id)
    db.commit()

    from ..ws import manager
    import asyncio
    try:
        asyncio.get_running_loop().create_task(manager.broadcast(case_id, {
            "type": "flag_decision", "case_id": case_id, "flag_id": flag_id,
            "decision": body.decision, "severity": flag["severity"],
        }))
    except RuntimeError:
        pass
    return {"ok": True, "flag": flag}


# ── Notes / follow-ups (Features 1.7, 2.17) ───────────────────────────
@router.post("/{case_id}/notes")
def add_note(
    case_id: str, body: NoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_review")),
):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    note = {
        "id": f"n-{len(case.notes or []) + 1}",
        "body": body.body,
        "author": user.username,
        "author_role": user.role,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    case.notes = list(case.notes or []) + [note]
    log_action(db, "modified", f"note added by {user.username}", case_id=case.id, user_id=user.id)
    db.commit()
    return {"ok": True, "note": note}


@router.post("/{case_id}/followups")
def add_followup(
    case_id: str, body: FollowupCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_review")),
):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    entry = {
        "id": f"f-{len(case.followups or []) + 1}",
        "stage": body.stage,
        "note": body.note,
        "outcome": body.outcome,
        "due_at": body.due_at,
        "completed": False,
        "by": user.username,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    case.followups = list(case.followups or []) + [entry]
    log_action(db, "modified", f"followup[{body.stage}] by {user.username}", case_id=case.id, user_id=user.id)
    db.commit()
    return {"ok": True, "followup": entry}


@router.patch("/{case_id}/followups/{followup_id}")
def update_followup(
    case_id: str, followup_id: str,
    body: FollowupUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_review")),
):
    """Complete / reschedule a follow-up (drives the reminder feed)."""
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    # Copy before mutating — see decide_flag() for why (JSON change tracking).
    followups = [dict(f) for f in (case.followups or [])]
    entry = next((f for f in followups if f.get("id") == followup_id), None)
    if entry is None:
        raise HTTPException(status_code=404, detail="Follow-up not found")

    if body.outcome is not None:
        entry["outcome"] = body.outcome
    if body.due_at is not None:
        entry["due_at"] = body.due_at
    if body.completed is not None:
        entry["completed"] = body.completed
        entry["completed_by"] = user.username
        entry["completed_at"] = datetime.now(timezone.utc).isoformat()

    case.followups = followups
    log_action(
        db, "modified",
        f"followup {followup_id} completed={entry.get('completed')} by {user.username}",
        case_id=case.id, user_id=user.id,
    )
    db.commit()
    return {"ok": True, "followup": entry}


# ── Referrals (Features 1.8, 2.16 — AI suggests, humans confirm) ──────
VALID_REFERRALS = {
    "counselling", "mental_health", "medical", "legal_aid", "protection",
    "emergency", "shelter", "rehabilitation", "welfare",
}


@router.post("/{case_id}/referrals")
def create_referral(
    case_id: str, body: ReferralCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_review")),
):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    if body.referral_type not in VALID_REFERRALS:
        raise HTTPException(status_code=400, detail=f"referral_type must be one of {sorted(VALID_REFERRALS)}")
    referral = Referral(
        case_id=case.id, referral_type=body.referral_type,
        notes=body.notes, ai_suggested=body.ai_suggested, created_by=user.id,
        status="pending",
    )
    db.add(referral)
    if case.status == "reviewing":
        case.status = "referred"
    log_action(db, "referral", f"type={body.referral_type} ai_suggested={body.ai_suggested}", case_id=case.id, user_id=user.id)
    db.commit()
    return {"ok": True, "referral_id": referral.id, "status": referral.status}


@router.post("/{case_id}/referrals/{referral_id}/confirm")
def confirm_referral(
    case_id: str, referral_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require("referral_confirm")),
):
    referral = db.get(Referral, referral_id)
    if referral is None or referral.case_id != case_id:
        raise HTTPException(status_code=404, detail="Referral not found")
    referral.status = "confirmed"
    referral.confirmed_by = user.id
    log_action(db, "referral", f"confirmed {referral.referral_type} by {user.username}", case_id=case_id, user_id=user.id)
    db.commit()
    return {"ok": True, "status": referral.status}


# ── Summaries (Feature 1.9 — generative + extractive fallback) ────────
@router.post("/{case_id}/summary")
async def generate_summary(
    case_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_review")),
):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    text = "\n".join(s.get("text", "") for s in (case.transcript or []))
    primary_lang = ((case.language_info or {}).get("primary") or {}).get("language", "en")

    llm_result = await generate(
        text,
        context={
            "trauma_mode": case.trauma_mode,
            "flag_categories": sorted({f.get("category") for f in (case.ai_flags or [])}),
            "profile": case.victim_safety_profile or {},
        },
        language=primary_lang,
    )
    summary = build_summary(text, case.ai_flags or [], case.victim_safety_profile or {}, llm_result)
    summary["generated_at"] = datetime.now(timezone.utc).isoformat()
    summary["generated_by_user"] = user.username
    case.summary = summary

    log_action(
        db, "summary_generated",
        f"type={summary['summary_type']} source={summary['generated_by']} llm_ok={llm_result.get('ok')} reason={llm_result.get('reason', '')}",
        case_id=case.id, user_id=user.id,
    )
    db.commit()
    return summary


@router.post("/{case_id}/anonymize")
def close_and_anonymize(
    case_id: str,
    body: AnonymizeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_anonymize")),
):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    anonymize_case(case, body.extra_names)
    case.status = "closed"
    log_action(db, "deleted", "PII scrubbed and case closed (Feature 1.10 anonymization)", case_id=case.id, user_id=user.id)
    db.commit()
    return {"ok": True, "status": case.status, "anonymized": True}


@router.get("/{case_id}/audit")
def case_audit(
    case_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require("audit_read")),
):
    entries = db.query(AuditLog).filter(AuditLog.case_id == case_id).order_by(AuditLog.timestamp.desc()).all()
    return {
        "entries": [
            {
                "id": e.id, "action": e.action, "details": e.details,
                "user_id": e.user_id, "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            }
            for e in entries
        ]
    }
