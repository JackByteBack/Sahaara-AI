"""Feature 1.15 — scripted demonstration cases (multilingual, varied priority)."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..audit import log_action
from ..database import get_db
from ..deps import get_current_user, require
from ..models import Case, User
from ..routers.cases import _next_case_number, serialize_case
from ..service import apply_analysis

router = APIRouter(prefix="/api/v1/demos", tags=["demos"])

# Scripted scenarios across languages, safety levels and priority bands.
SCENARIOS: list[dict] = [
    {
        "id": "demo-en-critical",
        "title": "English — Immediate danger (Safety Override)",
        "language": "en",
        "mode": "voice",
        "expected": "Safety Override → critical queue position",
        "lines": [
            "Hello? Please help me.",
            "He is here right now and he has a knife.",
            "He is threatening me and beating me, I am in danger.",
            "They are listening, I can't talk for long. Please help me.",
        ],
    },
    {
        "id": "demo-en-selfharm",
        "title": "English — Self-harm concern (Feature 2.6)",
        "language": "en",
        "mode": "text",
        "expected": "Self-harm pathway + high priority",
        "lines": [
            "I have been feeling very lonely lately.",
            "I feel hopeless and I think about hurting myself sometimes.",
            "No one to help me, everyone would be better off without me.",
        ],
    },
    {
        "id": "demo-hi-distress",
        "title": "हिंदी — Distress + vulnerability (Feature 1.3)",
        "language": "hi",
        "mode": "text",
        "expected": "Medium priority, Hindi transcript retained",
        "lines": [
            "मुझे बहुत डर लग रहा है, मैं उदास हूँ।",
            "मेरे पास कोई नहीं है, मदद चाहिए।",
            "वह धमकी देता है और मारपीट करता है।",
        ],
    },
    {
        "id": "demo-mr-coercion",
        "title": "मराठी — Coercion/interference (Feature 2.12)",
        "language": "mr",
        "mode": "text",
        "expected": "Possible coercion → high priority, human review",
        "lines": [
            "मला भीती वाटते, तो इथे आहे.",
            "ऐकत आहे म्हणून मी खूप काय सांगू शकत नाही.",
            "कोणाला सांगू नका, मला मदत हवी आहे.",
        ],
    },
    {
        "id": "demo-codeswitch",
        "title": "Code-switching — Marathi/Hindi/English (Feature 2.9)",
        "language": "mr",
        "mode": "text",
        "expected": "is_code_switched=true with switch points",
        "lines": [
            "Mala khup bhiti vatate...",
            "they are threatening me every day.",
            "मैं डर के कारण सो नहीं पा रही हूँ, please help me.",
        ],
    },
    {
        "id": "demo-en-low",
        "title": "English — Low distress (routine case)",
        "language": "en",
        "mode": "text",
        "expected": "Low priority, no override",
        "lines": [
            "I am feeling a bit sad about moving away from my family.",
            "I have friends here so it is manageable.",
        ],
    },
    {
        "id": "demo-trauma",
        "title": "English — Trauma indicators (Feature 2.7)",
        "language": "en",
        "mode": "text",
        "expected": "Trauma indicators, counselling pathway suggested",
        "lines": [
            "I keep thinking about what happened, nightmares every night.",
            "I freeze whenever someone raises their voice.",
            "It was rape and I was afraid to tell anyone.",
        ],
    },
]


@router.get("")
def list_demos(user: User = Depends(get_current_user)):
    return {"scenarios": [{k: v for k, v in s.items() if k != "lines"} | {"line_count": len(s["lines"])} for s in SCENARIOS]}


@router.get("/{scenario_id}")
def get_scenario(scenario_id: str, user: User = Depends(get_current_user)):
    scenario = next((s for s in SCENARIOS if s["id"] == scenario_id), None)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.post("/{scenario_id}/start")
def start_demo(
    scenario_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_create")),
):
    """Create an empty demo case; the console then streams lines through the live pipeline."""
    scenario = next((s for s in SCENARIOS if s["id"] == scenario_id), None)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")

    case = Case(
        case_number=_next_case_number(db),
        status="active",
        created_by=user.id,
        session_mode="demo",
        is_demo=True,
        consent={"given": True, "scope": "demonstration", "given_at": datetime.now(timezone.utc).isoformat(), "synthetic": True},
        language_info={"primary": {"language": scenario["language"], "confidence": 1.0}},
    )
    db.add(case)
    db.flush()
    log_action(db, "created", f"Demo case started scenario={scenario_id}", case_id=case.id, user_id=user.id)
    db.commit()
    return {"case": serialize_case(case), "scenario": scenario}


@router.post("/{scenario_id}/preload")
def preload_demo(
    scenario_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require("case_create")),
):
    """Load a full demo transcript at once (analysis runs over the complete conversation)."""
    scenario = next((s for s in SCENARIOS if s["id"] == scenario_id), None)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found")

    case = Case(
        case_number=_next_case_number(db),
        status="active",
        created_by=user.id,
        session_mode="demo",
        is_demo=True,
        consent={"given": True, "scope": "demonstration", "given_at": datetime.now(timezone.utc).isoformat(), "synthetic": True},
        language_info={"primary": {"language": scenario["language"], "confidence": 1.0}},
        transcript=[
            {"text": line, "speaker": "caller", "timestamp": float(i) * 6.0}
            for i, line in enumerate(scenario["lines"])
        ],
    )
    db.add(case)
    db.flush()
    log_action(db, "created", f"Demo preloaded scenario={scenario_id}", case_id=case.id, user_id=user.id)
    apply_analysis(db, case, actor_id=user.id, notify=False)
    db.commit()
    return {"case": serialize_case(case), "scenario": scenario}
