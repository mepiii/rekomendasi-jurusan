# Purpose: Validate raw Apti prodi source data before catalog generation.
# Callers: Data quality checks and catalog build script.
# Deps: collections, json, load_prodi_data.
# API: validate_bundle, build_quality_report.
# Side effects: Prints report when run as script.

from __future__ import annotations

import json
from collections import Counter
from typing import Any

from load_prodi_data import ProdiDataBundle, load_prodi_data

KELOMPOK_REQUIRED = {
    "no",
    "rumpun_ilmu",
    "kelompok_prodi_resmi",
    "mapel_kurmer",
    "mapel_k13_ipa",
    "mapel_k13_ips",
    "mapel_k13_bahasa",
    "sumber",
}
PRODI_REQUIRED = {
    "prodi_id",
    "nama_prodi_spesifik",
    "alias",
    "kelompok_prodi_resmi",
    "rumpun_ilmu",
    "mapel_kurmer",
    "mapel_k13_ipa",
    "mapel_k13_ips",
    "mapel_k13_bahasa",
    "confidence_score",
    "catatan_mapping",
    "sumber_mapel",
}
JSON_KELOMPOK_MAP = {
    "no": "no",
    "rumpun": "rumpun_ilmu",
    "kelompok": "kelompok_prodi_resmi",
    "kurmer": "mapel_kurmer",
    "k13_ipa": "mapel_k13_ipa",
    "k13_ips": "mapel_k13_ips",
    "k13_bahasa": "mapel_k13_bahasa",
}


def _normalize_row(row: dict[str, Any]) -> dict[str, str]:
    return {key: str(value or "").strip() for key, value in row.items()}


def _normalize_json_kelompok(row: dict[str, Any]) -> dict[str, str]:
    return {target: str(row.get(source, "")).strip() for source, target in JSON_KELOMPOK_MAP.items()}


def _missing_fields(rows: list[dict[str, Any]], required: set[str]) -> list[str]:
    if not rows:
        return sorted(required)
    fields = set(rows[0])
    return sorted(required - fields)


def build_quality_report(bundle: ProdiDataBundle) -> dict[str, Any]:
    kelompok_names = {str(row.get("kelompok_prodi_resmi", "")).strip() for row in bundle.kelompok_csv}
    prodi_ids = [str(row.get("prodi_id", "")).strip() for row in bundle.prodi_csv]
    prodi_names = [str(row.get("nama_prodi_spesifik", "")).strip() for row in bundle.prodi_csv]
    confidence_values: list[float] = []
    invalid_confidence: list[str] = []

    for row in bundle.prodi_csv:
        prodi_id = str(row.get("prodi_id", "")).strip()
        try:
            value = float(row.get("confidence_score", ""))
        except ValueError:
            invalid_confidence.append(prodi_id)
            continue
        if not 0 <= value <= 1:
            invalid_confidence.append(prodi_id)
        confidence_values.append(value)

    kelompok_csv_normalized = [
        {field: _normalize_row(row)[field] for field in JSON_KELOMPOK_MAP.values()}
        for row in bundle.kelompok_csv
    ]
    kelompok_json_normalized = [_normalize_json_kelompok(row) for row in bundle.kelompok_json]
    prodi_csv_normalized = [_normalize_row(row) for row in bundle.prodi_csv]
    prodi_json_normalized = [_normalize_row(row) for row in bundle.prodi_json]
    prodi_name_counts = Counter(prodi_names)

    return {
        "row_counts": {
            "kelompok_csv": len(bundle.kelompok_csv),
            "prodi_csv": len(bundle.prodi_csv),
            "kelompok_json": len(bundle.kelompok_json),
            "prodi_json": len(bundle.prodi_json),
        },
        "missing_columns": {
            "kelompok_csv": _missing_fields(bundle.kelompok_csv, KELOMPOK_REQUIRED),
            "prodi_csv": _missing_fields(bundle.prodi_csv, PRODI_REQUIRED),
        },
        "duplicate_prodi_id": sorted([item for item, count in Counter(prodi_ids).items() if count > 1]),
        "duplicate_prodi_names": {item: count for item, count in prodi_name_counts.items() if count > 1},
        "missing_kelompok_prodi_resmi": sorted(
            str(row.get("prodi_id", "")).strip()
            for row in bundle.prodi_csv
            if not str(row.get("kelompok_prodi_resmi", "")).strip()
        ),
        "mapping_groups_missing_from_official": sorted(
            {
                str(row.get("kelompok_prodi_resmi", "")).strip()
                for row in bundle.prodi_csv
                if str(row.get("kelompok_prodi_resmi", "")).strip() not in kelompok_names
            }
        ),
        "invalid_confidence_score": invalid_confidence,
        "confidence_score_range": [min(confidence_values), max(confidence_values)] if confidence_values else [None, None],
        "json_matches_csv": {
            "kelompok_resmi_59": kelompok_csv_normalized == kelompok_json_normalized,
            "prodi_spesifik_mapping": prodi_csv_normalized == prodi_json_normalized,
        },
        "passed": False,
    }


def validate_bundle(bundle: ProdiDataBundle) -> dict[str, Any]:
    report = build_quality_report(bundle)
    report["passed"] = not any(
        [
            report["missing_columns"]["kelompok_csv"],
            report["missing_columns"]["prodi_csv"],
            report["duplicate_prodi_id"],
            report["missing_kelompok_prodi_resmi"],
            report["mapping_groups_missing_from_official"],
            report["invalid_confidence_score"],
            not report["json_matches_csv"]["kelompok_resmi_59"],
            not report["json_matches_csv"]["prodi_spesifik_mapping"],
        ]
    )
    return report


if __name__ == "__main__":
    quality_report = validate_bundle(load_prodi_data())
    print(json.dumps(quality_report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if quality_report["passed"] else 1)
