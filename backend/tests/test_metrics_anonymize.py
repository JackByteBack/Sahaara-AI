"""Anonymization (Feature 1.10) + evaluation metrics (Feature 2.20)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.anonymize import anonymize_transcript
from app.ai.metrics import auprc, auroc, classification_metrics, fairness_by_subgroup


def test_name_redacted():
    out = anonymize_transcript("My name is Priya Sharma and I need help.", {"other_names": ["Priya Sharma"]})
    assert "Priya Sharma" not in out
    assert "[Name Redacted]" in out


def test_phone_number_redacted():
    out = anonymize_transcript("Call me at 98765 43210 or +91 9876543210.")
    assert "98765" not in out
    assert "[Phone Number Redacted]" in out


def test_location_redacted():
    out = anonymize_transcript("I live on MG Road in Pune District.")
    assert "[Location]" in out


def test_case_insensitive_name_match():
    out = anonymize_transcript("PRIYA needs help", {"other_names": ["priya"]})
    assert "PRIYA" not in out.upper().replace("[NAME REDACTED]", "")


def test_classification_metrics_perfect():
    m = classification_metrics([1, 1, 0, 0], [1, 1, 0, 0])
    assert m["sensitivity"] == 1.0
    assert m["specificity"] == 1.0
    assert m["f1"] == 1.0
    assert m["accuracy"] == 1.0


def test_metrics_missed_high_risk_case():
    # missed high-risk case → false negative (safety-critical metric, Feature 2.20)
    m = classification_metrics([1, 1], [0, 1])
    assert m["fn"] == 1
    assert m["false_negative_rate"] == 0.5
    assert m["recall"] == 0.5


def test_auroc_perfect_separation():
    assert auroc([1, 1, 0, 0], [0.9, 0.8, 0.2, 0.1]) == 1.0


def test_auroc_random_baseline():
    assert auroc([1, 0], [0.5, 0.5]) == 0.5


def test_auprc_range():
    assert 0.0 <= auprc([1, 0, 1, 0], [0.9, 0.8, 0.4, 0.2]) <= 1.0


def test_fairness_disparity_reported():
    records = (
        [{"language": "en", "y_true": 1, "y_pred": 1, "score": 0.9}] * 5
        + [{"language": "mr", "y_true": 1, "y_pred": 0, "score": 0.3}] * 5
    )
    report = fairness_by_subgroup(records)
    assert report["en"]["high_risk_rate"] == 1.0
    assert report["mr"]["high_risk_rate"] == 0.0
    assert report["_disparity"]["max_gap"] == 1.0
