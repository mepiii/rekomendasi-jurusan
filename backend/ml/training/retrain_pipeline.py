# Purpose: Run Apti v2 generation, training, evaluation, and promotion decision in sequence.
# Callers: Manual retraining and future feedback loop.
# Deps: argparse, subprocess, sys, pathlib.
# API: main CLI.
# Side effects: Regenerates dataset, artifacts, reports.

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _run(args: list[str]) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5000)
    parser.add_argument("--version", default="apti_dataset_v2")
    parser.add_argument("--model-version", default="apti_v2")
    args = parser.parse_args()
    _run(["backend/ml/data_generation/generate_synthetic_dataset.py", "--n", str(args.n), "--version", args.version])
    _run(["backend/ml/training/train_model.py", "--dataset", "backend/ml/data/processed/apti_training_v2.csv", "--model-version", args.model_version])
    _run(["backend/ml/training/evaluate_model.py", "--dataset", "backend/ml/data/processed/apti_training_v2.csv", "--model-version", args.model_version])
    _run(["backend/ml/training/promote_model.py"])
