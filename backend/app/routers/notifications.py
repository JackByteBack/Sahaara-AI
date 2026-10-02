"""Notification feed — derived, no extra tables.

Surfaces the things a helpline console should nudge a human about:
  · active Safety Override cases (updated in the last 7 days)
  · follow-ups due today or overdue
  · pending referral confirmations (for roles that can confirm)
  · cases assigned to the current user

Read-state is kept client-side (localStorage) — this feed is always fresh
and never stores anything new about a caller (data minimization).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require
from ..models import Case, Referral, User

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@router.get("")
def list_notifications(
    db: Session = Depends(get_db),
    user: User = Depends(require("case_read")),
):
    now = datetime.now(timezone.utc)
    today = now.date()
    items: list[dict] = []

    open_cases = db.query(Case).filter(Case.status != "closed").all()

    # 1. Active Safety Override — always top of the feed
    for c in open_cases:
        if not c.safety_override:
            continue
        updated = c.updated_at or c.created_at
        if updated and (now - updated) > timedelta(days=7):
            continue
        items.append({
            "id": f"safety-{c.id}",
            "type": "safety_override",
            "severity": "critical",
            "case_id": c.id,
            "case_number": c.case_number,
            "title": "Safety Override active",
            "body": (c.safety_override_reason or "Immediate-safety rule matched.")[:160],
            "link": f"/cases/{c.id}",
            "created_at": updated.isoformat() if updated else None,
        })

    # 2. Follow-ups due today or overdue
    for c in open_cases:
        for f in c.followups or []:
            if f.get("completed") or not f.get("due_at"):
                continue
            try:
                due = datetime.fromisoformat(str(f["due_at"])[:10]).date()
            except ValueError:
                continue
            if due > today:
                continue
            overdue = due < today
            items.append({
                "id": f"followup-{c.id}-{f.get('id')}",
                "type": "followup_due",
                "severity": "high" if overdue else "medium",
                "case_id": c.id,
                "case_number": c.case_number,
                "title": "Follow-up overdue" if overdue else "Follow-up due today",
                "body": f"[{f.get('stage', 'followup')}] {f.get('note') or ''}".strip()[:160],
                "link": f"/cases/{c.id}",
                "created_at": f.get("created_at"),
            })

    # 3. Pending referral confirmations — only for roles that can confirm
    if user.role in ("admin", "supervisor", "counsellor"):
        pending = (
            db.query(Referral)
            .join(Case, Referral.case_id == Case.id)
            .filter(Referral.status == "pending", Case.status != "closed")
            .all()
        )
        for r in pending:
            items.append({
                "id": f"referral-{r.id}",
                "type": "referral_pending",
                "severity": "medium",
                "case_id": r.case_id,
                "case_number": r.case.case_number if r.case else "",
                "title": "Referral awaiting confirmation",
                "body": f"{r.referral_type} — human confirmation required",
                "link": f"/cases/{r.case_id}",
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })

    # 4. Cases assigned to me
    for c in open_cases:
        if c.assigned_to != user.id:
            continue
        items.append({
            "id": f"assigned-{c.id}",
            "type": "assigned",
            "severity": "medium",
            "case_id": c.id,
            "case_number": c.case_number,
            "title": "Case assigned to you",
            "body": f"Priority {c.review_priority_score:.2f} · status {c.status}",
            "link": f"/cases/{c.id}",
            "created_at": (c.updated_at or c.created_at).isoformat()
            if (c.updated_at or c.created_at) else None,
        })

    items.sort(key=lambda n: (SEVERITY_ORDER.get(n["severity"], 9), n.get("created_at") or ""))
    items = items[:30]
    return {
        "notifications": items,
        "counts": {
            "critical": sum(1 for n in items if n["severity"] == "critical"),
            "total": len(items),
        },
        "generated_at": now.isoformat(),
    }
