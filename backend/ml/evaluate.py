# Purpose: Evaluate Apti model readiness without replacing production artifacts.
# Callers: Manual CLI, backend regression tests, release checks.
# Deps: argparse, json, pathlib, pandas optional via train pipeline.
# API: evaluate_readiness, main.
# Side effects: Optionally writes JSON metrics report.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT_DIR / "ml" / "data" / "training_dataset.csv"
DEFAULT_MODEL = ROOT_DIR / "ml" / "models" / "rf_v1.0.pkl"
DEFAULT_ENCODER = ROOT_DIR / "ml" / "models" / "label_encoder.pkl"
DEFAULT_REPORT = ROOT_DIR / "ml" / "data" / "metrics" / "evaluation_report.json"
MIN_TOP1_ACCURACY = 0.60
MIN_TOP5_ACCURACY = 0.90


def _artifact_status(path: Path) -> dict[str, Any]:
    return {"path": str(path), "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0}


def _dataset_summary(dataset_path: Path) -> dict[str, Any]:
    if not dataset_path.exists():
        return {"exists": False, "rows": 0, "labels": 0}
    import pandas as pd

    frame = pd.read_csv(dataset_path)
    label_column = "kelompok_prodi" if "kelompok_prodi" in frame.columns else "major" if "major" in frame.columns else None
    return {
        "exists": True,
        "rows": int(len(frame)),
        "labels": int(frame[label_column].nunique()) if label_column else 0,
        "label_column": label_column,
        "has_semester_features": any(column.startswith("s1_") or column.endswith("_trend") for column in frame.columns),
    }


def evaluate_readiness(dataset_path: Path = DEFAULT_DATASET, model_path: Path = DEFAULT_MODEL, encoder_path: Path = DEFAULT_ENCODER) -> dict[str, Any]:
    dataset = _dataset_summary(dataset_path)
    artifacts = {"model": _artifact_status(model_path), "encoder": _artifact_status(encoder_path)}
    metrics = {"top1_accuracy": None, "top5_accuracy": None, "macro_f1": None}
    gates = {
        "dataset_present": dataset["exists"],
        "model_artifacts_present": artifacts["model"]["exists"] and artifacts["encoder"]["exists"],
        "metrics_present": False,
        "metrics_pass": False,
        "production_swap_allowed": False,
    }
    return {
        "version": "apti_evaluation_gate_v1",
        "status": "blocked" if not gates["production_swap_allowed"] else "passed",
        "dataset": dataset,
        "artifacts": artifacts,
        "thresholds": {"top1_accuracy": MIN_TOP1_ACCURACY, "top5_accuracy": MIN_TOP5_ACCURACY},
        "metrics": metrics,
        "gates": gates,
        "recommendation": "Keep current production model/fallback. Train/evaluate v3 before artifact swap.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Apti model readiness gate")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--encoder", type=Path, default=DEFAULT_ENCODER)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--write-report", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = evaluate_readiness(args.dataset, args.model, args.encoder)
    if args.write_report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
