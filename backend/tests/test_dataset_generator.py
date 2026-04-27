# Purpose: Validate synthetic Apti dataset v2 generation contract.
# Callers: Pytest backend ML suite.
# Deps: backend.ml.dataset_generator.
# API: Tests semester trajectories, personas, and legacy feature compatibility.
# Side effects: None.

from ml.dataset_generator import INTEREST_COLUMN_MAP, MAJOR_LABELS, SUBJECTS, build_dataset


def test_dataset_v2_keeps_legacy_columns_and_adds_semester_features():
    frame = build_dataset(rows=150, seed=7)

    for subject in SUBJECTS:
        assert subject in frame.columns
        assert f"{subject}_trend" in frame.columns
        for semester in range(1, 7):
            assert f"s{semester}_{subject}" in frame.columns
    for column in INTEREST_COLUMN_MAP.values():
        assert column in frame.columns
    assert {"sma_track", "persona", "major", "kelompok_prodi", "cluster", "overall_gpa", "kelas_12_avg"}.issubset(frame.columns)


def test_dataset_v2_balances_labels_and_includes_personas():
    frame = build_dataset(rows=150, seed=7)
    counts = frame["major"].value_counts()

    assert set(frame["major"].unique()) == set(MAJOR_LABELS)
    assert counts.max() - counts.min() <= 1
    assert frame["persona"].nunique() >= 4
    assert frame["sma_track"].isin(["IPA", "IPS", "Bahasa", "Merdeka"]).all()


def test_dataset_v2_trajectory_fields_are_bounded():
    frame = build_dataset(rows=90, seed=11)
    score_columns = [column for column in frame.columns if column.startswith("s") and "_" in column and column.split("_", 1)[0][1:].isdigit()]
    trend_columns = [f"{subject}_trend" for subject in SUBJECTS]

    assert frame[score_columns].min().min() >= 25
    assert frame[score_columns].max().max() <= 100
    assert frame[trend_columns].min().min() >= -1
    assert frame[trend_columns].max().max() <= 1
    assert frame["overall_gpa"].between(25, 100).all()
