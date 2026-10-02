"""Feature 1.4 (Review Priority Score) + Feature 2.5 (Safety Override Engine).

Naming is deliberate per ai/instructions.md: `ReviewPriorityScore` measures how
urgently a *human* should review the case — it is never a clinical measurement.
Safety rules take precedence over the weighted score.
"""
from __future__ import annotations

NEGATIVE_WORDS = [
    "sad", "scared", "afraid", "hate", "abuse", "hurt", "hopeless", "alone",
    "crying", "terrified", "worthless", "danger", "threat",
    "डर", "उदास", "दुख", "हिंसा",
    "भीती", "रड", "दुःख",
    "dar", "dukh", "hate",
]


def calculate_review_priority(
    transcript_text: str,
    flags: list[dict],
    profile: dict,
    speech_features: dict | None = None,
) -> tuple[float, bool, str]:
    """Returns (score 0..1, safety_override_triggered, override_reason)."""
    speech_features = speech_features or {}
    text = (transcript_text or "").lower()

    # 1. Linguistic indicators (20%)
    negative_hits = sum(1 for w in NEGATIVE_WORDS if w in text)
    score = min(negative_hits * 0.05, 0.20)

    # 2. Contextual indicators (30%) — conversation length/detail
    score += min(len(transcript_text or "") / 1000 * 0.1, 0.15)
    # sentiment density bonus within contextual budget
    if text:
        score += min(negative_hits / max(len(text.split()), 1) * 0.6, 0.15)

    # 3. Conversation indicators (30%) — AI flags detected
    if flags:
        score += min(len(flags) * 0.1, 0.30)
        high = sum(1 for f in flags if f["severity"] in ("high", "critical"))
        score += min(high * 0.05, 0.10)

    # 4. Speech indicators (20%) — observable proxies only (Feature 2.11)
    volume = speech_features.get("volume")
    if volume is not None:
        if volume > 85 or (5 < volume < 20):
            score += 0.10
    long_pauses = speech_features.get("long_pause_count", 0)
    if long_pauses:
        # Supporting evidence only — alternatives are recorded on the flags
        score += min(long_pauses * 0.02, 0.06)

    score = round(min(max(score, 0.0), 1.0), 2)

    # ── Feature 2.5: Safety Override — rules beat the weighted average ──
    override, reason = safety_override(profile, flags, volume)
    if override:
        return 1.0 if reason.startswith("CRITICAL") else float(_override_score(reason)), True, reason
    return score, False, ""


def _override_score(reason: str) -> float:
    if reason.startswith("HIGH"):
        return 1.0
    if reason.startswith("COERCION"):
        return 0.9
    return 0.85


def safety_override(profile: dict, flags: list[dict], volume: float | None = None) -> tuple[bool, str]:
    """Explicit safety rules (Feature 2.5) — a critical signal must never be hidden by a lower score."""
    danger = (profile.get("immediate_danger") or {}).get("level", "UNKNOWN")
    self_harm = (profile.get("self_harm") or {}).get("level", "UNKNOWN")
    coercion = (profile.get("intimidation_coercion") or {}).get("level", "UNKNOWN")

    if danger in ("CRITICAL", "HIGH"):
        return True, f"CRITICAL: immediate physical threat detected (level={danger})"
    if self_harm in ("CRITICAL", "HIGH"):
        return True, f"HIGH: self-harm/suicide-risk indicator (level={self_harm})"
    if coercion == "POSSIBLE":
        # docs/rules.md §Review Priorities 3: coercion => high priority + immediate human review
        return True, "COERCION: possible coercion/interference requires immediate human review"
    if volume is not None and volume > 90:
        return True, "HIGH: volume spike consistent with shouting/ongoing violence"
    return False, ""


def queue_position(case) -> int:
    """Safety-override cases always sit at the top of the review queue (rules.md §Review 2)."""
    return 0 if case.safety_override else 1
