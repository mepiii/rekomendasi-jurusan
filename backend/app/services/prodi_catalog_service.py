# Purpose: Provide cached lookup access to Apti cleaned prodi catalog files.
# Callers: Prediction, scoring, explanation, and future form/catalog endpoints.
# Deps: functools, json, pathlib.
# API: ProdiCatalogService, prodi_catalog_service.
# Side effects: Reads cleaned catalog JSON files lazily.

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
CATALOG_DIR = ROOT_DIR / "ml" / "data" / "catalog"
PRODI_PATH = CATALOG_DIR / "prodi_spesifik_clean.json"
KELOMPOK_PATH = CATALOG_DIR / "kelompok_resmi_59_clean.json"
ALIASES_PATH = CATALOG_DIR / "prodi_aliases.json"
QUALITY_REPORT_PATH = CATALOG_DIR / "prodi_data_quality_report.json"


@lru_cache(maxsize=1)
def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class ProdiCatalogService:
    @property
    def prodi(self) -> list[dict[str, Any]]:
        return list(_read_json(PRODI_PATH))

    @property
    def kelompok(self) -> list[dict[str, Any]]:
        return list(_read_json(KELOMPOK_PATH))

    @property
    def aliases(self) -> dict[str, str]:
        return dict(_read_json(ALIASES_PATH))

    @property
    def quality_report(self) -> dict[str, Any]:
        return dict(_read_json(QUALITY_REPORT_PATH))

    def get_prodi(self, prodi_id: str) -> dict[str, Any] | None:
        return self._prodi_by_id().get(prodi_id)

    def resolve_alias(self, value: str) -> dict[str, Any] | None:
        prodi_id = self.aliases.get(value.strip().lower())
        return self.get_prodi(prodi_id) if prodi_id else None

    def search_prodi(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        normalized = query.strip().lower()
        if not normalized:
            return []
        matches = [
            item
            for item in self.prodi
            if normalized in item["nama_prodi"].lower()
            or any(normalized in alias.lower() for alias in item.get("alias", []))
        ]
        return matches[:limit]

    def get_by_kelompok(self, kelompok_prodi: str) -> list[dict[str, Any]]:
        return [item for item in self.prodi if item.get("kelompok_prodi") == kelompok_prodi]

    def get_kelompok(self, kelompok_prodi: str) -> dict[str, Any] | None:
        return self._kelompok_by_name().get(kelompok_prodi)

    def supporting_subjects(self, prodi_id: str, curriculum_type: str) -> list[dict[str, str]]:
        prodi = self.get_prodi(prodi_id)
        if not prodi:
            return []
        curriculum_key = self._curriculum_key(curriculum_type)
        return list(prodi.get("supporting_subjects", {}).get(curriculum_key, {}).get("subjects", []))

    def related_prodi(self, prodi_id: str, limit: int = 5) -> list[dict[str, Any]]:
        prodi = self.get_prodi(prodi_id)
        if not prodi:
            return []
        return [
            item
            for item in self.get_by_kelompok(prodi["kelompok_prodi"])
            if item["prodi_id"] != prodi_id
        ][:limit]

    def safe_prodi(self) -> list[dict[str, Any]]:
        profession_terms = ("profesi", "spesialis", "dokter spesialis")
        return [
            item
            for item in self.prodi
            if not any(term in item["nama_prodi"].lower() for term in profession_terms)
        ]

    @staticmethod
    def clear_cache() -> None:
        _read_json.cache_clear()

    @staticmethod
    def _curriculum_key(value: str | None) -> str:
        normalized = (value or "kurikulum_merdeka").strip().lower().replace(" ", "_").replace("-", "_")
        return {
            "merdeka": "kurikulum_merdeka",
            "kurikulum_merdeka": "kurikulum_merdeka",
            "ipa": "k13_ipa",
            "k13_ipa": "k13_ipa",
            "ips": "k13_ips",
            "k13_ips": "k13_ips",
            "bahasa": "k13_bahasa",
            "k13_bahasa": "k13_bahasa",
        }.get(normalized, "kurikulum_merdeka")

    @lru_cache(maxsize=1)
    def _prodi_by_id(self) -> dict[str, dict[str, Any]]:
        return {item["prodi_id"]: item for item in self.prodi}

    @lru_cache(maxsize=1)
    def _kelompok_by_name(self) -> dict[str, dict[str, Any]]:
        return {item["kelompok_prodi_resmi"]: item for item in self.kelompok}


prodi_catalog_service = ProdiCatalogService()
