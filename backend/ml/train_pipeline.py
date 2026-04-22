# Purpose: Train and evaluate major recommendation model, then persist inference artifacts.
# Callers: Manual CLI execution after dataset generation.
# Deps: pandas, scikit-learn, joblib.
# API: python ml/train_pipeline.py --dataset path --model-out path --encoder-out path.
# Side effects: Writes trained model and label encoder files to disk.

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, OneHotEncoder

NUMERIC_COLUMNS = [
    "math",
    "physics",
    "chemistry",
    "biology",
    "economics",
    "indonesian",
    "english",
]

INTEREST_COLUMNS = [
    "interest_tech",
    "interest_data_ai",
    "interest_engineering",
    "interest_social",
    "interest_communication",
    "interest_law_politics",
    "interest_nature_health",
    "interest_business",
    "interest_arts",
    "interest_education_language",
]

CATEGORICAL_COLUMNS = ["sma_track"]

DERIVED_COLUMNS = [
    "avg_sains",
    "avg_sosial",
    "avg_bahasa",
    "gap_sains_sosial",
    "max_subject_score",
    "min_subject_score",
    "subject_score_spread",
    "interest_count",
]


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    copy = df.copy()

    copy["avg_sains"] = (copy["math"] + copy["physics"] + copy["chemistry"] + copy["biology"]) / 4
    copy["avg_sosial"] = (copy["economics"] + copy["indonesian"]) / 2
    copy["avg_bahasa"] = (copy["indonesian"] + copy["english"]) / 2
    copy["gap_sains_sosial"] = copy["avg_sains"] - copy["avg_sosial"]

    copy["max_subject_score"] = copy[NUMERIC_COLUMNS].max(axis=1)
    copy["min_subject_score"] = copy[NUMERIC_COLUMNS].min(axis=1)
    copy["subject_score_spread"] = copy["max_subject_score"] - copy["min_subject_score"]
    copy["interest_count"] = copy[INTEREST_COLUMNS].sum(axis=1)

    return copy


def top_k_accuracy(pipeline: Pipeline, x_test: pd.DataFrame, y_test: np.ndarray, k: int = 3) -> float:
    probas = pipeline.predict_proba(x_test)
    top_indices = np.argsort(probas, axis=1)[:, ::-1][:, :k]
    hits = [(y_test[i] in top_indices[i]) for i in range(len(y_test))]
    return float(np.mean(hits))


def build_preprocessor() -> ColumnTransformer:
    numeric_all = NUMERIC_COLUMNS + INTEREST_COLUMNS + DERIVED_COLUMNS
    return ColumnTransformer(
        transformers=[
            ("numeric", MinMaxScaler(), numeric_all),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
        ]
    )


def train_models(x_train: pd.DataFrame, y_train: np.ndarray) -> Dict[str, Pipeline]:
    preprocessor = build_preprocessor()

    models: Dict[str, Pipeline] = {
        "dummy_most_frequent": Pipeline(
            steps=[
                ("preprocess", preprocessor),
                ("model", DummyClassifier(strategy="most_frequent")),
            ]
        ),
        "knn_k7_distance": Pipeline(
            steps=[
                ("preprocess", preprocessor),
                ("model", KNeighborsClassifier(n_neighbors=7, weights="distance")),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("preprocess", preprocessor),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=500,
                        max_depth=20,
                        min_samples_leaf=2,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
        "extra_trees": Pipeline(
            steps=[
                ("preprocess", preprocessor),
                (
                    "model",
                    ExtraTreesClassifier(
                        n_estimators=600,
                        max_depth=None,
                        min_samples_leaf=1,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }

    for model in models.values():
        model.fit(x_train, y_train)

    return models


def evaluate_models(models: Dict[str, Pipeline], x_test: pd.DataFrame, y_test: np.ndarray) -> Tuple[pd.DataFrame, str]:
    rows = []
    best_name = ""
    best_score = -1.0

    for name, model in models.items():
        prediction = model.predict(x_test)
        accuracy = accuracy_score(y_test, prediction)
        macro_f1 = f1_score(y_test, prediction, average="macro")
        top3 = top_k_accuracy(model, x_test, y_test, k=3)

        composite = (top3 * 0.55) + (macro_f1 * 0.30) + (accuracy * 0.15)

        rows.append(
            {
                "model": name,
                "accuracy": round(float(accuracy), 4),
                "macro_f1": round(float(macro_f1), 4),
                "top3_accuracy": round(float(top3), 4),
                "composite": round(float(composite), 4),
            }
        )

        if composite > best_score:
            best_score = composite
            best_name = name

    frame = pd.DataFrame(rows).sort_values(by="composite", ascending=False).reset_index(drop=True)
    return frame, best_name


def parse_args() -> argparse.Namespace:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Train recommendation model")
    parser.add_argument("--dataset", type=Path, default=base / "data" / "training_dataset.csv")
    parser.add_argument("--model-out", type=Path, default=base / "models" / "rf_v1.0.pkl")
    parser.add_argument("--encoder-out", type=Path, default=base / "models" / "label_encoder.pkl")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.dataset)
    df = add_derived_features(df)

    feature_columns = NUMERIC_COLUMNS + INTEREST_COLUMNS + CATEGORICAL_COLUMNS + DERIVED_COLUMNS

    x = df[feature_columns]
    y_raw = df["major"]

    encoder = LabelEncoder()
    y = encoder.fit_transform(y_raw)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=args.seed,
        stratify=y,
    )

    models = train_models(x_train, y_train)
    results, best_name = evaluate_models(models, x_test, y_test)

    best_model = models[best_name]

    args.model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, args.model_out)
    joblib.dump(encoder, args.encoder_out)

    print("\nModel comparison")
    print(results.to_string(index=False))
    print(f"\nselected_model={best_name}")
    print(f"model_out={args.model_out}")
    print(f"encoder_out={args.encoder_out}")


if __name__ == "__main__":
    main()
