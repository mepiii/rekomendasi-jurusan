# Purpose: Build Apti prodi profile matrix from cleaned catalog data.
# Callers: ML scoring, dataset generation, explanation, and LLM review context.
# Deps: json, pathlib.
# API: build_profiles.
# Side effects: Writes backend/ml/config/prodi_profiles.json.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG_DIR = REPO_ROOT / "backend" / "ml" / "data" / "catalog"
PROFILE_PATH = REPO_ROOT / "backend" / "ml" / "config" / "prodi_profiles.json"
CURRICULUM_KEYS = ("kurikulum_merdeka", "k13_ipa", "k13_ips", "k13_bahasa")

RUMPUN_INTERESTS = {
    "Humaniora": {"language_culture": 0.7, "creative_design": 0.5, "communication_media": 0.4},
    "Ilmu Sosial": {"social_law_public": 0.7, "communication_media": 0.5, "education": 0.3},
    "Ilmu Alam": {"health_life_science": 0.6, "environment_field": 0.5, "research_analysis": 0.4},
    "Ilmu Formal": {"technology_digital": 0.6, "data_ai": 0.5, "numbers_logic": 0.5},
    "Ilmu Terapan": {"engineering": 0.6, "technology_digital": 0.4, "hands_on": 0.4},
}

KEYWORD_WEIGHTS = {
    "Kecerdasan Artifisial": {"interest_weights": {"tech_ai_data": 1, "technology_digital": 0.8}, "career_paths": ["AI Engineer", "Machine Learning Engineer", "Data Scientist"], "skill_gaps": ["Matematika lanjut", "Pemrograman", "Etika AI"]},
    "Sains Data": {"interest_weights": {"tech_ai_data": 1, "business_finance": 0.3}, "career_paths": ["Data Scientist", "Data Analyst", "Machine Learning Engineer"], "skill_gaps": ["Statistika", "Python/SQL", "Komunikasi data"]},
    "Informatika": {"interest_weights": {"tech_software": 1, "technology_digital": 0.8}, "career_paths": ["Software Engineer", "Backend Developer", "Tech Lead"], "skill_gaps": ["Algoritma", "Pemrograman", "Sistem komputer"]},
    "Sistem Informasi": {"interest_weights": {"tech_software": 0.7, "business_management": 0.7}, "career_paths": ["System Analyst", "Product Analyst", "IT Consultant"], "skill_gaps": ["Analisis bisnis", "Database", "Manajemen produk"]},
    "Teknik": {"interest_weights": {"engineering": 0.9, "hands_on": 0.6}, "career_paths": ["Engineer", "Project Engineer", "Technical Specialist"], "skill_gaps": ["Fisika terapan", "Matematika", "Problem solving teknis"]},
    "Farmasi": {"interest_weights": {"health_pharmacy": 1, "health_lab": 0.7}, "career_paths": ["Apoteker", "Clinical Pharmacist", "Quality Control"], "skill_gaps": ["Kimia", "Biologi", "Ketelitian lab"]},
    "Gizi": {"interest_weights": {"health_nutrition": 1, "helping_people": 0.5}, "career_paths": ["Ahli Gizi", "Nutritionist", "Public Health Educator"], "skill_gaps": ["Biologi", "Komunikasi kesehatan", "Analisis pola makan"]},
    "Hukum": {"interest_weights": {"social_law": 1, "writing_reading": 0.7}, "career_paths": ["Legal Officer", "Advocate", "Policy Analyst"], "skill_gaps": ["Logika hukum", "Membaca intensif", "Argumentasi"]},
    "Psikologi": {"interest_weights": {"social_psychology": 1, "helping_people": 0.6}, "career_paths": ["HR Specialist", "Counselor Assistant", "Research Assistant"], "skill_gaps": ["Statistika dasar", "Observasi perilaku", "Komunikasi empatik"]},
    "Desain": {"interest_weights": {"creative_design": 1, "visual_design": 0.8}, "career_paths": ["Designer", "Creative Director", "UI/UX Designer"], "skill_gaps": ["Portofolio", "Visual thinking", "Design tools"]},
    "Pariwisata": {"interest_weights": {"tourism_hospitality": 1, "communication_media": 0.4}, "career_paths": ["Tourism Planner", "Hotel Manager", "Event Specialist"], "skill_gaps": ["Bahasa asing", "Service mindset", "Manajemen event"]},
    "Pendidikan": {"interest_weights": {"education_teaching": 1, "helping_people": 0.5}, "career_paths": ["Teacher", "Curriculum Developer", "Learning Designer"], "skill_gaps": ["Pedagogi", "Komunikasi", "Asesmen belajar"]},
}

CAREER_BY_RUMPUN = {
    "Humaniora": ["Researcher", "Writer", "Cultural Specialist"],
    "Ilmu Sosial": ["Analyst", "Public Officer", "Community Specialist"],
    "Ilmu Alam": ["Research Assistant", "Lab Analyst", "Science Communicator"],
    "Ilmu Formal": ["Data Analyst", "Quantitative Analyst", "Researcher"],
    "Ilmu Terapan": ["Practitioner", "Technical Specialist", "Project Officer"],
}


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _subject_weights(supporting_subjects: dict[str, Any]) -> dict[str, float]:
    weights: dict[str, float] = {}
    for curriculum in CURRICULUM_KEYS:
        subjects = supporting_subjects.get(curriculum, {}).get("subjects", [])
        for item in subjects:
            key = item["key"]
            weights[key] = min(1.0, weights.get(key, 0) + 0.25)
    return dict(sorted(weights.items()))


def _merge_weights(*weights: dict[str, float]) -> dict[str, float]:
    merged: dict[str, float] = {}
    for source in weights:
        for key, value in source.items():
            merged[key] = max(merged.get(key, 0), float(value))
    return dict(sorted(merged.items()))


def _keyword_profile(name: str, kelompok: str) -> dict[str, Any]:
    merged: dict[str, Any] = {"interest_weights": {}, "career_paths": [], "skill_gaps": []}
    haystack = f"{name} {kelompok}"
    for keyword, profile in KEYWORD_WEIGHTS.items():
        if keyword.lower() not in haystack.lower():
            continue
        merged["interest_weights"] = _merge_weights(merged["interest_weights"], profile.get("interest_weights", {}))
        merged["career_paths"] = [*merged["career_paths"], *profile.get("career_paths", [])]
        merged["skill_gaps"] = [*merged["skill_gaps"], *profile.get("skill_gaps", [])]
    return merged


def _unique(values: list[str], limit: int = 6) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result[:limit]


def _alternatives(prodi: dict[str, Any], by_kelompok: dict[str, list[dict[str, Any]]]) -> list[str]:
    siblings = by_kelompok.get(prodi["kelompok_prodi"], [])
    return [item["prodi_id"] for item in siblings if item["prodi_id"] != prodi["prodi_id"]][:5]


def _profile(prodi: dict[str, Any], by_kelompok: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    keyword = _keyword_profile(prodi["nama_prodi"], prodi["kelompok_prodi"])
    academic_weights = _subject_weights(prodi["supporting_subjects"])
    interest_weights = _merge_weights(RUMPUN_INTERESTS.get(prodi["rumpun_ilmu"], {}), keyword["interest_weights"])
    career_paths = _unique([*keyword["career_paths"], *CAREER_BY_RUMPUN.get(prodi["rumpun_ilmu"], [])])
    skill_gaps = _unique([*keyword["skill_gaps"], *[subject.replace("_", " ").title() for subject in academic_weights][:3]])

    return {
        "prodi_id": prodi["prodi_id"],
        "nama_prodi": prodi["nama_prodi"],
        "alias": prodi["alias"],
        "kelompok_prodi": prodi["kelompok_prodi"],
        "rumpun_ilmu": prodi["rumpun_ilmu"],
        "academic_weights": academic_weights,
        "interest_weights": interest_weights,
        "preference_weights": {
            "structured": 0.5,
            "practical_project": 0.5 if prodi["rumpun_ilmu"] == "Ilmu Terapan" else 0.3,
            "research_analysis": 0.5 if prodi["rumpun_ilmu"] in {"Ilmu Alam", "Ilmu Formal"} else 0.3,
        },
        "career_weights": {key: value for key, value in interest_weights.items() if value >= 0.5},
        "optional_boosts": academic_weights,
        "supporting_subjects": prodi["supporting_subjects"],
        "career_paths": career_paths,
        "skill_gaps": skill_gaps,
        "challenge_areas": ["Validasi minat lewat eksplorasi kampus/prodi", "Bandingkan kurikulum antar kampus"],
        "alternative_prodi": _alternatives(prodi, by_kelompok),
        "mapping_confidence": prodi["mapping_confidence"],
        "catatan_mapping": prodi["catatan_mapping"],
        "sumber_mapel": prodi["sumber_mapel"],
    }


def build_profiles(output_path: Path = PROFILE_PATH) -> dict[str, Any]:
    prodi_rows = _read_json(CATALOG_DIR / "prodi_spesifik_clean.json")
    by_kelompok: dict[str, list[dict[str, Any]]] = {}
    for prodi in prodi_rows:
        by_kelompok.setdefault(prodi["kelompok_prodi"], []).append(prodi)

    profiles = [_profile(prodi, by_kelompok) for prodi in prodi_rows]
    _write_json(output_path, {"version": "apti_prodi_profiles_v1", "profiles": profiles})
    return {"output_path": str(output_path), "profile_count": len(profiles), "version": "apti_prodi_profiles_v1"}


if __name__ == "__main__":
    print(json.dumps(build_profiles(), ensure_ascii=False, indent=2))
