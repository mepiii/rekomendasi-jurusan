# Purpose: Provide cached scoring profiles for Apti-specific prodi recommendations.
# Callers: ML scoring, explanations, dataset generation, and LLM review context.
# Deps: functools, json, pathlib, prodi catalog service.
# API: ProdiProfileService, prodi_profile_service.
# Side effects: Reads generated prodi profile matrix lazily.

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.services.prodi_catalog_service import prodi_catalog_service

ROOT_DIR = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT_DIR / "ml" / "config" / "prodi_profiles.json"


@lru_cache(maxsize=1)
def _profile_payload() -> dict[str, Any]:
    with PROFILE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


class ProdiProfileService:
    @property
    def version(self) -> str:
        return str(_profile_payload().get("version", "apti_prodi_profiles_v1"))

    @property
    def profiles(self) -> list[dict[str, Any]]:
        return list(_profile_payload().get("profiles", []))

    def get_profile(self, prodi_id: str) -> dict[str, Any] | None:
        return self._profiles_by_id().get(prodi_id)

    def resolve_profile(self, value: str) -> dict[str, Any] | None:
        prodi = prodi_catalog_service.resolve_alias(value)
        return self.get_profile(prodi["prodi_id"]) if prodi else None

    def profiles_by_kelompok(self, kelompok_prodi: str) -> list[dict[str, Any]]:
        return [profile for profile in self.profiles if profile.get("kelompok_prodi") == kelompok_prodi]

    def academic_weights(self, prodi_id: str) -> dict[str, float]:
        profile = self.get_profile(prodi_id)
        return dict(profile.get("academic_weights", {})) if profile else {}

    def radar_benchmark(self, prodi_id: str) -> dict[str, float]:
        weights = self.academic_weights(prodi_id)
        return {subject: round(72 + weight * 18, 2) for subject, weight in weights.items()}

    def alternatives(self, prodi_id: str) -> list[dict[str, Any]]:
        profile = self.get_profile(prodi_id)
        if not profile:
            return []
        return [
            prodi_catalog_service.get_prodi(alternative_id)
            for alternative_id in profile.get("alternative_prodi", [])
            if prodi_catalog_service.get_prodi(alternative_id)
        ]

    def llm_context(self, prodi_id: str) -> dict[str, Any] | None:
        profile = self.get_profile(prodi_id)
        if not profile:
            return None
        return {
            "prodi_id": profile["prodi_id"],
            "nama_prodi": profile["nama_prodi"],
            "kelompok_prodi": profile["kelompok_prodi"],
            "rumpun_ilmu": profile["rumpun_ilmu"],
            "academic_weights": profile["academic_weights"],
            "interest_weights": profile["interest_weights"],
            "career_paths": profile["career_paths"],
            "skill_gaps": profile["skill_gaps"],
            "mapping_confidence": profile["mapping_confidence"],
        }

    @staticmethod
    def clear_cache() -> None:
        _profile_payload.cache_clear()

    @lru_cache(maxsize=1)
    def _profiles_by_id(self) -> dict[str, dict[str, Any]]:
        return {profile["prodi_id"]: profile for profile in self.profiles}


prodi_profile_service = ProdiProfileService()
