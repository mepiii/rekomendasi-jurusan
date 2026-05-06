# Purpose: Verify Apti V2 major catalog metadata and tag coverage.
# Callers: Pytest backend suite.
# Deps: app.major_catalog_v2.
# API: Phase 2 catalog contract tests.
# Side effects: None.

from app.major_catalog_v2 import MAJOR_CATALOG_V2, get_major_catalog_v2, get_major_profile


def test_major_catalog_contains_dataset_backed_profiles():
    catalog = get_major_catalog_v2()

    assert len(catalog) >= 489
    assert {"P0120", "P0127", "P0472"}.issubset({item["prodi_id"] for item in catalog})


def test_major_profiles_include_v2_scoring_metadata():
    profile = get_major_profile("P0120")

    assert profile["label"]["id"] == "Teknik Informatika"
    assert profile["label"]["en"]
    assert profile["subject_weights"]
    assert profile["interest_tags"]
    assert profile["career_tags"]
    assert profile["avoid_tags"]
    assert profile["skill_gaps"]
    assert profile["explanation_templates"]["id"]
    assert profile["explanation_templates"]["en"]


def test_every_major_profile_has_required_v2_fields():
    required = {
        "prodi_id",
        "label",
        "kelompok_prodi",
        "rumpun_ilmu",
        "subject_weights",
        "interest_tags",
        "career_tags",
        "constraint_tags",
        "avoid_tags",
        "skill_gaps",
        "target_keywords",
        "chart_dimensions",
        "explanation_templates",
        "mapping_confidence",
    }

    for profile in MAJOR_CATALOG_V2.values():
        assert required.issubset(profile)
        assert profile["label"]["id"]
        assert profile["label"]["en"]
        assert profile["chart_dimensions"]
        assert 0 <= profile["mapping_confidence"] <= 1


def test_get_major_profile_returns_copy_not_shared_state():
    profile = get_major_profile("P0120")
    profile["interest_tags"].append("mutated")

    assert "mutated" not in get_major_profile("P0120")["interest_tags"]
