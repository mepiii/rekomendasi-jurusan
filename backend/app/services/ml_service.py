# Purpose: Load trained artifacts, normalize dynamic request data, and generate richer recommendation payloads + explainability.
# Callers: API predict endpoint and explainability background task.
# Deps: joblib, numpy, pandas, recommendation config, Pydantic schemas.
# API: predict(payload), build_explanations(payload, majors).
# Side effects: Reads model files during service initialization.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.config import settings
from app.recommendation_config import MAJOR_METADATA
from app.schemas import PredictRequest, ProfileSummary, RecommendationItem

DISCLAIMER_TEXT = (
    "These results support decision-making, not final judgment. "
    "Discuss them with a counselor, teacher, or parent."
)

MAJOR_CLUSTER_MAP = {major: meta["cluster"] for major, meta in MAJOR_METADATA.items()}
SUBJECT_LABELS = {
    "religion": "Pendidikan Agama",
    "civics": "PPKn",
    "pancasila": "Pancasila",
    "indonesian": "Bahasa Indonesia",
    "english": "Bahasa Inggris",
    "general_math": "Matematika Umum",
    "math": "Matematika",
    "basic_math": "Matematika Dasar",
    "advanced_math": "Matematika Lanjut",
    "pjok": "PJOK",
    "arts": "Seni",
    "biology": "Biologi",
    "physics": "Fisika",
    "chemistry": "Kimia",
    "economics": "Ekonomi",
    "sociology": "Sosiologi",
    "geography": "Geografi",
    "history": "Sejarah",
    "informatics": "Informatika",
    "anthropology": "Antropologi",
    "indonesian_literature": "Bahasa dan Sastra Indonesia",
    "english_literature": "Bahasa dan Sastra Inggris",
    "foreign_language": "Bahasa Asing",
    "advanced_language": "Bahasa Lanjut",
    "foreign_literature": "Sastra Asing",
    "entrepreneurship": "Kewirausahaan",
}

INTEREST_TO_COLUMN = {
    "Technology": "interest_technology",
    "Engineering": "interest_engineering",
    "Health": "interest_health",
    "Business": "interest_business",
    "Social": "interest_social",
    "Law": "interest_law",
    "Education": "interest_education",
    "Psychology": "interest_psychology",
    "Media": "interest_media",
    "Design": "interest_design",
    "Language": "interest_language",
    "Environment": "interest_environment",
    "Data / AI": "interest_data_ai",
}
PREFERENCE_TO_COLUMN = {
    "orientation": {"Numbers": "pref_orientation_numbers", "People": "pref_orientation_people", "Creativity": "pref_orientation_creativity"},
    "approach": {"Technical": "pref_approach_technical", "Social": "pref_approach_social"},
    "style": {"Teamwork": "pref_style_teamwork", "Independent": "pref_style_independent"},
}
BASE_FEATURE_COLUMNS = [
    "avg_score",
    "science_score",
    "social_score",
    "language_score",
    "humanities_score",
    "technical_score",
    "score_spread",
    "interest_count",
    "selected_elective_count",
    "track_ipa",
    "track_ips",
    "track_bahasa",
    "track_merdeka",
    *INTEREST_TO_COLUMN.values(),
    *(column for group in PREFERENCE_TO_COLUMN.values() for column in group.values()),
]
SHAP_FEATURE_LABELS = {
    "avg_score": "Average academic score",
    "science_score": "Science strength",
    "social_score": "Social studies strength",
    "language_score": "Language strength",
    "humanities_score": "Humanities breadth",
    "technical_score": "Technical readiness",
    "score_spread": "Score spread",
    "interest_count": "Interest breadth",
    "selected_elective_count": "Elective depth",
    "track_ipa": "IPA profile",
    "track_ips": "IPS profile",
    "track_bahasa": "Bahasa profile",
    "track_merdeka": "Merdeka profile",
}
SHAP_FEATURE_LABELS.update({value: key.replace("interest_", "Interest: ").replace("_", " ").title() for key, value in INTEREST_TO_COLUMN.items()})
SHAP_FEATURE_LABELS.update({column: column.replace("pref_", "Preference: ").replace("_", " ").title() for group in PREFERENCE_TO_COLUMN.values() for column in group.values()})


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
    def _preference_features(preferences: dict[str, str]) -> dict[str, int]:
        features = {column: 0 for group in PREFERENCE_TO_COLUMN.values() for column in group.values()}
        for group_name, group_map in PREFERENCE_TO_COLUMN.items():
            value = preferences.get(group_name)
            column = group_map.get(value)
            if column:
                features[column] = 1
        return features

    @staticmethod
    def _subject_groups(scores: dict[str, float]) -> dict[str, float]:
        science_keys = ["math", "general_math", "basic_math", "advanced_math", "physics", "chemistry", "biology", "informatics"]
        social_keys = ["economics", "sociology", "geography", "history", "anthropology", "pancasila", "civics"]
        language_keys = ["indonesian", "english", "indonesian_literature", "english_literature", "foreign_language", "advanced_language", "foreign_literature"]
        humanities_keys = ["religion", "arts", "history", "anthropology", "civics", "pancasila"]

        def average(keys: list[str]) -> float:
            values = [scores[key] for key in keys if key in scores]
            return round(sum(values) / len(values), 2) if values else 0.0

        return {
            "science_score": average(science_keys),
            "social_score": average(social_keys),
            "language_score": average(language_keys),
            "humanities_score": average(humanities_keys),
            "technical_score": average(["math", "general_math", "basic_math", "advanced_math", "physics", "chemistry", "informatics"]),
        }

    @staticmethod
    def _major_baseline_vector(major: str) -> dict[str, float]:
        cluster = MAJOR_CLUSTER_MAP.get(major, "Social")
        baselines = {
            "STEM": {"advanced_math": 84, "math": 82, "physics": 80, "chemistry": 76, "informatics": 78, "economics": 66, "english": 72},
            "Health": {"biology": 86, "chemistry": 82, "english": 74, "indonesian": 72, "math": 74},
            "Business": {"economics": 86, "math": 76, "english": 78, "indonesian": 76, "sociology": 70},
            "Arts": {"arts": 88, "language": 80, "indonesian": 82, "english": 80, "history": 72},
            "Social": {"english": 80, "indonesian": 82, "sociology": 78, "history": 76, "anthropology": 74},
        }
        return baselines.get(cluster, baselines["Social"])

    @staticmethod
    def _confidence_label(score: int) -> str:
        if score >= 80:
            return "High"
        if score >= 65:
            return "Medium"
        return "Emerging"

    def _build_profile_summary(self, req: PredictRequest) -> ProfileSummary:
        scores = {SUBJECT_LABELS.get(key, key): value for key, value in req.scores.items()}
        strongest_subject = max(scores, key=scores.get)
        grouped = self._subject_groups(req.scores)
        strongest_group = max(grouped, key=grouped.get).replace("_score", "").replace("_", " ")
        avg_score = round(sum(req.scores.values()) / len(req.scores), 1)
        return ProfileSummary(
            strongest_subject=strongest_subject,
            strongest_group=strongest_group,
            avg_score=avg_score,
            confidence_label=self._confidence_label(int(avg_score)),
        )

    def _generic_explanation(self, major: str, req: PredictRequest) -> str:
        strongest_subject = SUBJECT_LABELS.get(max(req.scores, key=req.scores.get), max(req.scores, key=req.scores.get))
        top_interest = req.interests[0] if req.interests else "your profile"
        return f"{major} stands out because your strongest academic signal is {strongest_subject} and it aligns with your interest in {top_interest}."

    def _fit_summary(self, req: PredictRequest, major: str) -> list[str]:
        summary = [f"Track: {req.sma_track}", f"Interest focus: {req.interests[0]}"]
        if req.selected_electives:
            summary.append(f"Electives: {', '.join(req.selected_electives[:2])}")
        summary.append(f"Preference: {req.preferences['approach']}")
        return summary

    def _to_feature_row(self, req: PredictRequest) -> pd.DataFrame:
        grouped = self._subject_groups(req.scores)
        score_values = list(req.scores.values())
        row = {
            "avg_score": round(sum(score_values) / len(score_values), 2),
            **grouped,
            "score_spread": max(score_values) - min(score_values),
            "interest_count": len(req.interests),
            "selected_elective_count": len(req.selected_electives),
            "track_ipa": int(req.sma_track == "IPA"),
            "track_ips": int(req.sma_track == "IPS"),
            "track_bahasa": int(req.sma_track == "Bahasa"),
            "track_merdeka": int(req.sma_track == "Merdeka"),
            **self._interest_features(req.interests),
            **self._preference_features(req.preferences),
        }
        return pd.DataFrame([row], columns=BASE_FEATURE_COLUMNS)

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
                rows.append({"major": major, "shap_values": self._vector_to_payload(vector, feature_names, top_k=top_k)})
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
        profile_summary = self._build_profile_summary(req)

        recommendations: list[RecommendationItem] = []
        for rank, index in enumerate(top_indices, start=1):
            major = str(class_labels[index])
            score = int(round(float(probabilities[index]) * 100))
            metadata = MAJOR_METADATA.get(major, {"cluster": "Other", "careers": [], "strengths": [], "tradeoffs": [], "alternatives": []})
            recommendations.append(
                RecommendationItem(
                    rank=rank,
                    major=major,
                    cluster=metadata["cluster"],
                    suitability_score=score,
                    confidence_label=self._confidence_label(score),
                    explanation=self._generic_explanation(major, req),
                    fit_summary=self._fit_summary(req, major),
                    strength_signals=metadata["strengths"],
                    tradeoffs=metadata["tradeoffs"],
                    career_paths=metadata["careers"],
                    alternative_majors=metadata["alternatives"],
                    shap_values={},
                    major_requirements=self._major_baseline_vector(major),
                )
            )

        return PredictionOutput(
            recommendations=recommendations,
            profile_summary=profile_summary,
            disclaimer=DISCLAIMER_TEXT,
            features=features.iloc[0].to_dict(),
        )


ml_service = MLService()
