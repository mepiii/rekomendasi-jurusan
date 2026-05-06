# Purpose: Verify Apti V2 foundation contracts before runtime wiring.
# Callers: Pytest backend suite.
# Deps: pytest, pydantic, V2 schema modules.
# API: Phase 1 foundation tests.
# Side effects: None.

import pytest
from pydantic import ValidationError

from app.schemas_v2 import AptiV2PredictRequest
from app.scoring_tags import build_tag_profile
from app.subject_normalization import normalize_subject_key


def test_subject_normalization_keeps_general_and_advanced_math_separate():
    assert normalize_subject_key("Matematika Umum") == "math_general"
    assert normalize_subject_key("Matematika Dasar") == "math_general"
    assert normalize_subject_key("Matematika Lanjut") == "math_advanced"
    assert normalize_subject_key("Matematika Tingkat Lanjut") == "math_advanced"


def test_merdeka_electives_accepts_two_to_eight_items():
    request = AptiV2PredictRequest(
        sma_track="Merdeka",
        selected_electives=["physics", "chemistry", "biology", "informatics", "economics", "sociology"],
        scores={"physics": 90, "chemistry": None},
        survey_options={"interests": ["software_engineering"]},
    )

    assert len(request.selected_electives) == 6
    assert request.scores["chemistry"] is None


@pytest.mark.parametrize("electives", [[], ["physics"], ["physics"] * 9])
def test_merdeka_electives_rejects_outside_two_to_eight_items(electives):
    with pytest.raises(ValidationError):
        AptiV2PredictRequest(sma_track="Merdeka", selected_electives=electives)


def test_v2_request_rejects_free_text_payloads():
    with pytest.raises(ValidationError):
        AptiV2PredictRequest(
            sma_track="IPA",
            scores={"math_general": 88},
            survey_options={"free_text_goal": "I want AI products"},
        )


def test_tag_profile_normalizes_page_weights_and_tracks_consistency():
    profile = build_tag_profile(
        {
            "interests": ["software_engineering", "data_ai_products"],
            "career_direction": ["technology_builder"],
            "goal": ["build_ai_products"],
        }
    )

    assert profile.tag_weights["technology"] > profile.tag_weights["software"]
    assert profile.consistency_counts["technology"] == 3
    assert profile.consistency_multiplier("technology") == 1.5


def test_target_and_avoid_major_fields_are_option_lists():
    request = AptiV2PredictRequest(
        sma_track="IPA",
        scores={"math_general": 90},
        target_majors=["Teknik Informatika"],
        avoided_majors=["Kedokteran"],
    )

    assert request.target_majors == ["Teknik Informatika"]
    assert request.avoided_majors == ["Kedokteran"]
