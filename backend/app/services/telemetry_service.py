# Purpose: Collect model telemetry, latency stats, drift checks, and fairness proxy metrics.
# Callers: API routes and /metrics endpoint.
# Deps: app.core.db and app.config.
# API: compute_bias_score, compute_drift_score, snapshot_metrics.
# Side effects: None.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config import settings
from app.core.db import fetch_metrics_snapshot

TRACK_STEM_BIAS = {
    "IPA": 0.55,
    "IPS": 0.30,
    "Bahasa": 0.15,
}


@dataclass
class DriftResult:
    score: float
    alerted: bool


def compute_bias_score(sma_track: str, top_major_cluster: str) -> float:
    expected = TRACK_STEM_BIAS.get(sma_track, 0.33)
    if top_major_cluster != "STEM":
        return 0.0
    return round(max(0.0, 1.0 - expected), 4)


def compute_drift_score(features: dict[str, Any]) -> DriftResult:
    subject_keys = ["math", "physics", "chemistry", "biology", "economics", "indonesian", "english"]
    values = [float(features.get(key, 0.0)) for key in subject_keys]
    if not values:
        return DriftResult(score=0.0, alerted=False)

    mean_score = sum(values) / len(values)
    drift = abs(mean_score - 75.0)
    return DriftResult(score=round(drift, 2), alerted=drift >= settings.drift_alert_threshold)


def snapshot_metrics(model_version: str) -> dict[str, float | int | str]:
    snap = fetch_metrics_snapshot()
    return {
        "model_version": model_version,
        "total_predictions": int(snap.get("total_predictions", 0)),
        "avg_latency_ms": float(snap.get("avg_latency_ms", 0.0)),
        "bias_score": float(snap.get("bias_score", 0.0)),
        "accuracy": float(snap.get("accuracy", 0.0)),
    }
