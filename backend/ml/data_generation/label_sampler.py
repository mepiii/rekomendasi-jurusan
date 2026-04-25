# Purpose: Sample balanced prodi labels from Apti profile matrix.
# Callers: Synthetic dataset generator.
# Deps: random, collections.
# API: LabelSampler.
# Side effects: None.

from __future__ import annotations

import random
from collections import defaultdict
from typing import Any

POPULAR_GROUPS = {"Komputer", "Kedokteran", "Manajemen"}


class LabelSampler:
    def __init__(self, profiles: list[dict[str, Any]], random_state: int = 42) -> None:
        self.random = random.Random(random_state)
        self.by_kelompok: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for profile in profiles:
            self.by_kelompok[profile["kelompok_prodi"]].append(profile)
        self.groups = sorted(self.by_kelompok)

    def sample(self) -> dict[str, Any]:
        group = self.random.choice(self.groups)
        if group in POPULAR_GROUPS and self.random.random() < 0.45:
            group = self.random.choice([item for item in self.groups if item not in POPULAR_GROUPS])
        return self.random.choice(self.by_kelompok[group])
