"""Operational analytics (Feature 1.12)."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require
from ..models import Case, User

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


def _duration_category(seconds: float) -> str:
    if seconds < 300:
        return "<5 min"
    if seconds < 900:
        return "5-15 min"
    if seconds < 1800:
        return "15-30 min"
    return ">30 min"


@router.get("/overview")
def overview(db: Session = Depends(get_db), user: User = Depends(require("analytics_read"))):
    cases = db.query(Case).all()
    now = datetime.now(timezone.utc)

    cases_by_day: dict[str, int] = defaultdict(int)
    for c in cases:
        if c.created_at:
            cases_by_day[c.created_at.date().isoformat()] += 1

    language_dist: Counter = Counter()
    priority_dist = {"critical (0.9-1.0)": 0, "high (0.7-0.9)": 0, "medium (0.4-0.7)": 0, "low (0-0.4)": 0}
    escalations = 0
    human_decisions: Counter = Counter()
    ai_vs_human = {"ai_recommended": 0, "human_confirmed": 0, "human_overrode": 0}
    durations: Counter = Counter()
    demo_count = 0
    override_count = 0

    for c in cases:
        lang = ((c.language_info or {}).get("primary") or {}).get("language", "unknown")
        language_dist[lang] += 1
        s = c.review_priority_score
        if s >= 0.9:
            priority_dist["critical (0.9-1.0)"] += 1
        elif s >= 0.7:
            priority_dist["high (0.7-0.9)"] += 1
        elif s >= 0.4:
            priority_dist["medium (0.4-0.7)"] += 1
        else:
            priority_dist["low (0-0.4)"] += 1

        if c.final_decision:
            human_decisions[c.final_decision.get("decision", "unknown")] += 1
            if c.final_decision.get("override_ai"):
                ai_vs_human["human_overrode"] += 1
            elif c.final_decision.get("decision") == "confirm":
                ai_vs_human["human_confirmed"] += 1
            if c.final_decision.get("decision") == "escalate":
                escalations += 1
        if c.status == "referred":
            escalations += 1
        if c.is_demo:
            demo_count += 1
        if c.safety_override:
            override_count += 1
        if c.created_at and c.updated_at:
            durations[_duration_category((c.updated_at - c.created_at).total_seconds())] += 1

    trend: Counter = Counter()
    for c in cases:
        if c.final_decision and c.final_decision.get("decision") == "escalate" and c.created_at:
            trend[c.created_at.date().isoformat()] += 1

    return {
        "total_cases": len(cases),
        "cases_last_7_days": sum(v for k, v in cases_by_day.items()
                                 if k >= (now - timedelta(days=7)).date().isoformat()),
        "cases_by_day": dict(sorted(cases_by_day.items())),
        "language_distribution": dict(language_dist),
        "priority_distribution": priority_dist,
        "escalation_trends": dict(sorted(trend.items())),
        "duration_categories": dict(durations),
        "ai_vs_human_decisions": {**ai_vs_human, "by_decision": dict(human_decisions)},
        "demonstration_data_usage": demo_count,
        "safety_override_cases": override_count,
        "status_distribution": dict(Counter(c.status for c in cases)),
        "notes": "Operational metrics only — no clinical interpretation (Feature 1.12).",
    }


@router.get("/languages")
def language_performance(db: Session = Depends(get_db), user: User = Depends(require("analytics_read"))):
    """Feature 2.24 — monitor performance disparities across languages."""
    cases = db.query(Case).all()
    stats: dict[str, dict] = defaultdict(lambda: {"cases": 0, "avg_priority": 0.0, "overrides": 0, "confirmed": 0})
    for c in cases:
        lang = ((c.language_info or {}).get("primary") or {}).get("language", "unknown")
        stats[lang]["cases"] += 1
        stats[lang]["avg_priority"] += c.review_priority_score
        stats[lang]["overrides"] += 1 if c.safety_override else 0
        if c.final_decision and c.final_decision.get("decision") == "confirm":
            stats[lang]["confirmed"] += 1
    for lang, s in stats.items():
        s["avg_priority"] = round(s["avg_priority"] / max(s["cases"], 1), 3)
    return {"languages": dict(stats)}
