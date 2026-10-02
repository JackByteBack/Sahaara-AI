"""Admin user management (Feature 1.11 RBAC administration)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..audit import log_action
from ..database import get_db
from ..deps import require
from ..models import User
from ..routers.auth import UserOut
from ..security import hash_password

router = APIRouter(prefix="/api/v1/users", tags=["users"])

VALID_ROLES = {"admin", "operator", "supervisor", "counsellor"}


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    role: str = "operator"
    display_name: str = ""
    language: str = "en"


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require("user_manage"))):
    return [
        UserOut(id=u.id, username=u.username, display_name=u.display_name or u.username,
                role=u.role, language=u.language)
        for u in db.query(User).order_by(User.created_at).all()
    ]


@router.get("/assignable", response_model=list[UserOut])
def list_assignable(db: Session = Depends(get_db), user: User = Depends(require("user_list"))):
    """Minimal directory for the case-assignment workflow (id/name/role only)."""
    return [
        UserOut(id=u.id, username=u.username, display_name=u.display_name or u.username,
                role=u.role, language=u.language)
        for u in db.query(User).order_by(User.username).all()
    ]


@router.post("", response_model=UserOut)
def create_user(body: CreateUserRequest, db: Session = Depends(get_db), admin: User = Depends(require("user_manage"))):
    if body.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"role must be one of {sorted(VALID_ROLES)}")
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        role=body.role,
        display_name=body.display_name or body.username,
        language=body.language,
    )
    db.add(user)
    log_action(db, "admin_change", f"created user={body.username} role={body.role}", user_id=admin.id)
    db.commit()
    return UserOut(id=user.id, username=user.username, display_name=user.display_name,
                   role=user.role, language=user.language)
