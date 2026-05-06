# Purpose: Normalize Apti V2 subject labels into canonical recommendation keys.
# Callers: V2 schemas, scoring services, future survey ingestion.
# Deps: re, unicodedata.
# API: SUBJECT_ALIASES, CANONICAL_SUBJECTS, normalize_subject_key.
# Side effects: None.

from __future__ import annotations

import re
import unicodedata

CANONICAL_SUBJECTS = {
    "religion",
    "civics",
    "indonesian",
    "english",
    "math_general",
    "math_advanced",
    "physical_education",
    "arts",
    "physics",
    "chemistry",
    "biology",
    "informatics",
    "economics",
    "sociology",
    "geography",
    "history",
    "anthropology",
    "indonesian_literature",
    "english_literature",
    "english_advanced",
    "foreign_language",
    "visual_arts",
    "design",
    "craft",
    "entrepreneurship",
}

SUBJECT_ALIASES = {
    "pendidikan agama": "religion",
    "agama": "religion",
    "ppkn": "civics",
    "pkn": "civics",
    "pancasila": "civics",
    "pendidikan pancasila": "civics",
    "bahasa indonesia": "indonesian",
    "indonesia": "indonesian",
    "bahasa inggris": "english",
    "english": "english",
    "matematika": "math_general",
    "matematika umum": "math_general",
    "matematika dasar": "math_general",
    "general_math": "math_general",
    "mathematics": "math_general",
    "matematika lanjut": "math_advanced",
    "matematika tingkat lanjut": "math_advanced",
    "advanced_math": "math_advanced",
    "mathematics_advanced": "math_advanced",
    "pjok": "physical_education",
    "pendidikan jasmani olahraga dan kesehatan": "physical_education",
    "seni": "arts",
    "seni budaya": "arts",
    "fisika": "physics",
    "kimia": "chemistry",
    "biologi": "biology",
    "informatika": "informatics",
    "ekonomi": "economics",
    "sosiologi": "sociology",
    "geografi": "geography",
    "sejarah": "history",
    "antropologi": "anthropology",
    "bahasa dan sastra indonesia": "indonesian_literature",
    "sastra indonesia": "indonesian_literature",
    "bahasa dan sastra inggris": "english_literature",
    "sastra inggris": "english_literature",
    "bahasa inggris tingkat lanjut": "english_advanced",
    "bahasa asing": "foreign_language",
    "seni rupa": "visual_arts",
    "desain": "design",
    "prakarya": "craft",
    "pkwu": "craft",
    "kewirausahaan": "entrepreneurship",
}


def _clean(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "").strip().lower()
    normalized = normalized.replace("&", " dan ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip(" .;")


def normalize_subject_key(value: str) -> str:
    cleaned = _clean(value)
    if cleaned in CANONICAL_SUBJECTS:
        return cleaned
    return SUBJECT_ALIASES.get(cleaned, cleaned.replace(" ", "_"))


def normalize_score_map(scores: dict[str, float | None]) -> dict[str, float | None]:
    normalized: dict[str, float | None] = {}
    for subject, score in scores.items():
        normalized[normalize_subject_key(subject)] = score
    return normalized
