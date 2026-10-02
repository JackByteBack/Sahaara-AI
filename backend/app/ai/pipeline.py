"""End-to-end analysis pipeline (architecture.md §Data Flow steps 2–4).

Input: transcript segments (+ optional speech features)
Output: language info, flags, victim safety profile, review priority,
        uncertainty, mode (AI or Human Assessment Mode — Feature 1.14)
"""
from __future__ import annotations

from .analysis import build_victim_safety_profile, compute_uncertainty, extract_indicators
from .language import detect_code_switching, detect_language
from .priority import calculate_review_priority
from .llm import ai_available


def analyze(segments: list[dict], speech_features: dict | None = None, trauma_mode: bool = False) -> dict:
    text = "\n".join((s.get("text") or "").strip() for s in segments if (s.get("text") or "").strip())

    # Feature 1.3 / 2.9 — language + code-switching (runs even without generative AI)
    code_switch = detect_code_switching(segments)
    primary = detect_language(text)
    language_info = {
        "primary": primary,
        "code_switching": {
            "is_code_switched": code_switch["is_code_switched"],
            "switches": code_switch["switches"],
            "languages_detected": code_switch["languages_detected"],
        },
        "segments": code_switch["segments"],
        "operator_override": None,
    }

    # Feature 1.1 / 1.5 — explainable indicators
    flags = extract_indicators(segments, speech_features)

    # Feature 2.2 — multidimensional profile
    profile = build_victim_safety_profile(flags, segments)

    # Feature 1.4 + 2.5 — weighted priority with safety override
    score, override, reason = calculate_review_priority(text, flags, profile, speech_features)

    # Feature 2.10 — uncertainty / abstention
    uncertainty = compute_uncertainty(flags, profile)
    if override:
        # A deterministic safety rule firing raises certainty (capped at 0.95)
        uncertainty["assessment_confidence"] = round(
            min(uncertainty["assessment_confidence"] + 0.15, 0.95), 2
        )

    # Feature 1.14 — mode: generative AI unavailable => Human Assessment Mode
    mode = "ai_assisted" if ai_available() else "human_assessment"

    return {
        "language_info": language_info,
        "flags": flags,
        "victim_safety_profile": profile,
        "review_priority_score": score,
        "safety_override": override,
        "safety_override_reason": reason,
        "uncertainty": uncertainty,
        "mode": mode,
        "trauma_mode": trauma_mode,
        "transcript_text": text,
    }
