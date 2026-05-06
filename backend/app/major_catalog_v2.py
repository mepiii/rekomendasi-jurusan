# Purpose: Build Apti V2 major catalog profiles with scoring tags and chart metadata.
# Callers: V2 scoring service, result API, and catalog tests.
# Deps: copy, json, pathlib, subject normalization.
# API: MAJOR_CATALOG_V2, get_major_catalog_v2, get_major_profile.
# Side effects: Reads bundled prodi dataset at import time.

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from app.subject_normalization import normalize_subject_key

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = REPO_ROOT / "dataset_prodi_mapel_pendukung.json"
CURRICULUM_FIELDS = ("mapel_kurmer", "mapel_k13_ipa", "mapel_k13_ips", "mapel_k13_bahasa")

RUMPUN_TAGS = {
    "Humaniora": ("language", "culture", "creative"),
    "Ilmu Sosial": ("social", "law", "communication", "people"),
    "Ilmu Alam": ("biology", "research", "environment", "health"),
    "Ilmu Formal": ("math", "data_ai", "technology", "research"),
    "Ilmu Terapan": ("engineering", "technology", "hands_on"),
}

KEYWORD_TAGS = {
    "informatika": {"interest": ("technology", "software"), "career": ("software_engineer", "technology_builder"), "avoid": ("avoid_coding",), "skills": ("Algoritma", "Pemrograman", "Sistem komputer")},
    "kecerdasan artifisial": {"interest": ("technology", "data_ai"), "career": ("ai_engineer", "data_scientist"), "avoid": ("avoid_math_heavy",), "skills": ("Matematika lanjut", "Python", "Etika AI")},
    "sains data": {"interest": ("data_ai", "research"), "career": ("data_scientist", "analyst"), "avoid": ("avoid_statistics",), "skills": ("Statistika", "Python/SQL", "Komunikasi data")},
    "kedokteran": {"interest": ("health", "biology"), "career": ("doctor", "healthcare_professional"), "avoid": ("avoid_long_clinical_path",), "skills": ("Biologi", "Kimia", "Komunikasi pasien")},
    "farmasi": {"interest": ("health", "chemistry"), "career": ("pharmacist", "lab_quality"), "avoid": ("avoid_lab_detail",), "skills": ("Kimia", "Biologi", "Ketelitian lab")},
    "hukum": {"interest": ("law", "social"), "career": ("legal_policy", "advocate"), "avoid": ("avoid_reading_heavy",), "skills": ("Logika hukum", "Argumentasi", "Membaca intensif")},
    "psikologi": {"interest": ("psychology", "people"), "career": ("counseling", "human_behavior_research"), "avoid": ("avoid_emotional_labor",), "skills": ("Statistika dasar", "Observasi perilaku", "Komunikasi empatik")},
    "desain": {"interest": ("design", "creative"), "career": ("creative_professional", "designer"), "avoid": ("avoid_portfolio_work",), "skills": ("Portofolio", "Visual thinking", "Design tools")},
    "pendidikan": {"interest": ("education", "people"), "career": ("educator", "curriculum"), "avoid": ("avoid_teaching",), "skills": ("Pedagogi", "Komunikasi", "Asesmen belajar")},
    "manajemen": {"interest": ("business", "people"), "career": ("business_leader", "operations"), "avoid": ("avoid_team_coordination",), "skills": ("Strategi bisnis", "Koordinasi", "Analisis pasar")},
    "akuntansi": {"interest": ("business", "numbers"), "career": ("finance_analyst", "auditor"), "avoid": ("avoid_repetitive_detail",), "skills": ("Akuntansi dasar", "Ketelitian", "Analisis laporan")},
}


def _load_rows() -> list[dict[str, Any]]:
    data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    return data["prodi_spesifik_mapping"]


def _split_subjects(value: str) -> list[str]:
    return [part.strip() for part in value.replace("dan/atau", ",").replace(" dan ", ",").split(",") if part.strip()]


def _subject_weights(row: dict[str, Any]) -> dict[str, float]:
    weights: dict[str, float] = {}
    for field in CURRICULUM_FIELDS:
        for subject in _split_subjects(row.get(field, "")):
            key = normalize_subject_key(subject)
            weights[key] = min(1.0, weights.get(key, 0.0) + 0.25)
    return dict(sorted(weights.items()))


def _keyword_profile(name: str, kelompok: str) -> dict[str, list[str]]:
    haystack = f"{name} {kelompok}".lower()
    profile = {"interest": [], "career": [], "avoid": [], "skills": []}
    for keyword, tags in KEYWORD_TAGS.items():
        if keyword not in haystack:
            continue
        profile["interest"].extend(tags["interest"])
        profile["career"].extend(tags["career"])
        profile["avoid"].extend(tags["avoid"])
        profile["skills"].extend(tags["skills"])
    return {key: _unique(values) for key, values in profile.items()}


def _unique(values: list[str] | tuple[str, ...], limit: int = 8) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result[:limit]


def _english_label(name: str) -> str:
    translations = {
        "Teknik Informatika": "Informatics Engineering",
        "Kecerdasan Artifisial": "Artificial Intelligence",
        "Sains Data": "Data Science",
        "Kedokteran": "Medicine",
        "Farmasi": "Pharmacy",
        "Psikologi": "Psychology",
        "Hukum": "Law",
        "Manajemen": "Management",
        "Akuntansi": "Accounting",
        "Desain Komunikasi Visual": "Visual Communication Design",
    }
    return translations.get(name, name)


def _profile(row: dict[str, Any]) -> dict[str, Any]:
    keyword = _keyword_profile(row["nama_prodi_spesifik"], row["kelompok_prodi_resmi"])
    rumpun_tags = list(RUMPUN_TAGS.get(row["rumpun_ilmu"], ()))
    subject_weights = _subject_weights(row)
    skill_gaps = keyword["skills"] or [subject.replace("_", " ").title() for subject in list(subject_weights)[:3]]

    return {
        "prodi_id": row["prodi_id"],
        "label": {"id": row["nama_prodi_spesifik"], "en": _english_label(row["nama_prodi_spesifik"])},
        "aliases": row.get("alias", []),
        "kelompok_prodi": row["kelompok_prodi_resmi"],
        "rumpun_ilmu": row["rumpun_ilmu"],
        "subject_weights": subject_weights,
        "interest_tags": _unique([*rumpun_tags, *keyword["interest"]]),
        "career_tags": _unique(keyword["career"] or rumpun_tags),
        "constraint_tags": _unique(["compare_campus_curriculum", "review_cost_path"]),
        "avoid_tags": _unique(keyword["avoid"] or [f"avoid_{row['rumpun_ilmu'].lower().replace(' ', '_')}"]),
        "skill_gaps": skill_gaps,
        "target_keywords": _unique([row["nama_prodi_spesifik"], row["kelompok_prodi_resmi"], *row.get("alias", [])]),
        "chart_dimensions": {
            "academic": round(sum(subject_weights.values()) / max(len(subject_weights), 1), 3),
            "interest": min(1.0, len(keyword["interest"] or rumpun_tags) / 5),
            "career": min(1.0, len(keyword["career"] or rumpun_tags) / 5),
        },
        "explanation_templates": {
            "id": "Cocok bila sinyal akademik, minat, dan arah kariermu selaras dengan prodi ini.",
            "en": "Fits when your academic signals, interests, and career direction align with this program.",
        },
        "mapping_confidence": float(row["confidence_score"]),
        "source": row.get("sumber_mapel", ""),
    }


def _build_catalog() -> dict[str, dict[str, Any]]:
    return {row["prodi_id"]: _profile(row) for row in _load_rows()}


MAJOR_CATALOG_V2 = _build_catalog()


def get_major_catalog_v2() -> list[dict[str, Any]]:
    return [copy.deepcopy(profile) for profile in MAJOR_CATALOG_V2.values()]


def get_major_profile(prodi_id: str) -> dict[str, Any]:
    return copy.deepcopy(MAJOR_CATALOG_V2[prodi_id])
