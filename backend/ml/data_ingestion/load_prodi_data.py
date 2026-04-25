# Purpose: Load raw Apti prodi CSV/JSON source files into consistent Python records.
# Callers: Catalog validation and build scripts.
# Deps: csv, json, pathlib.
# API: ProdiDataBundle, load_prodi_data, default_paths.
# Side effects: Reads raw source files.

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_JSON = REPO_ROOT / "dataset_prodi_mapel_pendukung.json"
RAW_KELOMPOK_CSV = REPO_ROOT / "kelompok_resmi_59_mapel_pendukung.csv"
RAW_PRODI_CSV = REPO_ROOT / "prodi_spesifik_mapping_mapel_pendukung.csv"


@dataclass(frozen=True)
class ProdiDataBundle:
    kelompok_csv: list[dict[str, Any]]
    prodi_csv: list[dict[str, Any]]
    kelompok_json: list[dict[str, Any]]
    prodi_json: list[dict[str, Any]]
    source_metadata: dict[str, Any]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_prodi_data(
    json_path: Path = RAW_JSON,
    kelompok_csv_path: Path = RAW_KELOMPOK_CSV,
    prodi_csv_path: Path = RAW_PRODI_CSV,
) -> ProdiDataBundle:
    data = _read_json(json_path)
    return ProdiDataBundle(
        kelompok_csv=_read_csv(kelompok_csv_path),
        prodi_csv=_read_csv(prodi_csv_path),
        kelompok_json=list(data.get("kelompok_resmi_59", [])),
        prodi_json=list(data.get("prodi_spesifik_mapping", [])),
        source_metadata={"raw": data.get("sumber", {})},
    )


def default_paths() -> dict[str, str]:
    return {
        "json": str(RAW_JSON),
        "kelompok_csv": str(RAW_KELOMPOK_CSV),
        "prodi_csv": str(RAW_PRODI_CSV),
    }


if __name__ == "__main__":
    bundle = load_prodi_data()
    print(
        json.dumps(
            {
                "paths": default_paths(),
                "kelompok_csv_rows": len(bundle.kelompok_csv),
                "prodi_csv_rows": len(bundle.prodi_csv),
                "kelompok_json_rows": len(bundle.kelompok_json),
                "prodi_json_rows": len(bundle.prodi_json),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
