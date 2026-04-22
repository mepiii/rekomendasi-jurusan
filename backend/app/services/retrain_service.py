# Purpose: Retrain model from synthetic + verified feedback with champion-vs-challenger checks.
# Callers: /api/retrain endpoint background task.
# Deps: pandas, joblib, sklearn, app.core.db, app.config.
# API: run_retrain(min_feedback_rows).
# Side effects: Writes new model artifacts when challenger wins.

from __future__ import annotations

from dataclasses import dataclass

import joblib
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

from app.config import settings
from app.core.db import count_feedback_rows, fetch_feedback_for_retrain
from ml.train_pipeline import (
    CATEGORICAL_COLUMNS,
    DERIVED_COLUMNS,
    INTEREST_COLUMNS,
    NUMERIC_COLUMNS,
    add_derived_features,
    evaluate_models,
    top_k_accuracy,
    train_models,
)


@dataclass
class RetrainResult:
    deployed: bool
    message: str


class RetrainService:
    @staticmethod
    def _fairness_disparate_impact(df: pd.DataFrame, prediction_col: str = "pred") -> float:
        track_rates: dict[str, float] = {}
        for track in ["IPA", "IPS", "Bahasa"]:
            group = df[df["sma_track"] == track]
            if group.empty:
                continue
            stem_rate = (group[prediction_col].isin(["Teknik Informatika", "Sistem Informasi", "Teknik Elektro", "Teknik Sipil", "Matematika"]).sum()) / len(group)
            track_rates[track] = float(stem_rate)

        if len(track_rates) < 2:
            return 1.0

        max_rate = max(track_rates.values())
        min_rate = min(track_rates.values())
        if max_rate == 0:
            return 1.0
        return round(min_rate / max_rate, 4)

    @staticmethod
    def _augment_with_feedback(df: pd.DataFrame, feedback_rows: list[dict]) -> pd.DataFrame:
        if not feedback_rows:
            return df

        sampled = df.sample(n=min(len(feedback_rows), 1000), replace=True, random_state=42).copy()
        selected = [row.get("selected_major") for row in feedback_rows if row.get("selected_major")]
        if selected:
            sampled["major"] = selected[: len(sampled)] + sampled["major"].tolist()[len(selected) :]
        return pd.concat([df, sampled], ignore_index=True)

    @staticmethod
    def _sample_weight_by_track(features: pd.DataFrame) -> pd.Series:
        counts = features["sma_track"].value_counts()
        if counts.empty:
            return pd.Series([1.0] * len(features), index=features.index, dtype=float)
        norm = float(len(features)) / float(len(counts))
        weight_map = {track: norm / float(count) for track, count in counts.items() if count > 0}
        return features["sma_track"].map(weight_map).fillna(1.0).astype(float)

    def run_retrain(self, min_feedback_rows: int = 100) -> RetrainResult:
        feedback_count = count_feedback_rows()
        if feedback_count < min_feedback_rows:
            return RetrainResult(
                deployed=False,
                message=f"feedback belum cukup ({feedback_count}/{min_feedback_rows})",
            )

        dataset_path = settings.model_abs_path.parents[1] / "data" / "training_dataset.csv"
        df = pd.read_csv(dataset_path)
        df = add_derived_features(df)

        feedback_rows = fetch_feedback_for_retrain(limit=5000)
        training_df = self._augment_with_feedback(df, feedback_rows)

        feature_columns = NUMERIC_COLUMNS + INTEREST_COLUMNS + CATEGORICAL_COLUMNS + DERIVED_COLUMNS
        x = training_df[feature_columns]
        y = training_df["major"]

        x_train, x_test, y_train, y_test = train_test_split(
            x,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        models = train_models(x_train, y_train)
        benchmark, champion_name = evaluate_models(models, x_test, y_test)
        challenger = models[champion_name]

        challenger_pred = challenger.predict(x_test)
        challenger_macro_f1 = float(f1_score(y_test, challenger_pred, average="macro"))
        challenger_top3 = float(top_k_accuracy(challenger, x_test, y_test, k=3))

        fairness_df = x_test.copy()
        fairness_df["pred"] = challenger_pred
        di_ratio = self._fairness_disparate_impact(fairness_df)

        current_model = joblib.load(settings.model_abs_path)
        current_pred = current_model.predict(x_test)
        current_macro_f1 = float(f1_score(y_test, current_pred, average="macro"))

        fairness_current = x_test.copy()
        fairness_current["pred"] = current_pred
        current_di = self._fairness_disparate_impact(fairness_current)

        baseline_gate = challenger_macro_f1 > current_macro_f1 and di_ratio >= current_di
        if baseline_gate:
            joblib.dump(challenger, settings.model_abs_path)
            return RetrainResult(
                deployed=True,
                message=(
                    f"challenger deployed | model={champion_name} macro_f1={challenger_macro_f1:.4f} "
                    f"top3={challenger_top3:.4f} fairness_di={di_ratio:.4f} benchmark_rows={len(benchmark)}"
                ),
            )

        weighted_models = train_models(x_train, y_train)
        train_weight = self._sample_weight_by_track(x_train)
        for model in weighted_models.values():
            estimator = model.named_steps.get("model")
            preprocess = model.named_steps.get("preprocess")
            transformed = preprocess.transform(x_train)
            try:
                estimator.fit(transformed, y_train, sample_weight=train_weight.to_numpy())
            except TypeError:
                continue

        _, weighted_name = evaluate_models(weighted_models, x_test, y_test)
        weighted_challenger = weighted_models[weighted_name]
        weighted_pred = weighted_challenger.predict(x_test)
        weighted_macro_f1 = float(f1_score(y_test, weighted_pred, average="macro"))
        weighted_top3 = float(top_k_accuracy(weighted_challenger, x_test, y_test, k=3))
        weighted_fairness_df = x_test.copy()
        weighted_fairness_df["pred"] = weighted_pred
        weighted_di = self._fairness_disparate_impact(weighted_fairness_df)

        weighted_gate = weighted_macro_f1 > current_macro_f1 and weighted_di >= current_di
        if weighted_gate:
            joblib.dump(weighted_challenger, settings.model_abs_path)
            return RetrainResult(
                deployed=True,
                message=(
                    f"weighted challenger deployed | model={weighted_name} macro_f1={weighted_macro_f1:.4f} "
                    f"top3={weighted_top3:.4f} fairness_di={weighted_di:.4f} benchmark_rows={len(benchmark)}"
                ),
            )

        return RetrainResult(
            deployed=False,
            message=(
                f"challenger ditolak | base_f1={challenger_macro_f1:.4f} base_di={di_ratio:.4f} "
                f"weighted_f1={weighted_macro_f1:.4f} weighted_di={weighted_di:.4f} "
                f"current_f1={current_macro_f1:.4f} current_di={current_di:.4f}"
            ),
        )


retrain_service = RetrainService()
