"""Unit tests — Safety Override must beat the weighted priority score (test-plan.md)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.priority import calculate_review_priority, safety_override


def test_safety_override_forces_critical():
    profile = {"immediate_danger": {"level": "CRITICAL"}, "self_harm": {"level": "UNKNOWN"},
               "intimidation_coercion": {"level": "UNKNOWN"}}
    score, override, reason = calculate_review_priority("we talked about dinner", [], profile)
    assert override is True
    assert score == 1.0
    assert "CRITICAL" in reason


def test_moderate_distress_with_immediate_danger_is_overridden():
    """Spec scenario: overall distress MODERATE + immediate threat YES → override (Feature 2.5)."""
    profile = {"immediate_danger": {"level": "HIGH"}, "self_harm": {"level": "LOW"},
               "intimidation_coercion": {"level": "UNKNOWN"}}
    flags = [{"severity": "medium", "category": "distress", "confidence": 0.6}]
    score, override, reason = calculate_review_priority("I am sad", flags, profile)
    assert override is True
    assert score == 1.0


def test_coercion_triggers_high_priority():
    profile = {"immediate_danger": {"level": "UNKNOWN"}, "self_harm": {"level": "UNKNOWN"},
               "intimidation_coercion": {"level": "POSSIBLE"}}
    score, override, reason = calculate_review_priority("", [], profile)
    assert override is True
    assert score == 0.9
    assert "COERCION" in reason


def test_normal_case_no_override():
    profile = {"immediate_danger": {"level": "LOW"}, "self_harm": {"level": "LOW"},
               "intimidation_coercion": {"level": "UNKNOWN"}}
    flags = [{"severity": "low", "category": "distress", "confidence": 0.5}]
    score, override, _ = calculate_review_priority("I am a little sad today", flags, profile)
    assert override is False
    assert 0.0 <= score <= 1.0


def test_score_clamped_between_zero_and_one():
    profile = {"immediate_danger": {"level": "UNKNOWN"}, "self_harm": {"level": "UNKNOWN"},
               "intimidation_coercion": {"level": "UNKNOWN"}}
    huge_text = "sad scared hurt " * 500
    flags = [{"severity": "critical", "category": "x", "confidence": 0.9}] * 50
    score, _, _ = calculate_review_priority(huge_text, flags, profile)
    assert 0.0 <= score <= 1.0


def test_safety_override_helper_returns_false_for_safe_profile():
    profile = {"immediate_danger": {"level": "LOW"}, "self_harm": {"level": "LOW"},
               "intimidation_coercion": {"level": "UNKNOWN"}}
    assert safety_override(profile, []) == (False, "")
