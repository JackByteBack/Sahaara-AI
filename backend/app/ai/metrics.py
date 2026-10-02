"""Feature 2.20 — evaluation metrics (pure functions, unit-testable).

Sensitivity/specificity/precision/recall/F1/AUROC/AUPRC plus fairness slicing
by language for Feature 2.24 continuous monitoring.
"""
from __future__ import annotations


def confusion(y_true: list[int], y_pred: list[int]) -> dict:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}


def classification_metrics(y_true: list[int], y_pred: list[int]) -> dict:
    c = confusion(y_true, y_pred)
    tp, tn, fp, fn = c["tp"], c["tn"], c["fp"], c["fn"]
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0  # sensitivity
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        **c,
        "sensitivity": round(recall, 4),
        "specificity": round(specificity, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "false_negative_rate": round(1 - recall, 4) if (tp + fn) else 0.0,
        "false_positive_rate": round(1 - specificity, 4) if (tn + fp) else 0.0,
        "accuracy": round((tp + tn) / max(len(y_true), 1), 4),
    }


def auroc(y_true: list[int], y_scores: list[float]) -> float:
    """Rank-based AUROC (Mann-Whitney U)."""
    pairs = sorted(zip(y_scores, y_true), key=lambda x: x[0])
    pos = [y for _, y in pairs if y == 1]
    neg = [y for _, y in pairs if y == 0]
    n_pos, n_neg = len(pos), len(neg)
    if n_pos == 0 or n_neg == 0:
        return 0.5
    # handle ties by average rank
    ranks = {}
    rank_sum_pos = 0.0
    i = 0
    rank = 1
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        avg_rank = (rank + rank + (j - i) - 1) / 2
        for k in range(i, j):
            if pairs[k][1] == 1:
                rank_sum_pos += avg_rank
        rank += j - i
        i = j
    return round((rank_sum_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg), 4)


def auprc(y_true: list[int], y_scores: list[float]) -> float:
    """Average precision (area under precision-recall curve)."""
    pairs = sorted(zip(y_scores, y_true), key=lambda x: -x[0])
    n_pos = sum(y_true)
    if n_pos == 0:
        return 0.0
    tp = 0
    fp = 0
    ap = 0.0
    prev_recall = 0.0
    for score, y in pairs:
        if y == 1:
            tp += 1
        else:
            fp += 1
        precision = tp / (tp + fp)
        recall = tp / n_pos
        ap += (recall - prev_recall) * precision
        prev_recall = recall
    return round(ap, 4)


def calibration_bins(y_true: list[int], y_scores: list[float], n_bins: int = 5) -> list[dict]:
    """Feature 2.20 — calibration: predicted confidence vs observed rate."""
    bins = []
    size = 1.0 / n_bins
    for b in range(n_bins):
        lo, hi = b * size, (b + 1) * size
        idx = [i for i, s in enumerate(y_scores) if lo <= s < hi or (b == n_bins - 1 and s == 1.0)]
        if not idx:
            bins.append({"bin": [round(lo, 2), round(hi, 2)], "count": 0, "mean_predicted": None, "observed_rate": None})
            continue
        obs = sum(y_true[i] for i in idx) / len(idx)
        mean_pred = sum(y_scores[i] for i in idx) / len(idx)
        bins.append({
            "bin": [round(lo, 2), round(hi, 2)],
            "count": len(idx),
            "mean_predicted": round(mean_pred, 3),
            "observed_rate": round(obs, 3),
        })
    return bins


def fairness_by_subgroup(records: list[dict]) -> dict:
    """records: [{"language": ..., "y_true": int, "y_pred": int, "score": float}] (Feature 2.24)."""
    by_lang: dict[str, list[dict]] = {}
    for r in records:
        by_lang.setdefault(r.get("language", "unknown"), []).append(r)
    report = {}
    for lang, rows in by_lang.items():
        m = classification_metrics([r["y_true"] for r in rows], [r["y_pred"] for r in rows])
        m["high_risk_rate"] = round(sum(r["y_pred"] for r in rows) / len(rows), 4)
        m["n"] = len(rows)
        report[lang] = m
    if len(report) > 1:
        rates = [m["high_risk_rate"] for m in report.values()]
        report["_disparity"] = {
            "max_gap": round(max(rates) - min(rates), 4),
            "note": "Gap in high-risk prediction rate across languages (Feature 2.24 monitoring signal).",
        }
    return report
