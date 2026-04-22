# Purpose: Load trained artifacts, preprocess request data, and generate recommendations + async explainability payloads.
# Callers: API predict endpoint and explainability background task.
# Deps: joblib, numpy, pandas, Pydantic schemas.
# API: predict(payload), build_explanations(payload, majors).
# Side effects: Reads model files during service initialization.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.config import settings
from app.schemas import PredictRequest, ProfileSummary, RecommendationItem

DISCLAIMER_TEXT = (
    "Hasil ini adalah alat bantu pengambilan keputusan, bukan penentu final. "
    "Diskusikan dengan guru BK atau orang tua."
)

MAJOR_CLUSTER_MAP = {
    "Teknik Informatika": "STEM",
    "Sistem Informasi": "STEM",
    "Teknik Sipil": "STEM",
    "Teknik Elektro": "STEM",
    "Kedokteran": "Health",
    "Farmasi": "Health",
    "Biologi": "Health",
    "Matematika": "STEM",
    "Psikologi": "Social",
    "Ilmu Komunikasi": "Social",
    "Hukum": "Social",
    "Pendidikan Bahasa Inggris": "Social",
    "Manajemen": "Business",
    "Akuntansi": "Business",
    "Desain Komunikasi Visual": "Arts",
}

FEATURE_COLUMNS = [
    "math",
    "physics",
    "chemistry",
    "biology",
    "economics",
    "indonesian",
    "english",
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
    "sma_track",
    "avg_sains",
    "avg_sosial",
    "avg_bahasa",
    "gap_sains_sosial",
    "max_subject_score",
    "min_subject_score",
    "subject_score_spread",
    "interest_count",
]

INTEREST_TO_COLUMN = {
    "Teknologi": "interest_tech",
    "Data & AI": "interest_data_ai",
    "Rekayasa": "interest_engineering",
    "Sosial/Manusia": "interest_social",
    "Komunikasi": "interest_communication",
    "Hukum/Politik": "interest_law_politics",
    "Alam/Kesehatan": "interest_nature_health",
    "Bisnis/Manajemen": "interest_business",
    "Seni/Kreatif": "interest_arts",
    "Pendidikan/Bahasa": "interest_education_language",
}

SHAP_FEATURE_LABELS = {
    "math": "Matematika",
    "physics": "Fisika",
    "chemistry": "Kimia",
    "biology": "Biologi",
    "economics": "Ekonomi",
    "indonesian": "Bahasa Indonesia",
    "english": "Bahasa Inggris",
    "interest_tech": "Minat Teknologi",
    "interest_data_ai": "Minat Data & AI",
    "interest_engineering": "Minat Rekayasa",
    "interest_social": "Minat Sosial/Manusia",
    "interest_communication": "Minat Komunikasi",
    "interest_law_politics": "Minat Hukum/Politik",
    "interest_nature_health": "Minat Alam/Kesehatan",
    "interest_business": "Minat Bisnis/Manajemen",
    "interest_arts": "Minat Seni/Kreatif",
    "interest_education_language": "Minat Pendidikan/Bahasa",
    "avg_sains": "Rata-rata Sains",
    "avg_sosial": "Rata-rata Sosial",
    "avg_bahasa": "Rata-rata Bahasa",
    "gap_sains_sosial": "Gap Sains-Sosial",
    "max_subject_score": "Nilai Tertinggi",
    "min_subject_score": "Nilai Terendah",
    "subject_score_spread": "Sebaran Nilai",
    "interest_count": "Jumlah Minat",
}


@dataclass
class PredictionOutput:
    recommendations: list[RecommendationItem]
    profile_summary: ProfileSummary
    disclaimer: str
    features: dict[str, Any]


class MLService:
    def __init__(self) -> None:
        self.model = None
        self.label_encoder = None

    def load(self) -> None:
        self.model = joblib.load(settings.model_abs_path)
        self.label_encoder = joblib.load(settings.label_encoder_abs_path)

    @property
    def loaded(self) -> bool:
        return self.model is not None and self.label_encoder is not None

    @staticmethod
    def _interest_features(interests: list[str]) -> dict[str, int]:
        features = {column: 0 for column in INTEREST_TO_COLUMN.values()}
        for interest in interests:
            column = INTEREST_TO_COLUMN.get(interest)
            if column:
                features[column] = 1
        return features

    @staticmethod
    def _scores_dict(req: PredictRequest) -> dict[str, float]:
        return {
            "Matematika": req.scores.math,
            "Fisika": req.scores.physics,
            "Kimia": req.scores.chemistry,
            "Biologi": req.scores.biology,
            "Ekonomi": req.scores.economics,
            "Bahasa Indonesia": req.scores.indonesian,
            "Bahasa Inggris": req.scores.english,
        }

    @staticmethod
    def _major_baseline_vector(major: str) -> dict[str, float]:
        stem = {
            "math": 85,
            "physics": 85,
            "chemistry": 80,
            "biology": 72,
            "economics": 68,
            "indonesian": 72,
            "english": 75,
        }
        health = {
            "math": 78,
            "physics": 74,
            "chemistry": 82,
            "biology": 86,
            "economics": 66,
            "indonesian": 74,
            "english": 76,
        }
        social = {
            "math": 68,
            "physics": 62,
            "chemistry": 64,
            "biology": 66,
            "economics": 84,
            "indonesian": 84,
            "english": 82,
        }
        business = {
            "math": 76,
            "physics": 66,
            "chemistry": 68,
            "biology": 66,
            "economics": 88,
            "indonesian": 80,
            "english": 82,
        }
        arts = {
            "math": 62,
            "physics": 58,
            "chemistry": 60,
            "biology": 62,
            "economics": 74,
            "indonesian": 86,
            "english": 84,
        }

        cluster = MAJOR_CLUSTER_MAP.get(major, "Social")
        if cluster == "STEM":
            return stem
        if cluster == "Health":
            return health
        if cluster == "Business":
            return business
        if cluster == "Arts":
            return arts
        return social

    def _build_profile_summary(self, req: PredictRequest) -> ProfileSummary:
        scores = self._scores_dict(req)
        strongest_subject = max(scores, key=scores.get)

        avg_sains = (req.scores.math + req.scores.physics + req.scores.chemistry + req.scores.biology) / 4
        avg_sosial = (req.scores.economics + req.scores.indonesian) / 2
        avg_bahasa = (req.scores.indonesian + req.scores.english) / 2
        group_scores = {"sains": avg_sains, "sosial": avg_sosial, "bahasa": avg_bahasa}
        strongest_group = max(group_scores, key=group_scores.get)

        return ProfileSummary(
            strongest_subject=strongest_subject,
            strongest_group=strongest_group,
            avg_score=round(sum(scores.values()) / len(scores), 1),
        )

    @staticmethod
    def _generic_explanation(major: str, req: PredictRequest) -> str:
        scores = {
            "Matematika": req.scores.math,
            "Fisika": req.scores.physics,
            "Kimia": req.scores.chemistry,
            "Biologi": req.scores.biology,
            "Ekonomi": req.scores.economics,
            "Bahasa Indonesia": req.scores.indonesian,
            "Bahasa Inggris": req.scores.english,
        }
        top_subject = max(scores, key=scores.get)
        top_interest = req.interests[0] if req.interests else "profil akademik"
        return f"{major} direkomendasikan karena {top_subject} kuat dan minat {top_interest} konsisten."

    def _to_feature_row(self, req: PredictRequest) -> pd.DataFrame:
        avg_sains = (req.scores.math + req.scores.physics + req.scores.chemistry + req.scores.biology) / 4
        avg_sosial = (req.scores.economics + req.scores.indonesian) / 2
        avg_bahasa = (req.scores.indonesian + req.scores.english) / 2

        numeric_scores = [
            req.scores.math,
            req.scores.physics,
            req.scores.chemistry,
            req.scores.biology,
            req.scores.economics,
            req.scores.indonesian,
            req.scores.english,
        ]

        interest_features = self._interest_features(req.interests)

        row = {
            "math": req.scores.math,
            "physics": req.scores.physics,
            "chemistry": req.scores.chemistry,
            "biology": req.scores.biology,
            "economics": req.scores.economics,
            "indonesian": req.scores.indonesian,
            "english": req.scores.english,
            **interest_features,
            "sma_track": req.sma_track,
            "avg_sains": avg_sains,
            "avg_sosial": avg_sosial,
            "avg_bahasa": avg_bahasa,
            "gap_sains_sosial": avg_sains - avg_sosial,
            "max_subject_score": max(numeric_scores),
            "min_subject_score": min(numeric_scores),
            "subject_score_spread": max(numeric_scores) - min(numeric_scores),
            "interest_count": int(sum(interest_features.values())),
        }

        return pd.DataFrame([row], columns=FEATURE_COLUMNS)

    @staticmethod
    def _vector_to_payload(values: np.ndarray, feature_names: list[str], top_k: int = 4) -> dict[str, float]:
        abs_values = np.abs(np.asarray(values, dtype=float))
        top_idx = np.argsort(abs_values)[::-1][:top_k]
        total = float(abs_values[top_idx].sum()) if len(top_idx) else 0.0

        payload: dict[str, float] = {}
        for idx in top_idx:
            feature_name = feature_names[idx]
            label = SHAP_FEATURE_LABELS.get(feature_name, feature_name)
            contribution = float(abs_values[idx] / total * 100) if total > 0 else 0.0
            payload[label] = round(contribution, 2)
        return payload

    def build_explanations(self, req: PredictRequest, majors: list[str], top_k: int = 4) -> list[dict[str, Any]]:
        if not self.loaded or not majors:
            return []

        try:
            import shap

            features = self._to_feature_row(req)
            preprocess = self.model.named_steps["preprocess"]
            estimator = self.model.named_steps["model"]

            transformed = preprocess.transform(features)
            transformed_arr = transformed.toarray() if hasattr(transformed, "toarray") else np.asarray(transformed)
            feature_names = preprocess.get_feature_names_out().tolist()

            explainer = shap.TreeExplainer(estimator)
            shap_values = explainer.shap_values(transformed_arr)
            classes = list(self.label_encoder.classes_)

            rows: list[dict[str, Any]] = []
            for major in majors:
                if major not in classes:
                    rows.append({"major": major, "shap_values": {}})
                    continue

                class_idx = classes.index(major)

                if isinstance(shap_values, list):
                    vector = np.asarray(shap_values[class_idx])[0]
                elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
                    vector = np.asarray(shap_values)[0, class_idx, :]
                elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 2:
                    vector = np.asarray(shap_values)[0]
                else:
                    vector = np.asarray(transformed_arr)[0]

                rows.append(
                    {
                        "major": major,
                        "shap_values": self._vector_to_payload(vector, feature_names, top_k=top_k),
                    }
                )
            return rows
        except Exception:
            return []

    def predict(self, req: PredictRequest) -> PredictionOutput:
        if not self.loaded:
            raise RuntimeError("Model belum dimuat")

        features = self._to_feature_row(req)
        probabilities = self.model.predict_proba(features)[0]
        class_labels = self.label_encoder.classes_
        top_indices = np.argsort(probabilities)[::-1][: req.top_n]

        recommendations: list[RecommendationItem] = []
        for rank, index in enumerate(top_indices, start=1):
            major = str(class_labels[index])
            score = int(round(float(probabilities[index]) * 100))
            recommendations.append(
                RecommendationItem(
                    rank=rank,
                    major=major,
                    cluster=MAJOR_CLUSTER_MAP.get(major, "Lainnya"),
                    suitability_score=score,
                    explanation=self._generic_explanation(major, req),
                    shap_values={},
                    major_requirements=self._major_baseline_vector(major),
                )
            )

        return PredictionOutput(
            recommendations=recommendations,
            profile_summary=self._build_profile_summary(req),
            disclaimer=DISCLAIMER_TEXT,
            features=features.iloc[0].to_dict(),
        )


ml_service = MLService()
