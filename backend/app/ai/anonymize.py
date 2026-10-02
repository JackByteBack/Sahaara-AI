"""Feature 1.10 — anonymization / data minimization on case closure."""
from __future__ import annotations

import re

PHONE_RE = re.compile(r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}")
LOCATION_RE = re.compile(r"\b(Street|Road|Lane|District|Colony|Nagar|Marg|City|State)\b", re.IGNORECASE)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def anonymize_transcript(transcript_text: str, case_data: dict | None = None) -> str:
    """Replace PII with placeholders. Uses regex (production note: swap in NER)."""
    case_data = case_data or {}
    text = transcript_text or ""

    victim_name = (case_data.get("victim_name") or "").strip()
    if victim_name:
        pattern = r"\b" + re.escape(victim_name) + r"\b"
        text = re.sub(pattern, "[Name Redacted]", text, flags=re.IGNORECASE)

    other_names = case_data.get("other_names") or []
    for name in other_names:
        name = name.strip()
        if name:
            text = re.sub(r"\b" + re.escape(name) + r"\b", "[Name Redacted]", text, flags=re.IGNORECASE)

    text = PHONE_RE.sub("[Phone Number Redacted]", text)
    text = EMAIL_RE.sub("[Email Redacted]", text)
    text = LOCATION_RE.sub("[Location]", text)
    return text


def anonymize_case(case, extra_names: list[str] | None = None) -> dict:
    """Scrub a case in place: transcript PII, notes, identifiers kept only as case number."""
    names = [n for n in (extra_names or []) if n]
    case.transcript = [
        {**seg, "text": anonymize_transcript(seg.get("text", ""), {"other_names": names})}
        for seg in (case.transcript or [])
    ]
    case.notes = [
        {**note, "body": anonymize_transcript(note.get("body", ""), {"other_names": names})}
        for note in (case.notes or [])
    ]
    if case.summary:
        vs = dict(case.summary.get("verbatim_summary") or {})  # copy — JSON change tracking
        if vs.get("user_statement"):
            vs["user_statement"] = anonymize_transcript(vs["user_statement"], {"other_names": names})
        case.summary = {**case.summary, "verbatim_summary": vs}
    case.anonymized = True
    # Consent record retained (audit requirement) but personal fields dropped
    if case.consent:
        case.consent = {
            "given": case.consent.get("given", False),
            "given_at": case.consent.get("given_at"),
            "scope": case.consent.get("scope", "processing"),
            "person_identifiers_removed": True,
        }
    return case
