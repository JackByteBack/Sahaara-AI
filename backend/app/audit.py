"""Feature 1.13 — audit trail helper."""
from sqlalchemy.orm import Session

from .models import AuditLog


def log_action(
    db: Session,
    action: str,
    details: str = "",
    case_id: str | None = None,
    user_id: str | None = None,
    commit: bool = False,
) -> AuditLog:
    entry = AuditLog(action=action, details=details, case_id=case_id, user_id=user_id)
    db.add(entry)
    if commit:
        db.commit()
    else:
        db.flush()
    return entry
