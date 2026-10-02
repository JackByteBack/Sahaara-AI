"""Seed demo users and scripted demonstration cases (Feature 1.15)."""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from .models import Case, User
from .security import hash_password
from .service import apply_analysis

DEMO_USERS = [
    ("admin", "Sahaara Admin", "admin", "admin123"),
    ("supervisor", "Duty Supervisor", "supervisor", "super123"),
    ("counsellor", "Helpline Counsellor", "counsellor", "counsel123"),
    ("operator", "Operator One", "operator", "operator123"),
]

_MOCK_PATH = Path(__file__).resolve().parent.parent.parent / "build" / "mock-data.json"


def seed_users(db: Session) -> None:
    for username, display, role, password in DEMO_USERS:
        if db.query(User).filter(User.username == username).first() is None:
            db.add(User(
                username=username,
                display_name=display,
                role=role,
                password_hash=hash_password(password),
            ))
    db.commit()


def seed_demo_cases(db: Session) -> None:
    if db.query(Case).filter(Case.is_demo.is_(True)).count() > 0:
        return

    scripts: list[dict] = []
    if _MOCK_PATH.exists():
        try:
            scripts = json.loads(_MOCK_PATH.read_text()).get("cases", [])
        except json.JSONDecodeError:
            scripts = []

    # Fallback scripts (mirrors build/mock-data.json if the file moves)
    scripts = scripts or [
        {
            "case_id": "c1",
            "transcript": "I am feeling very lonely and I think about hurting myself sometimes.",
        },
        {
            "case_id": "c2",
            "transcript": "My husband came home and started yelling at me again.",
        },
    ]

    extra = [
        {
            "transcript": "He is here right now with a knife, he is threatening me and beating me. They are listening, I can't talk long.",
            "mode": "voice",
        },
        {
            "transcript": "मुझे बहुत डर लग रहा है, वह धमकी देता है और मारपीट करता है। मेरे पास कोई नहीं है।",
            "mode": "text",
        },
        {
            "transcript": "मला भीती वाटते, तो इथे आहे. ऐकत आहे म्हणून मी खूप काय सांगू शकत नाही.",
            "mode": "text",
        },
    ]

    from .routers.cases import _next_case_number

    for i, script in enumerate(scripts + extra):
        transcript = script.get("transcript", "")
        segments = [
            {"text": s.strip(), "speaker": "caller", "timestamp": float(idx) * 5.0}
            for idx, s in enumerate(transcript.split("."))
            if s.strip()
        ]
        case = Case(
            case_number=_next_case_number(db),
            status="reviewing",
            session_mode=script.get("mode", "text"),
            is_demo=True,
            consent={"given": True, "scope": "demonstration", "synthetic": True},
            transcript=segments,
        )
        db.add(case)
        db.flush()
        apply_analysis(db, case, notify=False)

    db.commit()


def seed(db: Session) -> None:
    seed_users(db)
    seed_demo_cases(db)
