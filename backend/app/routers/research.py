"""Research evaluation endpoints (Features 2.20, 2.21, 2.24).

AI advisory only — metrics support research monitoring, never automated decisions.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..ai.metrics import (
    auprc,
    auroc,
    calibration_bins,
    classification_metrics,
    fairness_by_subgroup,
)
from ..database import get_db
from ..deps import require
from ..models import User

router = APIRouter(prefix="/api/v1/research", tags=["research"])


class EvalRecord(BaseModel):
    y_true: int = Field(ge=0, le=1)
    y_pred: int = Field(ge=0, le=1)
    score: float = Field(ge=0.0, le=1.0)
    language: str = "unknown"


class EvalRequest(BaseModel):
    records: list[EvalRecord]


# In-memory research monitor (build/dedicated-ai-research.js → ResearchMonitor)
_MONITOR: list[dict] = []


class MonitorIn(BaseModel):
    case_id: str
    language: str
    predicted_risk: str
    actual_risk: str | None = None


@router.post("/evaluate")
def evaluate(body: EvalRequest, user: User = Depends(require("analytics_read"))):
    """Feature 2.20 — sensitivity, specificity, precision, recall, F1, AUROC, AUPRC, calibration + fairness."""
    y_true = [r.y_true for r in body.records]
    y_pred = [r.y_pred for r in body.records]
    scores = [r.score for r in body.records]
    base = classification_metrics(y_true, y_pred)
    return {
        "n": len(y_true),
        **base,
        "auroc": auroc(y_true, scores),
        "auprc": auprc(y_true, scores),
        "calibration": calibration_bins(y_true, scores),
        "fairness_by_language": fairness_by_subgroup([r.model_dump() for r in body.records]),
        "disclaimer": "Research metrics (Feature 2.20). Not a clinical validation claim.",
    }


@router.post("/monitor")
def log_prediction(body: MonitorIn, user: User = Depends(require("analytics_read"))):
    _MONITOR.append({**body.model_dump()})
    return {"ok": True, "logged": len(_MONITOR)}


@router.get("/monitor")
def monitor_summary(user: User = Depends(require("analytics_read"))):
    """Feature 2.24 — drift/disparity signals: high-risk rate by language + override rates."""
    if not _MONITOR:
        return {"predictions": 0, "by_language": {}}
    by_lang: dict[str, list[dict]] = {}
    for m in _MONITOR:
        by_lang.setdefault(m["language"], []).append(m)
    out = {}
    for lang, rows in by_lang.items():
        high = sum(1 for r in rows if r["predicted_risk"] in ("HIGH", "CRITICAL"))
        labelled = [r for r in rows if r["actual_risk"]]
        fn = sum(1 for r in labelled if r["predicted_risk"] in ("LOW", "MODERATE") and r["actual_risk"] in ("HIGH", "CRITICAL"))
        out[lang] = {
            "n": len(rows),
            "high_risk_rate": round(high / len(rows), 3),
            "labelled": len(labelled),
            "false_negatives": fn,
        }
    rates = [v["high_risk_rate"] for v in out.values()]
    return {
        "predictions": len(_MONITOR),
        "by_language": out,
        "disparity_max_gap": round(max(rates) - min(rates), 3) if len(rates) > 1 else 0.0,
    }
