# Purpose: Generate Apti synthetic dataset v2 from cleaned prodi profile matrix.
# Callers: Training pipeline and manual data refresh commands.
# Deps: argparse, csv, json, pathlib, local simulator/sampler.
# API: generate_dataset.
# Side effects: Writes synthetic CSV, processed CSV, and dataset card JSON.

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from label_sampler import LabelSampler
from noise_config import RANDOM_STATE
from profile_simulator import ProfileSimulator

REPO_ROOT = Path(__file__).resolve().parents[3]
PROFILE_PATH = REPO_ROOT / "backend" / "ml" / "config" / "prodi_profiles.json"
SYNTHETIC_PATH = REPO_ROOT / "backend" / "ml" / "data" / "synthetic" / "apti_synthetic_profiles_v2.csv"
PROCESSED_PATH = REPO_ROOT / "backend" / "ml" / "data" / "processed" / "apti_training_v2.csv"
DATASET_CARD_PATH = REPO_ROOT / "backend" / "ml" / "data" / "metadata" / "apti_dataset_card_v2.json"


def _read_profiles() -> list[dict[str, Any]]:
    data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    return list(data["profiles"])


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _dataset_card(rows: list[dict[str, Any]], version: str) -> dict[str, Any]:
    label_counts: dict[str, int] = {}
    group_counts: dict[str, int] = {}
    for row in rows:
        label_counts[row["target_prodi"]] = label_counts.get(row["target_prodi"], 0) + 1
        group_counts[row["target_kelompok_prodi"]] = group_counts.get(row["target_kelompok_prodi"], 0) + 1
    return {
        "dataset_version": version,
        "row_count": len(rows),
        "source_type": "synthetic_v2_from_catalog_profiles",
        "random_state": RANDOM_STATE,
        "synthetic_real_ratio": "100:0",
        "label_count": len(label_counts),
        "group_count": len(group_counts),
        "top_label_counts": dict(sorted(label_counts.items(), key=lambda item: item[1], reverse=True)[:15]),
        "top_group_counts": dict(sorted(group_counts.items(), key=lambda item: item[1], reverse=True)[:15]),
        "limitations": [
            "Synthetic data is not real-world proof.",
            "Official feedback and validation data should replace or augment this dataset before production claims.",
            "Recommendations remain decision support, not final selection advice.",
        ],
    }


def generate_dataset(n: int, version: str) -> dict[str, Any]:
    profiles = _read_profiles()
    sampler = LabelSampler(profiles, RANDOM_STATE)
    simulator = ProfileSimulator(RANDOM_STATE)
    rows = [simulator.simulate(index + 1, sampler.sample(), version) for index in range(n)]
    _write_csv(SYNTHETIC_PATH, rows)
    _write_csv(PROCESSED_PATH, rows)
    card = _dataset_card(rows, version)
    DATASET_CARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATASET_CARD_PATH.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"synthetic_path": str(SYNTHETIC_PATH), "processed_path": str(PROCESSED_PATH), "dataset_card_path": str(DATASET_CARD_PATH), "row_count": len(rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5000)
    parser.add_argument("--version", default="apti_dataset_v2")
    args = parser.parse_args()
    print(json.dumps(generate_dataset(args.n, args.version), ensure_ascii=False, indent=2))
