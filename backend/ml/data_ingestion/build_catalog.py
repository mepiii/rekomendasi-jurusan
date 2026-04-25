# Purpose: Build cleaned Apti prodi catalog files from validated raw CSV/JSON sources.
# Callers: Data ingestion CLI, backend catalog service setup.
# Deps: json, pathlib, load_prodi_data, normalize_subjects, validate_prodi_data.
# API: build_catalog.
# Side effects: Writes cleaned catalog JSON files.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from load_prodi_data import ProdiDataBundle, load_prodi_data
from normalize_subjects import SUBJECT_NORMALIZATION_MAP, normalize_subject_text
from validate_prodi_data import validate_bundle

CATALOG_DIR = Path(__file__).resolve().parents[1] / "data" / "catalog"
CURRICULUM_FIELDS = {
    "kurikulum_merdeka": "mapel_kurmer",
    "k13_ipa": "mapel_k13_ipa",
    "k13_ips": "mapel_k13_ips",
    "k13_bahasa": "mapel_k13_bahasa",
}


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _supporting_subjects(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        curriculum: {
            "raw": str(row.get(field, "")).strip(),
            "subjects": normalize_subject_text(str(row.get(field, ""))),
        }
        for curriculum, field in CURRICULUM_FIELDS.items()
    }


def _clean_kelompok(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "no": int(row["no"]),
        "rumpun_ilmu": row["rumpun_ilmu"].strip(),
        "kelompok_prodi_resmi": row["kelompok_prodi_resmi"].strip(),
        "supporting_subjects": _supporting_subjects(row),
        "sumber": row["sumber"].strip(),
    }


def _aliases(row: dict[str, Any]) -> list[str]:
    alias_text = str(row.get("alias", "")).strip()
    if not alias_text:
        return []
    return [item.strip() for item in alias_text.replace(";", ",").split(",") if item.strip()]


def _clean_prodi(row: dict[str, Any], kelompok_by_name: dict[str, dict[str, Any]]) -> dict[str, Any]:
    kelompok = row["kelompok_prodi_resmi"].strip()
    return {
        "prodi_id": row["prodi_id"].strip(),
        "nama_prodi": row["nama_prodi_spesifik"].strip(),
        "alias": _aliases(row),
        "kelompok_prodi": kelompok,
        "rumpun_ilmu": row["rumpun_ilmu"].strip(),
        "supporting_subjects": _supporting_subjects(row),
        "kelompok_supporting_subjects": kelompok_by_name.get(kelompok, {}).get("supporting_subjects", {}),
        "mapping_confidence": float(row["confidence_score"]),
        "catatan_mapping": row.get("catatan_mapping", "").strip(),
        "sumber_mapel": row.get("sumber_mapel", "").strip(),
    }


def _build_alias_map(prodi_rows: list[dict[str, Any]]) -> dict[str, str]:
    alias_map: dict[str, str] = {}
    for row in prodi_rows:
        names = [row["nama_prodi"], *row["alias"]]
        for name in names:
            key = name.strip().lower()
            if key:
                alias_map[key] = row["prodi_id"]
    return dict(sorted(alias_map.items()))


def build_catalog(bundle: ProdiDataBundle | None = None, output_dir: Path = CATALOG_DIR) -> dict[str, Any]:
    bundle = bundle or load_prodi_data()
    report = validate_bundle(bundle)
    if not report["passed"]:
        _write_json(output_dir / "prodi_data_quality_report.json", report)
        raise ValueError("Prodi data validation failed. See prodi_data_quality_report.json")

    kelompok_clean = [_clean_kelompok(row) for row in bundle.kelompok_csv]
    kelompok_by_name = {row["kelompok_prodi_resmi"]: row for row in kelompok_clean}
    prodi_clean = [_clean_prodi(row, kelompok_by_name) for row in bundle.prodi_csv]
    aliases = _build_alias_map(prodi_clean)
    normalization_map = {
        "canonical_subjects": SUBJECT_NORMALIZATION_MAP,
        "curriculum_fields": CURRICULUM_FIELDS,
    }

    _write_json(output_dir / "kelompok_resmi_59_clean.json", kelompok_clean)
    _write_json(output_dir / "prodi_spesifik_clean.json", prodi_clean)
    _write_json(output_dir / "prodi_aliases.json", aliases)
    _write_json(output_dir / "subject_normalization_map.json", normalization_map)
    _write_json(output_dir / "prodi_data_quality_report.json", report)

    return {
        "output_dir": str(output_dir),
        "kelompok_rows": len(kelompok_clean),
        "prodi_rows": len(prodi_clean),
        "alias_count": len(aliases),
        "quality_report": report,
    }


if __name__ == "__main__":
    print(json.dumps(build_catalog(), ensure_ascii=False, indent=2))
