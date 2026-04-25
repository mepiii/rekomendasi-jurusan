# Purpose: Normalize Indonesian supporting-subject text into Apti ML feature keys.
# Callers: Prodi data ingestion and catalog builders.
# Deps: re, unicodedata.
# API: normalize_subject_text, normalize_subject_list, SUBJECT_NORMALIZATION_MAP.
# Side effects: None.

from __future__ import annotations

import re
import unicodedata

SUBJECT_NORMALIZATION_MAP: dict[str, str] = {
    "matematika": "mathematics",
    "matematika tingkat lanjut": "mathematics_advanced",
    "matematika dari kelompok peminatan mipa": "mathematics",
    "fisika": "physics",
    "kimia": "chemistry",
    "biologi": "biology",
    "ekonomi": "economics",
    "sosiologi": "sociology",
    "geografi": "geography",
    "sejarah": "history",
    "sejarah indonesia": "history",
    "ppkn": "civics",
    "pendidikan pancasila": "civics",
    "pendidikan pancasila dan kewarganegaraan": "civics",
    "bahasa indonesia": "bahasa_indonesia",
    "bahasa indonesia tingkat lanjut": "bahasa_indonesia_advanced",
    "bahasa inggris": "english",
    "bahasa inggris tingkat lanjut": "english_advanced",
    "bahasa asing": "foreign_language",
    "bahasa asing lainnya": "foreign_language",
    "bahasa asing yang relevan": "foreign_language",
    "antropologi": "anthropology",
    "seni budaya": "arts_culture",
    "seni": "arts_culture",
    "pjok": "pe",
    "pendidikan jasmani olahraga dan kesehatan": "pe",
    "pendidikan jasmani, olahraga, dan kesehatan": "pe",
    "religion/ethics": "religion_ethics",
    "pendidikan agama": "religion_ethics",
    "informatika": "informatics",
}

_SPLIT_RE = re.compile(r"\s*(?:dan/atau|dan atau|/|,|\bdan\b)\s*", re.IGNORECASE)
_PAREN_RE = re.compile(r"\(([^)]+)\)")


def _clean_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "").strip().lower()
    normalized = normalized.replace("&", " dan ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip(" .;")


def _normalize_one(raw_subject: str) -> str:
    cleaned = _clean_text(raw_subject)
    return SUBJECT_NORMALIZATION_MAP.get(cleaned, cleaned.replace(" ", "_"))


def normalize_subject_text(raw_text: str | None) -> list[dict[str, str]]:
    text = (raw_text or "").strip()
    if not text:
        return []

    parenthetical = _PAREN_RE.findall(text)
    without_parentheses = _PAREN_RE.sub("", text)
    parts = [part.strip() for part in _SPLIT_RE.split(without_parentheses) if part.strip()]
    parts.extend(part.strip() for part in parenthetical if part.strip())

    seen: set[str] = set()
    normalized: list[dict[str, str]] = []
    for raw in parts:
        key = _normalize_one(raw)
        if key in seen:
            continue
        seen.add(key)
        normalized.append({"raw": raw, "key": key})
    return normalized


def normalize_subject_list(values: list[str]) -> list[dict[str, str]]:
    subjects: list[dict[str, str]] = []
    seen: set[str] = set()
    for value in values:
        for item in normalize_subject_text(value):
            if item["key"] in seen:
                continue
            seen.add(item["key"])
            subjects.append(item)
    return subjects
