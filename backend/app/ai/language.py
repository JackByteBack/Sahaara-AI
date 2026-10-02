"""Feature 1.3 (language detection) + Feature 2.9 (code-switching).

Deterministic, dependency-free detection so the pipeline keeps working when
external AI providers are unavailable (Feature 1.14). Research expansion
languages (Feature 2.8) are detected at the script level.
"""
from __future__ import annotations

import re

# Devanagari: distinguish Hindi vs Marathi with function-word cues
_MR_CUES = ["मला", "आहे", "आहेस", "नाही", "नाहीस", "करतो", "करते", "काय", "कसा", "कशी",
            "तुम्ही", "तुमचा", "माझ", "इथे", "तिथे", "झाले", "होते", "सांगू", "मदत"]
_HI_CUES = ["मैं", "हूँ", "हूं", "क्या", "कैसे", "क्यों", "तुम", "आप", "मेरा", "मेरी",
            "वह", "यह", "है", "रहा", "रही", "बताओ", "मदद"]

_LATIN_STOPWORDS = {
    "the", "i", "am", "is", "are", "to", "and", "of", "my", "me", "you", "he", "she",
    "they", "we", "it", "in", "on", "at", "have", "has", "was", "were", "not", "no",
    "help", "please", "can", "don't", "cannot", "can't", "here", "there", "this", "that",
    "because", "with", "for", "from", "but", "all", "would", "should", "about", "scared",
}

# Romanized Hindi/Marathi markers in Latin script (Feature 2.9 code-switching)
_ROMAN_HI_MR_CUES = {
    "mujhe", "hai", "hai.", "kya", "kaise", "kyun", "madad", "dar", "raha", "rahi",
    "tum", "aap", "mera", "meri", "nahi", "nahi.", "kar", "sakte", "bhai", "bola",
    "mala", "vate", "aahe", "karun", "tumcha", "majhi", "itha", "kay", "mhanto",
}

_SCRIPT_PATTERNS = {
    "bn": re.compile(r"[\u0980-\u09FF]"),
    "ta": re.compile(r"[\u0B80-\u0BFF]"),
    "te": re.compile(r"[\u0C00-\u0C7F]"),
    "kn": re.compile(r"[\u0C80-\u0CFF]"),
    "ml": re.compile(r"[\u0D00-\u0D7F]"),
    "gu": re.compile(r"[\u0A80-\u0AFF]"),
    "pa": re.compile(r"[\u0A00-\u0A7F]"),
    "or": re.compile(r"[\u0B00-\u0B7F]"),
    "ur": re.compile(r"[\u0600-\u06FF]"),
}

SUPPORTED_CORE = {"en", "hi", "mr"}
SUPPORTED_RESEARCH = {"bn", "ta", "te", "kn", "ml", "gu", "pa", "or"}  # Feature 2.8 expansion


def _has_devanagari(text: str) -> bool:
    return bool(re.search(r"[\u0900-\u097F]", text))


def detect_language(text: str) -> dict:
    """Return {language, confidence, script, supported, method}."""
    text = (text or "").strip()
    if not text:
        return {"language": "en", "confidence": 0.0, "script": "latin", "supported": True, "method": "empty"}

    for lang, pattern in _SCRIPT_PATTERNS.items():
        hits = len(pattern.findall(text))
        if hits >= 3:
            ratio = hits / max(len(text), 1)
            return {
                "language": lang,
                "confidence": round(min(0.6 + ratio * 4, 0.97), 2),
                "script": lang,
                "supported": lang in SUPPORTED_CORE,
                "method": "script",
            }

    if _has_devanagari(text):
        mr_hits = sum(text.count(cue) for cue in _MR_CUES)
        hi_hits = sum(text.count(cue) for cue in _HI_CUES)
        if mr_hits > hi_hits:
            return {"language": "mr", "confidence": min(0.6 + mr_hits * 0.08, 0.95), "script": "devanagari", "supported": True, "method": "lexicon"}
        if hi_hits > 0:
            return {"language": "hi", "confidence": min(0.6 + hi_hits * 0.08, 0.95), "script": "devanagari", "supported": True, "method": "lexicon"}
        # Devanagari but no cue match (Feature 1.3 default: report low confidence)
        return {"language": "hi", "confidence": 0.5, "script": "devanagari", "supported": True, "method": "script-fallback"}

    words = re.findall(r"[a-zA-Z']+", text.lower())
    if not words:
        return {"language": "en", "confidence": 0.4, "script": "unknown", "supported": True, "method": "fallback"}
    stop_hits = sum(1 for w in words if w in _LATIN_STOPWORDS)
    roman_hits = sum(1 for w in words if w in _ROMAN_HI_MR_CUES)
    if roman_hits > stop_hits:
        # Romanized Hindi/Marathi (Feature 2.8) — low-ish confidence, mark unsupported script
        return {"language": "hi" if roman_hits else "en", "confidence": 0.55, "script": "latin-romanized", "supported": True, "method": "romanized-cues"}
    ratio = stop_hits / len(words)
    return {
        "language": "en",
        "confidence": round(min(0.5 + ratio * 0.6, 0.96), 2),
        "script": "latin",
        "supported": True,
        "method": "stopwords",
    }


def detect_code_switching(segments: list[dict]) -> dict:
    """Feature 2.9 — compare adjacent segments; retain original wording + ASR confidence.

    segments: [{"text": ..., "timestamp": ...}]
    """
    switches: list[dict] = []
    processed: list[dict] = []
    prev_lang = None
    for seg in segments:
        detection = detect_language(seg.get("text", ""))
        entry = {
            "text": seg.get("text", ""),
            "timestamp": seg.get("timestamp"),
            "language": detection["language"],
            "confidence": detection["confidence"],
        }
        if prev_lang and prev_lang != detection["language"]:
            entry["switch_point"] = True
            switches.append({
                "at_timestamp": seg.get("timestamp"),
                "from": prev_lang,
                "to": detection["language"],
                # Rule docs/rules.md §Multilingual 1: a mid-sentence switch is not "silence"
                "note": "Language switch mid-conversation — do not treat as pause/silence.",
            })
        prev_lang = detection["language"]
        processed.append(entry)

    langs = sorted({p["language"] for p in processed})
    return {
        "is_code_switched": len(switches) > 1 or (len(langs) > 1),
        "segments": processed,
        "switches": switches,
        "languages_detected": langs,
        "primary_language": langs[0] if langs else "en",
    }
