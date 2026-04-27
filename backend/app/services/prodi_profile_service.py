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
BENCHMARK_DEFAULTS_PATH = ROOT_DIR / "ml" / "data" / "config" / "benchmark_defaults.json"


@lru_cache(maxsize=1)
def _profile_payload() -> dict[str, Any]:
    with PROFILE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def _benchmark_defaults_payload() -> dict[str, Any]:
    with BENCHMARK_DEFAULTS_PATH.open(encoding="utf-8") as handle:
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

    def academic_requirements(self, prodi_id: str) -> dict[str, dict[str, dict[str, float]]]:
        profile = self.get_profile(prodi_id)
        if not profile:
            return {"primary": {}, "supporting": {}, "contextual": {}}
        explicit = profile.get("academic_requirements")
        if explicit:
            return explicit
        defaults = self.kelompok_defaults(profile["kelompok_prodi"])
        if defaults.get("academic_requirements"):
            return defaults["academic_requirements"]
        return {"primary": {}, "supporting": {}, "contextual": {}}

    def kelompok_defaults(self, kelompok_prodi: str) -> dict[str, Any]:
        return dict(_benchmark_defaults_payload().get("kelompok_defaults", {}).get(kelompok_prodi, {}))

    def tier(self, prodi_id: str) -> str:
        profile = self.get_profile(prodi_id) or {}
        if profile.get("tier"):
            return str(profile["tier"])
        defaults = self.kelompok_defaults(profile.get("kelompok_prodi", ""))
        return str(defaults.get("tier", "open"))

    def min_gpa(self, prodi_id: str) -> float:
        profile = self.get_profile(prodi_id) or {}
        if profile.get("min_gpa") is not None:
            return float(profile["min_gpa"])
        defaults = self.kelompok_defaults(profile.get("kelompok_prodi", ""))
        return float(defaults.get("min_gpa", 70))

    def trend_bonus_subjects(self, prodi_id: str) -> list[str]:
        profile = self.get_profile(prodi_id) or {}
        if profile.get("trend_bonus_subjects"):
            return list(profile["trend_bonus_subjects"])
        defaults = self.kelompok_defaults(profile.get("kelompok_prodi", ""))
        return list(defaults.get("trend_bonus_subjects", []))

    def radar_benchmark(self, prodi_id: str) -> dict[str, float]:
        requirements = self.academic_requirements(prodi_id)
        subjects = {subject: values for group in requirements.values() for subject, values in group.items()}
        return {subject: round(float(values.get("benchmark", 75)), 2) for subject, values in subjects.items()}

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
            "academic_requirements": self.academic_requirements(prodi_id),
            "tier": self.tier(prodi_id),
            "min_gpa": self.min_gpa(prodi_id),
            "trend_bonus_subjects": self.trend_bonus_subjects(prodi_id),
            "interest_weights": profile["interest_weights"],
            "preference_weights": profile.get("preference_weights", {}),
            "career_weights": profile.get("career_weights", {}),
            "optional_boosts": profile.get("optional_boosts", {}),
            "supporting_subjects": profile.get("supporting_subjects", {}),
            "career_paths": profile["career_paths"],
            "challenge_areas": profile.get("challenge_areas", []),
            "skill_gaps": profile["skill_gaps"],
            "mapping_confidence": profile["mapping_confidence"],
        }

    @staticmethod
    def clear_cache() -> None:
        _profile_payload.cache_clear()
        _benchmark_defaults_payload.cache_clear()

    @lru_cache(maxsize=1)
    def _profiles_by_id(self) -> dict[str, dict[str, Any]]:
        return {profile["prodi_id"]: profile for profile in self.profiles}


prodi_profile_service = ProdiProfileService()
