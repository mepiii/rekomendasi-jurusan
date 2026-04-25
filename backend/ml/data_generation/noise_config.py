# Purpose: Centralize deterministic noise settings for Apti synthetic dataset v2.
# Callers: profile_simulator and dataset generator.
# Deps: None.
# API: NOISE_CONFIG, RANDOM_STATE.
# Side effects: None.

from __future__ import annotations

RANDOM_STATE = 42
NOISE_CONFIG = {
    "score_std": 7.5,
    "missing_optional_rate": 0.18,
    "ambiguous_profile_rate": 0.22,
    "balanced_high_rate": 0.08,
    "focused_average_rate": 0.14,
    "label_noise_rate": 0.04,
}
