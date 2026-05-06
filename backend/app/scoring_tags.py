# Purpose: Convert option-only survey selections into normalized Apti V2 scoring tags.
# Callers: V2 scoring service and schema tests.
# Deps: dataclasses, math.
# API: OPTION_TAGS, TagProfile, build_tag_profile.
# Side effects: None.

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt

OPTION_TAGS: dict[str, tuple[str, ...]] = {
    "software_engineering": ("technology", "software"),
    "data_ai_products": ("technology", "data_ai"),
    "technology_builder": ("technology", "builder"),
    "build_ai_products": ("technology", "data_ai", "product"),
    "cybersecurity_systems": ("technology", "security"),
    "robotics_engineering": ("engineering", "technology"),
    "healthcare_impact": ("health", "biology"),
    "finance_business_analytics": ("business", "data_ai"),
    "public_policy_advocacy": ("law", "social"),
    "teaching_curriculum": ("education", "people"),
    "creative_visual_work": ("creative", "design"),
    "human_behavior_research": ("psychology", "research"),
}


@dataclass(frozen=True)
class TagProfile:
    tag_weights: dict[str, float] = field(default_factory=dict)
    consistency_counts: dict[str, int] = field(default_factory=dict)

    def consistency_multiplier(self, tag: str) -> float:
        count = self.consistency_counts.get(tag, 0)
        if count >= 3:
            return 1.5
        if count == 2:
            return 1.2
        return 1.0


def _selection_tags(option: str) -> tuple[str, ...]:
    return OPTION_TAGS.get(option, (option,))


def build_tag_profile(survey_options: dict[str, list[str]]) -> TagProfile:
    page_weights: dict[str, float] = {}
    page_presence: dict[str, set[str]] = {}

    for page, selections in survey_options.items():
        if not selections:
            continue
        base = 1 / sqrt(len(selections))
        seen_on_page: set[str] = set()
        for selection in selections:
            for tag in _selection_tags(selection):
                page_weights[tag] = page_weights.get(tag, 0.0) + base
                seen_on_page.add(tag)
        for tag in seen_on_page:
            page_presence.setdefault(tag, set()).add(page)

    consistency_counts = {tag: len(pages) for tag, pages in page_presence.items()}
    weights = {
        tag: round(weight * TagProfile(consistency_counts=consistency_counts).consistency_multiplier(tag), 4)
        for tag, weight in page_weights.items()
    }
    return TagProfile(tag_weights=weights, consistency_counts=consistency_counts)
