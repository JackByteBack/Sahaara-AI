"""Auth dependencies and RBAC guards (Feature 1.11)."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_access_token

bearer = HTTPBearer(auto_error=False)

# Role capability map — every protected route declares the roles allowed.
ROLE_CAPABILITIES = {
    "case_read": ["admin", "operator", "supervisor", "counsellor"],
    "case_create": ["admin", "operator", "supervisor"],
    "case_review": ["admin", "operator", "supervisor", "counsellor"],
    "case_escalate": ["admin", "supervisor", "counsellor"],
    "referral_confirm": ["admin", "supervisor", "counsellor"],
    "case_anonymize": ["admin", "supervisor"],
    "analytics_read": ["admin", "supervisor", "counsellor", "operator"],
    "audit_read": ["admin", "supervisor"],
    "user_manage": ["admin"],
    "user_list": ["admin", "supervisor", "counsellor"],  # minimal directory for assignment
}


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = db.get(User, payload.get("sub"))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require(capability: str):
    allowed = ROLE_CAPABILITIES[capability]

    def guard(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: '{capability}' requires role in {allowed}",
            )
        return user

    return guard
