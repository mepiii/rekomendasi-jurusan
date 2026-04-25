# Purpose: Train Apti v2 kelompok/prodi model artifacts from processed dataset.
# Callers: Manual ML refresh and retrain pipeline.
# Deps: argparse, joblib, pandas, sklearn.
# API: train_model.
# Side effects: Writes model, preprocessor, label encoder, metadata JSON.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

from topn_metrics import top_n_accuracy

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET = REPO_ROOT / "backend" / "ml" / "data" / "processed" / "apti_training_v2.csv"
MODEL_DIR = REPO_ROOT / "backend" / "ml" / "models"
METADATA_PATH = MODEL_DIR / "apti_model_metadata_v2.json"

TARGET = "target_kelompok_prodi"
DROP_COLUMNS = {"sample_id", "target_prodi", "target_prodi_id", "target_cluster", TARGET}


def _columns(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    features = [column for column in df.columns if column not in DROP_COLUMNS]
    numeric = [column for column in features if pd.api.types.is_numeric_dtype(df[column])]
    categorical = [column for column in features if column not in numeric]
    return numeric, categorical


def _pipeline(df: pd.DataFrame, classifier: Any) -> Pipeline:
    numeric, categorical = _columns(df)
    numeric_pipe = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    categorical_pipe = Pipeline([("imputer", SimpleImputer(strategy="constant", fill_value="missing")), ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric),
            ("cat", categorical_pipe, categorical),
        ]
    )
    return Pipeline([("preprocessor", preprocessor), ("classifier", classifier)])


def train_model(dataset: Path, model_version: str) -> dict[str, Any]:
    df = pd.read_csv(dataset)
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df[TARGET])
    x = df.drop(columns=[TARGET])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)

    candidates = {
        "dummy": DummyClassifier(strategy="most_frequent"),
        "logistic_regression": LogisticRegression(max_iter=800, n_jobs=None),
        "random_forest": RandomForestClassifier(n_estimators=240, random_state=42, class_weight="balanced_subsample", n_jobs=-1),
        "hist_gradient_boosting": HistGradientBoostingClassifier(random_state=42),
    }
    metrics: dict[str, Any] = {}
    trained: dict[str, Pipeline] = {}
    for name, classifier in candidates.items():
        pipe = _pipeline(x_train, classifier)
        pipe.fit(x_train, y_train)
        pred = pipe.predict(x_test)
        proba = pipe.predict_proba(x_test) if hasattr(pipe, "predict_proba") else None
        metrics[name] = {
            "accuracy": round(float(accuracy_score(y_test, pred)), 4),
            "macro_f1": round(float(f1_score(y_test, pred, average="macro", zero_division=0)), 4),
            "top3_accuracy": top_n_accuracy(label_encoder.inverse_transform(y_test).tolist(), label_encoder.classes_.tolist(), proba, 3) if proba is not None else None,
            "top5_accuracy": top_n_accuracy(label_encoder.inverse_transform(y_test).tolist(), label_encoder.classes_.tolist(), proba, 5) if proba is not None else None,
        }
        trained[name] = pipe

    best_name = max(metrics, key=lambda key: (metrics[key]["macro_f1"], metrics[key]["accuracy"]))
    best = trained[best_name]
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best, MODEL_DIR / "apti_group_model_v2.pkl")
    joblib.dump(best.named_steps["preprocessor"], MODEL_DIR / "apti_preprocessor_v2.pkl")
    joblib.dump(label_encoder, MODEL_DIR / "apti_label_encoder_group_v2.pkl")
    metadata = {
        "model_version": model_version,
        "dataset_version": str(df["dataset_version"].iloc[0]),
        "feature_version": "apti_features_v2",
        "training_rows": len(df),
        "classes": label_encoder.classes_.tolist(),
        "label_distribution": df[TARGET].value_counts().to_dict(),
        "best_model": best_name,
        "metrics": metrics,
        "random_state": 42,
        "hyperparameters": candidates[best_name].get_params(),
        "synthetic_real_ratio": "100:0",
    }
    METADATA_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--model-version", default="apti_v2")
    args = parser.parse_args()
    print(json.dumps(train_model(args.dataset, args.model_version), ensure_ascii=False, indent=2, default=str))
