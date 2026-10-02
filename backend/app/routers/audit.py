"""Global audit access (Feature 1.13) — admin/supervisor only."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require
from ..models import AuditLog, User

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("")
def list_audit(
    limit: int = Query(100, le=500),
    action: str | None = None,
    case_id: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require("audit_read")),
):
    q = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
    if action:
        q = q.filter(AuditLog.action == action)
    if case_id:
        q = q.filter(AuditLog.case_id == case_id)
    entries = q.limit(limit).all()
    return {
        "entries": [
            {
                "id": e.id,
                "action": e.action,
                "details": e.details,
                "case_id": e.case_id,
                "user_id": e.user_id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            }
            for e in entries
        ]
    }
