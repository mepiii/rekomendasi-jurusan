# Purpose: Simulate realistic Apti student profiles from prodi profiles.
# Callers: generate_synthetic_dataset.py.
# Deps: random, typing, noise_config.
# API: ProfileSimulator.
# Side effects: None.

from __future__ import annotations

import random
from typing import Any

from noise_config import NOISE_CONFIG

CORE_SUBJECTS = ["religion", "civics", "indonesian", "english", "math", "pjok", "arts"]
OPTIONAL_SUBJECTS = [
    "advanced_math",
    "physics",
    "chemistry",
    "biology",
    "economics",
    "sociology",
    "geography",
    "history",
    "anthropology",
    "informatics",
    "foreign_language",
]
SUBJECT_ALIASES = {
    "mathematics": "math",
    "mathematics_advanced": "advanced_math",
    "bahasa_indonesia": "indonesian",
    "bahasa_indonesia_advanced": "indonesian",
    "english_advanced": "english",
    "arts_culture": "arts",
    "religion_ethics": "religion",
    "pe": "pjok",
}
INTEREST_LABELS = {
    "technology_digital": "Technology",
    "tech_ai_data": "Data / AI",
    "tech_software": "Technology",
    "engineering": "Engineering",
    "health_life_science": "Health",
    "health_pharmacy": "Health",
    "business_management": "Business",
    "business_finance": "Business",
    "social_law": "Law",
    "social_psychology": "Psychology",
    "communication_media": "Media",
    "language_culture": "Language",
    "creative_design": "Design",
    "education_teaching": "Education",
    "environment_field": "Environment",
    "tourism_hospitality": "Tourism",
}


class ProfileSimulator:
    def __init__(self, random_state: int = 42) -> None:
        self.random = random.Random(random_state)

    def simulate(self, sample_id: int, profile: dict[str, Any], dataset_version: str) -> dict[str, Any]:
        ambiguity = self.random.random() < NOISE_CONFIG["ambiguous_profile_rate"]
        balanced_high = self.random.random() < NOISE_CONFIG["balanced_high_rate"]
        focused_average = self.random.random() < NOISE_CONFIG["focused_average_rate"]
        base = 86 if balanced_high else 74 if focused_average else self.random.randint(68, 84)
        scores: dict[str, int | None] = {}

        for subject in [*CORE_SUBJECTS, *OPTIONAL_SUBJECTS]:
            scores[subject] = self._score(base, 0)
        for subject, weight in profile.get("academic_weights", {}).items():
            normalized = SUBJECT_ALIASES.get(subject, subject)
            scores[normalized] = self._score(base, 10 * float(weight))
        for subject in OPTIONAL_SUBJECTS:
            if self.random.random() < NOISE_CONFIG["missing_optional_rate"]:
                scores[subject] = None

        interests = sorted({INTEREST_LABELS[key] for key in profile.get("interest_weights", {}) if key in INTEREST_LABELS})[:5]
        if ambiguity:
            interests = sorted(set(interests + self.random.sample(["Technology", "Business", "Social", "Design", "Education"], 2)))[:5]
        if not interests:
            interests = ["Education"]

        return {
            "sample_id": f"S{sample_id:05d}",
            "source_type": "synthetic_v2",
            "dataset_version": dataset_version,
            "curriculum_type": self.random.choice(["Kurikulum Merdeka", "K13 IPA", "K13 IPS", "K13 Bahasa"]),
            "sma_track": self.random.choice(["Merdeka", "IPA", "IPS", "Bahasa"]),
            **{f"score_{key}": value for key, value in scores.items()},
            "academic_confidence": self.random.choice(["numbers/calculation", "science/lab", "language/writing", "social/human", "creative/art", "balanced"]),
            "score_pattern": "balanced" if ambiguity else "several strong subjects",
            "interests": "|".join(interests),
            "interest_deep_dive": "|".join(sorted(profile.get("interest_weights", {}))[:6]),
            "work_style": self.random.choice(["independent", "teamwork", "lab work", "field work", "research-focused"]),
            "career_priorities": "|".join(self.random.sample(["stable career", "high salary potential", "helping people", "research/innovation", "public service", "remote/digital work"], 2)),
            "constraints": self.random.choice(["balanced", "practical/project-heavy", "lab-heavy", "field-heavy", "theory-heavy"]),
            "expected_prodi": "" if self.random.random() < 0.7 else profile["nama_prodi"],
            "prodi_to_avoid": "none",
            "free_text_goal_keywords": " ".join(profile.get("career_paths", [])[:2]),
            "target_cluster": profile["rumpun_ilmu"],
            "target_kelompok_prodi": profile["kelompok_prodi"],
            "target_prodi": profile["nama_prodi"],
            "target_prodi_id": profile["prodi_id"],
            "ambiguity_flag": ambiguity,
            "quality_flag": "balanced_high" if balanced_high else "focused_average" if focused_average else "standard",
        }

    def _score(self, base: int, boost: float) -> int:
        value = self.random.gauss(base + boost, NOISE_CONFIG["score_std"])
        return max(45, min(100, int(round(value))))
