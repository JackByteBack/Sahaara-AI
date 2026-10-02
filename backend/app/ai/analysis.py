"""Feature 1.1 (distress assessment), 1.5 (explainable indicators),
2.1/2.2 (Victim Safety & Wellbeing Profile), 2.4 (immediate safety),
2.6 (self-harm pathway), 2.7 (trauma indicators), 2.12 (coercion), 2.11 (context-aware speech).

Deterministic rule engine — always emits evidence-linked, timestamped,
confidence-scored indicators. Never a diagnosis (rules.md §General 2).
"""
from __future__ import annotations

import uuid

from .lexicons import ALL_TERMS, COERCION_TERMS, PAUSE_ALTERNATIVES, DANGER_KEYWORDS

LEVEL_ORDER = {"UNKNOWN": -1, "LOW": 0, "MODERATE": 1, "HIGH": 2, "CRITICAL": 3}


def _flag(category, description, evidence, timestamp, confidence, severity, source="rule_engine", kind="verbal"):
    return {
        "id": uuid.uuid4().hex[:12],
        "category": category,
        "type": kind,
        "description": description,
        "evidence": evidence,
        "transcript_excerpt": evidence,
        "timestamp": timestamp,
        "confidence": round(float(confidence), 2),
        "severity": severity,
        "source": source,
        "model_version": "rules-1.4",
        # Feature 1.6: every flag is a suggestion awaiting human confirmation
        "status": "suggested",
        "human_decision": None,
        "alternatives_considered": [],
    }


def extract_indicators(segments: list[dict], speech_features: dict | None = None) -> list[dict]:
    """Scan transcript segments for observable indicators (Features 1.1, 1.5, 2.4, 2.6, 2.7, 2.12)."""
    flags: list[dict] = []
    speech_features = speech_features or {}

    for seg in segments:
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        low = text.lower()
        ts = seg.get("timestamp", 0.0)

        matched_terms = []
        for term, (category, severity, confidence) in ALL_TERMS.items():
            if term in low:
                matched_terms.append((term, category, severity, confidence))

        for term, category, severity, confidence in matched_terms:
            # Feature 2.11: speech/volume evidence is supporting only, with alternatives listed
            alternatives = []
            if category in ("distress", "trauma"):
                alternatives = PAUSE_ALTERNATIVES.copy()
            flags.append(
                _flag(
                    category=category,
                    description=f"Observable '{category.replace('_', ' ')}' indicator: matched '{term}'",
                    evidence=text,
                    timestamp=ts,
                    confidence=confidence,
                    severity=severity,
                )
            )
            if alternatives:
                flags[-1]["alternatives_considered"] = alternatives

    # Feature 2.12 — Possible coercion/interference (always non-definitive)
    full_text = " ".join((s.get("text") or "") for s in segments).lower()
    for term in COERCION_TERMS:
        if term in full_text:
            flags.append(
                _flag(
                    category="coercion",
                    description="Possible coercion/interference — speaker may not be able to speak freely. Human review required.",
                    evidence=term,
                    timestamp=segments[-1].get("timestamp", 0.0) if segments else 0.0,
                    confidence=0.7,
                    severity="high",
                    kind="contextual",
                )
            )
            break  # one coercion flag is enough

    # Feature 2.4 — immediate safety keywords (explicit danger wording)
    if any(kw in full_text for kw in DANGER_KEYWORDS):
        existing = any(f["category"] == "immediate_danger" for f in flags)
        if not existing:
            flags.append(
                _flag(
                    category="immediate_danger",
                    description="Immediate danger keyword detected in conversation.",
                    evidence=next(kw for kw in DANGER_KEYWORDS if kw in full_text),
                    timestamp=segments[-1].get("timestamp", 0.0) if segments else 0.0,
                    confidence=0.6,
                    severity="high",
                    kind="contextual",
                )
            )

    # Feature 2.4 / 2.11 — acoustic evidence (volume spike / whispering) as supporting context
    volume = speech_features.get("volume")
    if volume is not None:
        if volume > 85:
            flags.append(
                _flag(
                    category="immediate_danger",
                    description="High vocal volume (possible shouting) — supporting evidence only.",
                    evidence=f"volume={volume}dB",
                    timestamp=speech_features.get("timestamp", 0.0),
                    confidence=0.5,
                    severity="medium",
                    kind="non_verbal",
                )
            )
        elif 5 < volume < 20 and full_text:
            flags.append(
                _flag(
                    category="coercion",
                    description="Whispering detected alongside situational wording — possible interference (Feature 2.12).",
                    evidence=f"volume={volume}dB",
                    timestamp=speech_features.get("timestamp", 0.0),
                    confidence=0.55,
                    severity="medium",
                    kind="non_verbal",
                )
            )

    # de-duplicate identical (category, evidence) pairs
    seen = set()
    unique = []
    for f in flags:
        key = (f["category"], f["transcript_excerpt"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    return unique


_SEV_TO_LEVEL = {"low": "LOW", "medium": "MODERATE", "high": "HIGH", "critical": "CRITICAL"}


def _max_level(flags: list[dict], categories: tuple, floor: str = "UNKNOWN") -> str:
    level = floor
    for f in flags:
        if f["category"] in categories:
            lvl = _SEV_TO_LEVEL.get(f.get("severity", ""), "UNKNOWN")
            if LEVEL_ORDER[lvl] > LEVEL_ORDER[level]:
                level = lvl
    return level


def build_victim_safety_profile(flags: list[dict], segments: list[dict]) -> dict:
    """Feature 2.2 — multidimensional Victim Safety & Wellbeing Profile.

    Deliberately separate from ReviewPriorityScore (Decision 1: dual-layer architecture).
    """

    def dim(level, confidence, evidence):
        return {"level": level, "confidence": round(confidence, 2), "evidence": evidence}

    def evidence_for(*cats):
        return [f["transcript_excerpt"] for f in flags if f["category"] in cats][:3]

    distress_ev = evidence_for("distress")
    trauma_ev = evidence_for("trauma")
    danger_ev = evidence_for("immediate_danger")
    selfharm_ev = evidence_for("self_harm")
    coercion_ev = evidence_for("coercion")
    vuln_ev = evidence_for("vulnerability")

    profile = {
        # psychological distress
        "psych_distress": dim(
            _max_level(flags, ("distress",)),
            max([f["confidence"] for f in flags if f["category"] == "distress"], default=0.0),
            distress_ev,
        ),
        # trauma indicators (Feature 2.7 — not a PTSD diagnosis)
        "trauma_indicators": dim(
            _max_level(flags, ("trauma",)),
            max([f["confidence"] for f in flags if f["category"] == "trauma"], default=0.0),
            trauma_ev,
        ),
        # immediate physical danger (Feature 2.4)
        "immediate_danger": dim(
            _max_level(flags, ("immediate_danger",)),
            max([f["confidence"] for f in flags if f["category"] == "immediate_danger"], default=0.0),
            danger_ev,
        ),
        # self-harm / suicide concern (Feature 2.6)
        "self_harm": dim(
            _max_level(flags, ("self_harm",)),
            max([f["confidence"] for f in flags if f["category"] == "self_harm"], default=0.0),
            selfharm_ev,
        ),
        # intimidation / possible coercion (Feature 2.12 — "POSSIBLE", never definitive)
        "intimidation_coercion": (
            dim("POSSIBLE", 0.7, coercion_ev) if coercion_ev else dim("UNKNOWN", 0.0, [])
        ),
        # social / medical / legal vulnerability
        "social_vulnerability": dim(
            "MODERATE" if vuln_ev else "UNKNOWN",
            0.6 if vuln_ev else 0.0,
            vuln_ev,
        ),
        "medical_vulnerability": dim("UNKNOWN", 0.0, []),
        "legal_service_vulnerability": dim(
            "HIGH" if any(f["category"] == "immediate_danger" for f in flags) else "UNKNOWN",
            0.65 if danger_ev else 0.0,
            danger_ev,
        ),
        # Feature 2.10 evidence quality inputs
        "assessed_dimensions": [
            "psych_distress", "trauma_indicators", "immediate_danger",
            "self_harm", "intimidation_coercion", "social_vulnerability",
            "medical_vulnerability", "legal_service_vulnerability",
        ],
        "note": "Analytical profile for support planning — not a clinical or psychological measurement.",
    }
    return profile


def compute_uncertainty(flags: list[dict], profile: dict) -> dict:
    """Feature 2.10 — uncertainty-aware assessment with the ability to abstain."""
    if not flags:
        return {
            "assessment_confidence": 0.35,
            "evidence_quality": "LOW",
            "missing_information": [
                "No indicators detected in available transcript",
                "Immediate safety not established",
            ],
            "recommended_action": "HUMAN_ASSESSMENT_REQUIRED",
            "abstain": True,
        }

    avg_conf = sum(f["confidence"] for f in flags) / len(flags)
    missing = []
    if profile.get("immediate_danger", {}).get("level") in ("UNKNOWN", "LOW"):
        missing.append("Immediate safety not established")
    if profile.get("medical_vulnerability", {}).get("level") == "UNKNOWN":
        missing.append("Medical situation unknown")
    if profile.get("social_vulnerability", {}).get("level") == "UNKNOWN":
        missing.append("Support network / social context unknown")

    quality = "HIGH" if avg_conf >= 0.8 and not missing else "MODERATE" if avg_conf >= 0.6 else "LOW"
    confidence = round(min(avg_conf, 0.95) * (1 - 0.1 * len(missing)), 2)
    abstain = quality == "LOW"

    return {
        "assessment_confidence": confidence,
        "evidence_quality": quality,
        "missing_information": missing,
        "recommended_action": "HUMAN_ASSESSMENT_REQUIRED" if not abstain else "ABSTAIN_HUMAN_ASSESSMENT",
        "abstain": abstain,
    }
