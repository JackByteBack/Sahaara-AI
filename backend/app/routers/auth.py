"""Auth endpoints — login + current user + profile settings (Features 1.11, 1.13)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..audit import log_action
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import LoginRequest, ProfileUpdate, TokenResponse, UserOut
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if user is None or not verify_password(body.password, user.password_hash):
        log_action(db, "login_failed", f"username={body.username}", commit=True)
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(user.id, user.role, user.username)
    log_action(db, "login", f"user={user.username} role={user.role}", user_id=user.id, commit=True)
    return TokenResponse(
        access_token=token,
        user=UserOut(
            id=user.id,
            username=user.username,
            display_name=user.display_name or user.username,
            role=user.role,
            language=user.language,
        ),
    )


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name or user.username,
        role=user.role,
        language=user.language,
    )


@router.patch("/me", response_model=UserOut)
def update_me(
    body: ProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Settings page — display name, interface language, password change (audited)."""
    changes: list[str] = []

    if body.display_name is not None:
        name = body.display_name.strip()
        if len(name) > 100:
            raise HTTPException(status_code=400, detail="Display name too long (max 100)")
        user.display_name = name
        changes.append("display_name")

    if body.language is not None:
        if body.language not in ("en", "hi", "mr"):
            raise HTTPException(status_code=400, detail="language must be en | hi | mr")
        user.language = body.language
        changes.append("language")

    if body.new_password:
        if not body.current_password or not verify_password(body.current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        if len(body.new_password) < 8:
            raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
        user.password_hash = hash_password(body.new_password)
        changes.append("password_changed")

    if not changes:
        raise HTTPException(status_code=400, detail="Nothing to update")

    log_action(
        db, "settings",
        f"profile updated by {user.username}: {', '.join(changes)}",
        user_id=user.id, commit=True,
    )
    return UserOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name or user.username,
        role=user.role,
        language=user.language,
    )
