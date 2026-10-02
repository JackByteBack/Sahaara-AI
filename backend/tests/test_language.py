"""Language detection + code-switching (Features 1.3, 2.8, 2.9)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.language import detect_code_switching, detect_language


def test_detect_english():
    d = detect_language("I am scared and I need help right now.")
    assert d["language"] == "en"
    assert d["confidence"] > 0.5


def test_detect_hindi_devanagari():
    d = detect_language("मुझे बहुत डर लग रहा है, मैं उदास हूँ।")
    assert d["language"] == "hi"
    assert d["script"] == "devanagari"


def test_detect_marathi_devanagari():
    d = detect_language("मला भीती वाटते, मला मदत हवी आहे.")
    assert d["language"] == "mr"


def test_detect_bengali_script_expansion():
    d = detect_language("আমি ভয় পাচ্ছি, আমাকে সাহায্য করুন")
    assert d["language"] == "bn"
    assert d["supported"] is False  # research expansion language (Feature 2.8)


def test_code_switching_detected():
    segments = [
        {"text": "Mala khup bhiti vatate", "timestamp": 1.0},
        {"text": "they are threatening me every day", "timestamp": 4.0},
        {"text": "मैं सो नहीं पा रही हूँ", "timestamp": 8.0},
    ]
    result = detect_code_switching(segments)
    assert result["is_code_switched"] is True
    assert len(result["switches"]) >= 1
    assert "en" in result["languages_detected"]
    # switch notes must warn against treating switches as silence (rules.md)
    assert all("silence" in s["note"] for s in result["switches"])


def test_single_language_no_switch():
    segments = [
        {"text": "I need help please", "timestamp": 1.0},
        {"text": "can you hear me", "timestamp": 4.0},
    ]
    result = detect_code_switching(segments)
    assert result["is_code_switched"] is False


def test_empty_text_low_confidence():
    d = detect_language("")
    assert d["confidence"] == 0.0
