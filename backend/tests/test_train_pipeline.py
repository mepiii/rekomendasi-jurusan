# Purpose: Validate Apti training pipeline v2 feature and metric contracts.
# Callers: Pytest backend ML suite.
# Deps: pandas, backend.ml dataset/training modules.
# API: Tests feature columns and model evaluation metrics.
# Side effects: None.

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline

from ml.dataset_generator import build_dataset
from ml.train_pipeline import build_preprocessor, evaluate_models, feature_columns_for


def test_training_pipeline_uses_semester_persona_features():
    frame = build_dataset(rows=150, seed=12)
    columns = feature_columns_for(frame)

    assert "s1_math" in columns
    assert "s6_english" in columns
    assert "math_trend" in columns
    assert "overall_gpa" in columns
    assert "persona" in columns
    assert "sma_track" in columns


def test_training_preprocessor_accepts_v2_frame():
    frame = build_dataset(rows=150, seed=12)
    columns = feature_columns_for(frame)
    preprocessor = build_preprocessor(frame[columns])
    transformed = preprocessor.fit_transform(frame[columns])

    assert transformed.shape[0] == len(frame)
    assert transformed.shape[1] >= len(columns)


def test_evaluate_models_reports_top5_accuracy():
    frame = build_dataset(rows=150, seed=12)
    columns = feature_columns_for(frame)
    labels = frame["kelompok_prodi"].astype("category").cat.codes.to_numpy()
    model = Pipeline([("preprocess", build_preprocessor(frame[columns])), ("model", DummyClassifier(strategy="stratified", random_state=1))])
    model.fit(frame[columns], labels)

    results, best_name = evaluate_models({"dummy": model}, frame[columns], labels)

    assert best_name == "dummy"
    assert "top5_accuracy" in results.columns
    assert np.isfinite(results.iloc[0]["top5_accuracy"])
