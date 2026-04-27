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

from app.recommendation_config import MAJOR_CLUSTER_MAP as CONFIG_MAJOR_CLUSTER_MAP, MAJOR_CLUSTERS, MAJOR_METADATA, RELIGION_RELATED_MAJORS
from app.schemas import DerivedAggregates, PredictRequest, ProfileSummary, RecommendationItem
from app.services.prodi_catalog_service import prodi_catalog_service
from app.services.prodi_profile_service import prodi_profile_service

DISCLAIMER_TEXT = (
    "These results support decision-making, not final judgment. "
    "Discuss them with a counselor, teacher, or parent."
)
GEMINI_EXPLANATION_PROMPT = """
Anda adalah asisten konseling akademik Apti untuk siswa SMA Indonesia. Jelaskan alasan rekomendasi jurusan dalam Bahasa Indonesia yang natural, singkat, dan aman.

Gunakan hanya data berikut: nilai siswa, minat, preferensi, jurusan, bobot/patokan jurusan, sinyal kekuatan, dan hal yang perlu ditinjau. Jangan menebak agama, identitas, status ekonomi, kesehatan, atau masa depan siswa. Jangan menyatakan kepastian. Jangan menjadi penentu final; selalu posisikan hasil sebagai bahan diskusi dengan guru BK, orang tua, atau konselor.

Format keluaran JSON:
{
  "summary": "2 kalimat alasan utama",
  "strengths": ["2-3 poin kekuatan berbasis data"],
  "tradeoffs": ["1-2 hal yang perlu ditinjau"],
  "next_steps": ["2 langkah eksplorasi praktis"]
}

Gaya: ramah, spesifik, tidak lebay, tidak menyalahkan siswa. Jika model ML tidak tersedia, sebutkan bahwa penjelasan memakai aturan cadangan tanpa istilah teknis.
""".strip()

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

OPTIONAL_SUBJECTS = {
    "regional_language": "has_regional_language",
    "arts_culture": "has_art",
    "pkwu": "has_pkwu",
    "prakarya": "has_pkwu",
    "pe": "has_pe",
    "religion_ethics": "has_religion_ethics",
    "informatics": "has_informatics",
}
OPTIONAL_FEATURE_COLUMNS = [
    *dict.fromkeys(OPTIONAL_SUBJECTS.values()),
    "avg_optional_available",
    "optional_subject_count",
    "optional_subject_boost",
    "optional_completeness_score",
]

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
    *OPTIONAL_FEATURE_COLUMNS,
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
    notes: list[str]
    fallback_used: bool
    disclaimer: str = DISCLAIMER_TEXT
    features: dict[str, Any] | None = None


class MLService:
    def __init__(self) -> None:
        self.model = None
        self.label_encoder = None
        self.load_error = None

    def load(self) -> None:
        try:
            from app.config import settings

            self.model = joblib.load(settings.model_abs_path)
            self.label_encoder = joblib.load(settings.label_encoder_abs_path)
        except Exception as exc:
            self.model = None
            self.label_encoder = None
            self.load_error = f"{type(exc).__name__}: {exc}"
        else:
            self.load_error = None

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
    def _preference_features(preferences: dict[str, str | list[str]]) -> dict[str, int]:
        features = {column: 0 for group in PREFERENCE_TO_COLUMN.values() for column in group.values()}
        for group_name, group_map in PREFERENCE_TO_COLUMN.items():
            values = preferences.get(group_name, [])
            for value in values if isinstance(values, list) else [values]:
                column = group_map.get(value)
                if column:
                    features[column] = 1
        return features

    @staticmethod
    def _semester_slope(points: list[tuple[int, float]]) -> float:
        if len(points) < 2:
            return 0.0
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        x_mean = sum(xs) / len(xs)
        y_mean = sum(ys) / len(ys)
        denominator = sum((x - x_mean) ** 2 for x in xs)
        if denominator == 0:
            return 0.0
        slope = sum((x - x_mean) * (y - y_mean) for x, y in points) / denominator
        return round(max(-1.0, min(1.0, slope / 10)), 3)

    def _rapor_aggregates(self, req: PredictRequest) -> DerivedAggregates:
        if not req.rapor:
            scores = {key: float(value) for key, value in req.scores.items() if value is not None}
            avg = round(sum(scores.values()) / len(scores), 2) if scores else 0.0
            return DerivedAggregates(subject_avg=scores, subject_trend={key: 0.0 for key in scores}, kelas_12_avg=avg, overall_gpa=avg)

        grouped: dict[str, list[tuple[int, float]]] = {}
        kelas_values = {10: [], 11: [], 12: []}
        for kelas, items in [(10, req.rapor.kelas_10), (11, req.rapor.kelas_11), (12, req.rapor.kelas_12)]:
            for item in items:
                if item.score is not None:
                    score = float(item.score)
                    grouped.setdefault(item.subject, []).append((item.semester, score))
                    kelas_values[kelas].append(score)
        subject_avg = {subject: round(sum(score for _, score in values) / len(values), 2) for subject, values in grouped.items()}
        subject_trend = {subject: self._semester_slope(values) for subject, values in grouped.items()}
        kelas_avg = {kelas: (sum(values) / len(values) if values else None) for kelas, values in kelas_values.items()}
        available_weight = sum(weight for kelas, weight in {10: 0.2, 11: 0.3, 12: 0.5}.items() if kelas_avg[kelas] is not None)
        overall_gpa = sum(float(kelas_avg[kelas]) * weight for kelas, weight in {10: 0.2, 11: 0.3, 12: 0.5}.items() if kelas_avg[kelas] is not None) / available_weight if available_weight else 0.0
        return DerivedAggregates(
            subject_avg=subject_avg,
            subject_trend=subject_trend,
            kelas_12_avg=round(float(kelas_avg[12] or overall_gpa), 2),
            overall_gpa=round(overall_gpa, 2),
        )

    @staticmethod
    def _subject_groups(scores: dict[str, float]) -> dict[str, float]:
        normalized = {**scores}
        for source, target in {
            "mathematics": "general_math",
            "bahasa_indonesia": "indonesian",
            "arts_culture": "arts",
            "religion_ethics": "religion",
            "civic": "civics",
            "ppkn": "civics",
        }.items():
            if source in scores and target not in normalized:
                normalized[target] = scores[source]
        science_keys = ["math", "general_math", "basic_math", "advanced_math", "physics", "chemistry", "biology", "informatics"]
        social_keys = ["economics", "sociology", "geography", "history", "anthropology", "pancasila", "civics"]
        language_keys = ["indonesian", "english", "indonesian_literature", "english_literature", "foreign_language", "advanced_language", "foreign_literature"]
        humanities_keys = ["religion", "arts", "history", "anthropology", "civics", "pancasila"]

        def average(keys: list[str]) -> float:
            values = [normalized[key] for key in keys if normalized.get(key) is not None]
            return round(sum(values) / len(values), 2) if values else 50.0

        return {
            "science_score": average(science_keys),
            "social_score": average(social_keys),
            "language_score": average(language_keys),
            "humanities_score": average(humanities_keys),
            "technical_score": average(["math", "general_math", "basic_math", "advanced_math", "physics", "chemistry", "informatics"]),
        }

    @staticmethod
    def _major_baseline_vector(major: str) -> dict[str, float]:
        cluster = CONFIG_MAJOR_CLUSTER_MAP.get(major, MAJOR_METADATA.get(major, {}).get("cluster", "Social / Humanities"))
        baselines = {
            "STEM": {"advanced_math": 84, "math": 82, "physics": 80, "chemistry": 76, "informatics": 78, "english": 72},
            "STEM / Technology": {"advanced_math": 84, "math": 82, "physics": 80, "chemistry": 76, "informatics": 78, "english": 72},
            "Health": {"biology": 86, "chemistry": 82, "english": 74, "indonesian": 72, "math": 74},
            "Health / Natural Science": {"biology": 86, "chemistry": 82, "english": 74, "indonesian": 72, "math": 74},
            "Business": {"economics": 86, "math": 76, "english": 78, "indonesian": 76, "sociology": 70},
            "Business / Economy": {"economics": 86, "math": 76, "english": 78, "indonesian": 76, "sociology": 70},
            "Arts": {"arts": 88, "indonesian": 82, "english": 80, "history": 72},
            "Creative": {"arts": 88, "indonesian": 82, "english": 80, "history": 72},
            "Social": {"english": 80, "indonesian": 82, "sociology": 78, "history": 76, "anthropology": 74},
            "Social / Humanities": {"english": 80, "indonesian": 82, "sociology": 78, "history": 76, "anthropology": 74},
            "Language / Culture": {"indonesian": 84, "english": 84, "history": 74, "anthropology": 74},
            "Education": {"indonesian": 82, "english": 78, "sociology": 74, "history": 72},
            "Religion-related": {"religion": 86, "indonesian": 80, "history": 76, "civics": 74},
        }
        base = baselines.get(cluster, baselines["Social / Humanities"])
        overrides = {
            "Medicine": {"biology": 92, "chemistry": 86, "english": 76, "indonesian": 74},
            "Biology": {"biology": 90, "chemistry": 78, "math": 72, "english": 72},
            "Pharmacy": {"chemistry": 90, "biology": 82, "math": 76, "english": 72},
            "Computer Science": {"informatics": 92, "advanced_math": 88, "math": 84, "english": 74},
            "Information Systems": {"informatics": 84, "economics": 78, "math": 76, "english": 76},
            "Civil Engineering": {"physics": 88, "math": 84, "advanced_math": 82, "english": 70},
            "Electrical Engineering": {"physics": 90, "advanced_math": 86, "informatics": 78, "english": 70},
            "Mathematics": {"advanced_math": 92, "math": 90, "informatics": 72, "english": 68},
            "Psychology": {"sociology": 84, "biology": 74, "indonesian": 80, "english": 76},
            "Communication Studies": {"indonesian": 86, "english": 82, "sociology": 78, "history": 72},
            "Law": {"indonesian": 88, "civics": 84, "history": 80, "english": 76},
            "English Education": {"english": 90, "indonesian": 80, "sociology": 72, "history": 70},
            "Management": {"economics": 84, "math": 74, "english": 78, "sociology": 72},
            "Accounting": {"economics": 86, "math": 82, "english": 74, "indonesian": 72},
            "Visual Communication Design": {"arts": 92, "indonesian": 78, "english": 76, "history": 70},
        }
        return overrides.get(major, base)

    @staticmethod
    def _confidence_label(score: int) -> str:
        if score >= 80:
            return "High"
        if score >= 65:
            return "Medium"
        return "Emerging"

    def _build_profile_summary(self, req: PredictRequest) -> ProfileSummary:
        valid_scores = {key: value for key, value in req.scores.items() if value is not None}
        strongest_key = self._strongest_subject_key(valid_scores, None)
        scores = {SUBJECT_LABELS.get(key, key): value for key, value in valid_scores.items()}
        strongest_subject = SUBJECT_LABELS.get(strongest_key, strongest_key) if strongest_key else None
        grouped = self._subject_groups(req.scores)
        strongest_group = max(grouped, key=grouped.get).replace("_score", "").replace("_", " ")
        avg_score = round(sum(scores.values()) / len(scores), 1) if scores else 0.0
        return ProfileSummary(
            strongest_subject=strongest_subject,
            strongest_group=strongest_group,
            avg_score=avg_score,
            confidence_label=self._confidence_label(int(avg_score)),
        )

    def _religion_preference(self, req: PredictRequest) -> str:
        value = req.preferences.get("religion_related_major_preference", "Other / unsure")
        return str(value[0] if isinstance(value, list) and value else value)

    @staticmethod
    def _is_religion_major(major: str) -> bool:
        return major in RELIGION_RELATED_MAJORS or CONFIG_MAJOR_CLUSTER_MAP.get(major) == "Religion-related"

    def _strongest_subject_key(self, scores: dict[str, float], major: str | None) -> str | None:
        if not scores:
            return None
        religion_context = major is not None and self._is_religion_major(major)
        priority = [
            "advanced_math",
            "math",
            "general_math",
            "basic_math",
            "physics",
            "chemistry",
            "biology",
            "informatics",
            "economics",
            "sociology",
            "geography",
            "history",
            "indonesian",
            "english",
            "arts",
            "anthropology",
            "civics",
            "pancasila",
        ]
        if religion_context:
            priority.insert(0, "religion")
        candidates = [key for key in scores if religion_context or key not in {"religion", "religion_ethics"}]
        if not candidates:
            candidates = list(scores)
        return max(candidates, key=lambda key: (scores[key], -priority.index(key) if key in priority else -len(priority)))

    def _generic_explanation(self, major: str, req: PredictRequest) -> str:
        scores = {key: value for key, value in req.scores.items() if value is not None}
        strongest_key = self._strongest_subject_key(scores, major) or "your profile"
        strongest_subject = SUBJECT_LABELS.get(strongest_key, strongest_key)
        top_interest = req.interests[0] if req.interests else "your profile"
        if self._is_religion_major(major):
            return f"{major} is included because your selected preference is {self._religion_preference(req)} and your academic signal includes {strongest_subject}."
        return f"{major} stands out because your strongest academic signal is {strongest_subject} and it aligns with your interest in {top_interest}."

    def _fit_summary(self, req: PredictRequest, major: str) -> list[str]:
        interest_focus = req.interests[0] if req.interests else "General exploration"
        summary = [f"Track: {req.sma_track}", f"Interest focus: {interest_focus}"]
        if req.selected_electives:
            summary.append(f"Electives: {', '.join(req.selected_electives[:2])}")
        preference = req.preferences.get("approach", "Flexible approach")
        if isinstance(preference, list):
            preference = ", ".join(str(item) for item in preference) if preference else "Flexible approach"
        summary.append(f"Preference: {preference}")
        return summary

    @staticmethod
    def _optional_subject_features(scores: dict[str, float | None]) -> dict[str, float | int]:
        available = [scores[subject] for subject in OPTIONAL_SUBJECTS if scores.get(subject) is not None]
        flags = {flag: 0 for flag in dict.fromkeys(OPTIONAL_SUBJECTS.values())}
        for subject, flag in OPTIONAL_SUBJECTS.items():
            if scores.get(subject) is not None:
                flags[flag] = 1
        count = len(available)
        avg_available = round(sum(available) / count, 2) if available else 0.0
        return {
            **flags,
            "avg_optional_available": avg_available,
            "optional_subject_count": count,
            "optional_subject_boost": max(50, round(avg_available, 2)) if count else 50,
            "optional_completeness_score": round(count / len(OPTIONAL_SUBJECTS) * 100, 2),
        }

    def _to_feature_row(self, req: PredictRequest) -> pd.DataFrame:
        grouped = self._subject_groups(req.scores)
        score_values = [score for score in req.scores.values() if score is not None]
        row = {
            "avg_score": round(sum(score_values) / len(score_values), 2) if score_values else 0.0,
            **grouped,
            "score_spread": max(score_values) - min(score_values) if score_values else 0.0,
            "interest_count": len(req.interests),
            "selected_elective_count": len(req.selected_electives),
            **self._optional_subject_features(req.scores),
            "track_ipa": int(req.sma_track == "IPA"),
            "track_ips": int(req.sma_track == "IPS"),
            "track_bahasa": int(req.sma_track == "Bahasa"),
            "track_merdeka": int(req.sma_track == "Merdeka"),
            **self._interest_features(req.interests),
            **self._preference_features(req.preferences),
        }
        return pd.DataFrame([row], columns=BASE_FEATURE_COLUMNS)

    def _to_v2_feature_row(self, req: PredictRequest) -> pd.DataFrame:
        def score(*keys: str) -> float | None:
            for key in keys:
                if req.scores.get(key) is not None:
                    return float(req.scores[key])
            return None

        row = {
            "academic_confidence": str(req.academic_context.get("note", "balanced")),
            "ambiguity_flag": False,
            "career_priorities": "|".join(str(item) for value in req.career_direction.values() for item in (value if isinstance(value, list) else [value])) or "balanced",
            "constraints": str(req.constraints.get("note", "balanced")),
            "curriculum_type": req.curriculum_type or req.sma_track,
            "dataset_version": "apti_dataset_v2",
            "expected_prodi": req.expected_prodi or "none",
            "free_text_goal_keywords": req.free_text_goal or "",
            "interest_deep_dive": "|".join(str(item) for value in req.interest_deep_dive.values() for item in (value if isinstance(value, list) else [value])),
            "interests": "|".join(req.interests),
            "prodi_to_avoid": "|".join(req.prodi_to_avoid) or "none",
            "quality_flag": "runtime",
            "sample_id": "runtime",
            "score_advanced_math": score("advanced_math", "mathematics_advanced"),
            "score_anthropology": score("anthropology"),
            "score_arts": score("arts", "arts_culture"),
            "score_bahasa": score("indonesian", "bahasa_indonesia"),
            "score_biology": score("biology"),
            "score_chemistry": score("chemistry"),
            "score_civics": score("civics", "pancasila"),
            "score_economics": score("economics"),
            "score_english": score("english"),
            "score_foreign_language": score("foreign_language", "advanced_language"),
            "score_geography": score("geography"),
            "score_history": score("history"),
            "score_indonesian": score("indonesian", "bahasa_indonesia"),
            "score_informatics": score("informatics"),
            "score_kesehatan": score("health"),
            "score_math": score("math", "general_math", "basic_math", "mathematics"),
            "score_olahraga": score("pjok", "pe"),
            "score_paling_banyak_1_mata_pelajaran_pendukung_yang_relevan_dengan_program_studi_kependidikannya": None,
            "score_pattern": "runtime",
            "score_pendidikan_jasmani": score("pjok", "pe"),
            "score_physics": score("physics"),
            "score_pjok": score("pjok", "pe"),
            "score_religion": score("religion", "religion_ethics"),
            "score_sastra_inggris": score("english_literature"),
            "score_sociology": score("sociology"),
            "sma_track": req.sma_track,
            "source_type": "runtime",
            "target_cluster": "unknown",
            "target_kelompok_prodi": "unknown",
            "target_prodi": "unknown",
            "target_prodi_id": "unknown",
            "work_style": str(req.preferences.get("style", "balanced")),
        }
        return pd.DataFrame([row])

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
        if not majors:
            return []
        if not self.loaded:
            return [{"major": major, "shap_values": {"Rule-based explanation": 100.0}} for major in majors]
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


    @staticmethod
    def _match_level(score: int) -> str:
        if score >= 85:
            return "Strong match"
        if score >= 70:
            return "Good match"
        if score >= 55:
            return "Moderate match"
        return "Exploratory match"

    @staticmethod
    def _weighted_score(breakdown: dict[str, int]) -> int:
        score = (
            breakdown.get("model_score", 0) * 0.45
            + breakdown.get("academic_fit_score", 0) * 0.25
            + breakdown.get("interest_fit_score", 0) * 0.15
            + breakdown.get("preference_fit_score", 0) * 0.10
            + breakdown.get("optional_subject_boost", 0) * 0.05
        )
        return max(0, min(100, int(round(score))))

    def _fallback_model_score(self, req: PredictRequest, major: str, index: int) -> int:
        academic = self._academic_fit_score(req, major)
        interest = self._interest_fit_score(req, major)
        preference = self._preference_fit_score(req, major)
        track_bonus = 4 if CONFIG_MAJOR_CLUSTER_MAP.get(major) in {
            "STEM / Technology" if req.sma_track == "IPA" else "",
            "Health / Natural Science" if req.sma_track == "IPA" else "",
            "Business / Economy" if req.sma_track == "IPS" else "",
            "Social / Humanities" if req.sma_track == "IPS" else "",
            "Language / Culture" if req.sma_track == "Bahasa" else "",
            "Education" if req.sma_track == "Bahasa" else "",
        } else 0
        score = academic * 0.42 + interest * 0.33 + preference * 0.20 + track_bonus - min(index, 8)
        return max(35, min(95, int(round(score))))

    def _fallback_candidates(self, req: PredictRequest) -> list[str]:
        interest_clusters = {
            "Technology": "STEM / Technology",
            "Data / AI": "STEM / Technology",
            "Engineering": "STEM / Technology",
            "Health": "Health / Natural Science",
            "Business": "Business / Economy",
            "Social": "Social / Humanities",
            "Law": "Social / Humanities",
            "Psychology": "Social / Humanities",
            "Media": "Social / Humanities",
            "Language": "Language / Culture",
            "Design": "Creative",
            "Education": "Education",
            "Environment": "Health / Natural Science",
        }
        candidates: list[str] = []
        religion_preference = self._religion_preference(req)
        if religion_preference != "Not relevant":
            candidates.extend(MAJOR_CLUSTERS["Religion-related"])
        if religion_preference == "Islamic studies / education":
            candidates = ["Islamic Education", "Islamic Studies", *candidates]
        for interest in req.interests:
            candidates.extend(MAJOR_CLUSTERS.get(interest_clusters.get(interest, ""), []))
        if req.sma_track == "IPA":
            candidates.extend(MAJOR_CLUSTERS["STEM / Technology"] + MAJOR_CLUSTERS["Health / Natural Science"])
        elif req.sma_track == "IPS":
            candidates.extend(MAJOR_CLUSTERS["Business / Economy"] + MAJOR_CLUSTERS["Social / Humanities"])
        elif req.sma_track == "Bahasa":
            candidates.extend(MAJOR_CLUSTERS["Language / Culture"] + MAJOR_CLUSTERS["Education"])
        else:
            candidates.extend(MAJOR_CLUSTERS["STEM / Technology"] + MAJOR_CLUSTERS["Business / Economy"])
        unique = list(dict.fromkeys(candidates + ["Computer Science", "Management", "Psychology", "Communication Studies", "Accounting"]))
        return unique[: max(5, req.top_n * 2)]

    @staticmethod
    def _spread_scores(recommendations: list[RecommendationItem]) -> list[RecommendationItem]:
        spread: list[RecommendationItem] = []
        previous = 101
        for index, item in enumerate(recommendations):
            score = max(0, min(100, item.suitability_score - min(index, 4)))
            if score >= previous:
                score = max(0, previous - 1)
            previous = score
            spread.append(item.model_copy(update={"suitability_score": score, "match_level": MLService._match_level(score)}))
        return spread

    def _apply_sanity_layer(self, req: PredictRequest, recommendations: list[RecommendationItem]) -> list[RecommendationItem]:
        preference = self._religion_preference(req)
        if preference == "Not relevant":
            existing = {item.major for item in recommendations}
            fillers = [
                self._build_recommendation(req, len(recommendations) + index, major, 45)
                for index, major in enumerate(self._fallback_candidates(req), start=1)
                if not self._is_religion_major(major) and major not in existing
            ]
            adjusted = [
                item.model_copy(update={"suitability_score": max(0, item.suitability_score - 50)})
                if self._is_religion_major(item.major)
                else item
                for item in [*recommendations, *fillers]
            ]
        elif preference == "Islamic studies / education":
            preferred = {"Islamic Education", "Islamic Studies"}
            adjusted = [
                item.model_copy(update={"suitability_score": min(100, item.suitability_score + 12)})
                if item.major in preferred
                else item
                for item in recommendations
            ]
        else:
            adjusted = recommendations
        ranked = self._spread_scores(sorted(adjusted, key=lambda item: item.suitability_score, reverse=True))
        return [item.model_copy(update={"rank": rank}) for rank, item in enumerate(ranked, start=1)]

    @staticmethod
    def _civic_humanities_score(scores: dict[str, float | None]) -> float:
        values = [scores[key] for key in ["arts", "history", "anthropology", "civics", "pancasila"] if scores.get(key) is not None]
        return round(sum(values) / len(values), 2) if values else 50.0

    def _major_weighted_score(self, req: PredictRequest, major: str) -> int:
        requirements = self._major_baseline_vector(major)
        pairs = [(float(req.scores[key]), float(target)) for key, target in requirements.items() if req.scores.get(key) is not None]
        if not pairs:
            return 50
        scores = [max(0, min(100, score + (score - target) * 0.35)) for score, target in pairs]
        return max(0, min(100, int(round(sum(scores) / len(scores)))))

    def _academic_fit_score(self, req: PredictRequest, major: str) -> int:
        grouped = self._subject_groups(req.scores)
        cluster = CONFIG_MAJOR_CLUSTER_MAP.get(major, MAJOR_METADATA.get(major, {}).get("cluster", "Social"))
        if "STEM" in cluster or cluster == "STEM":
            value = (grouped["science_score"] + grouped["technical_score"]) / 2
        elif "Health" in cluster:
            value = grouped["science_score"]
        elif "Business" in cluster:
            value = (grouped["social_score"] + grouped["technical_score"]) / 2
        elif "Language" in cluster:
            value = grouped["language_score"]
        elif "Creative" in cluster:
            value = (grouped["humanities_score"] + grouped["language_score"]) / 2
        elif cluster in {"Social / Humanities", "Social"}:
            civic_humanities = self._civic_humanities_score(req.scores)
            value = (grouped["social_score"] + civic_humanities + grouped["language_score"]) / 3
        elif self._is_religion_major(major):
            religion_score = req.scores.get("religion") or req.scores.get("religion_ethics") or grouped["humanities_score"]
            value = (float(religion_score) + grouped["language_score"] + grouped["social_score"]) / 3
        else:
            value = (grouped["social_score"] + grouped["humanities_score"] + grouped["language_score"]) / 3
        cluster_score = max(0, min(100, int(round(value))))
        major_score = self._major_weighted_score(req, major)
        return max(0, min(100, int(round(cluster_score * 0.55 + major_score * 0.45))))

    def _interest_fit_score(self, req: PredictRequest, major: str) -> int:
        text = f"{major} {CONFIG_MAJOR_CLUSTER_MAP.get(major, '')} {MAJOR_METADATA.get(major, {}).get('cluster', '')}".lower()
        score = 55
        keyword_map = {
            "Technology": ["computer", "information", "data", "cyber", "technology", "engineering"],
            "Data / AI": ["data", "computer", "statistics", "mathematics", "ai"],
            "Engineering": ["engineering", "architecture"],
            "Health": ["medicine", "nursing", "pharmacy", "health", "biology"],
            "Business": ["business", "management", "accounting", "finance", "economics"],
            "Social": ["social", "psychology", "communication", "sociology"],
            "Law": ["law"],
            "Education": ["education", "teacher"],
            "Psychology": ["psychology", "counseling"],
            "Media": ["communication", "media", "film"],
            "Design": ["design", "creative", "visual", "animation"],
            "Language": ["language", "literature", "linguistics", "translation"],
            "Environment": ["environment", "biology", "civil"],
        }
        for interest in req.interests:
            if any(keyword in text for keyword in keyword_map.get(interest, [])):
                score += 18
        return max(0, min(100, score))

    def _preference_fit_score(self, req: PredictRequest, major: str) -> int:
        values = [item for value in req.preferences.values() for item in (value if isinstance(value, list) else [value])]
        text = f"{major} {CONFIG_MAJOR_CLUSTER_MAP.get(major, '')}".lower()
        score = 60
        if "Numbers" in values and any(word in text for word in ["computer", "data", "math", "engineering", "accounting", "finance"]):
            score += 15
        if "Technical" in values and any(word in text for word in ["computer", "engineering", "technology", "science"]):
            score += 15
        if "Creativity" in values and any(word in text for word in ["design", "creative", "media", "communication"]):
            score += 15
        if "People" in values and any(word in text for word in ["psychology", "education", "medicine", "communication", "law"]):
            score += 15
        if "Independent" in values and any(word in text for word in ["computer", "data", "math", "literature"]):
            score += 5
        return max(0, min(100, score))

    def _explanation_bullets(self, req: PredictRequest, major: str, breakdown: dict[str, int]) -> list[str]:
        bullets = [self._generic_explanation(major, req)]
        baseline = self._major_baseline_vector(major)
        scored = [
            (SUBJECT_LABELS.get(subject, subject), int(req.scores[subject] - target))
            for subject, target in baseline.items()
            if req.scores.get(subject) is not None
        ]
        if scored:
            label, gap = max(scored, key=lambda item: item[1])
            direction = "above" if gap >= 0 else "near"
            bullets.append(f"{label} is {direction} this major benchmark by {abs(gap)} points.")
        bullets.append(f"Academic fit contributes {breakdown['academic_fit_score']}/100 based on major-relevant subjects.")
        if req.interests:
            bullets.append(f"Interest fit reflects your stated focus: {', '.join(req.interests[:3])}.")
        return bullets

    def _tradeoffs_for_major(self, major: str) -> list[str]:
        metadata = MAJOR_METADATA.get(major)
        if metadata and metadata.get("tradeoffs"):
            return metadata["tradeoffs"]
        return ["This major may require extra exploration because detailed program metadata is limited."]

    def _build_recommendation(self, req: PredictRequest, rank: int, major: str, model_score: int = 50) -> RecommendationItem:
        academic = self._academic_fit_score(req, major)
        interest = self._interest_fit_score(req, major)
        preference = self._preference_fit_score(req, major)
        optional = int(self._optional_subject_features(req.scores)["optional_subject_boost"])
        breakdown = {
            "model_score": model_score,
            "academic_fit_score": academic,
            "interest_fit_score": interest,
            "preference_fit_score": preference,
            "optional_subject_boost": optional,
        }
        suitability = self._weighted_score(breakdown)
        metadata = MAJOR_METADATA.get(major, {})
        cluster = CONFIG_MAJOR_CLUSTER_MAP.get(major, metadata.get("cluster", "General"))
        return RecommendationItem(
            rank=rank,
            major=major,
            cluster=cluster,
            suitability_score=suitability,
            match_level=self._match_level(suitability),
            score_breakdown=breakdown,
            confidence_label=self._confidence_label(suitability),
            explanation=self._explanation_bullets(req, major, breakdown),
            fit_summary=self._fit_summary(req, major),
            strength_signals=metadata.get("strengths", []),
            tradeoffs=self._tradeoffs_for_major(major),
            career_paths=metadata.get("careers", [f"{major} specialist", "Program coordinator"]),
            alternative_majors=metadata.get("alternatives", [candidate for candidate in self._fallback_candidates(req) if candidate != major][:2]),
            caution="This recommendation is an exploration aid, not a final decision.",
            shap_values={},
            major_requirements=self._major_baseline_vector(major),
            user_scores={key: float(value) for key, value in req.scores.items() if value is not None},
        )

    @staticmethod
    def _score_value(scores: dict[str, float | None], subject: str) -> float | None:
        values = [float(scores[key]) for key in MLService._subject_key_candidates(subject) if scores.get(key) is not None]
        return max(values) if values else None

    @staticmethod
    def _subject_key_candidates(subject: str) -> list[str]:
        aliases = {
            "mathematics": ["math", "general_math", "basic_math", "advanced_math"],
            "mathematics_advanced": ["advanced_math"],
            "bahasa_indonesia": ["indonesian"],
            "bahasa_indonesia_advanced": ["indonesian_literature"],
            "english_advanced": ["english_literature"],
            "arts_culture": ["arts"],
            "religion_ethics": ["religion"],
            "pe": ["pjok"],
        }
        return [subject, *aliases.get(subject, [])]

    def _score_prodi_profile(self, req: PredictRequest, profile: dict[str, Any], model_score: int = 55) -> RecommendationItem:
        aggregates = self._rapor_aggregates(req)
        academic_requirements = prodi_profile_service.academic_requirements(profile["prodi_id"])
        academic_weights = profile.get("academic_weights", {})
        requirement_items = [(group, subject, values) for group, subjects in academic_requirements.items() for subject, values in subjects.items()]
        scored_subjects = []
        score_gaps = []
        unmet_primary = []
        for group, subject, values in requirement_items:
            score = self._score_value(req.scores, subject)
            if score is None:
                continue
            weight = float(values.get("weight", academic_weights.get(subject, 0.3)))
            benchmark = float(values.get("benchmark", 75))
            scored_subjects.append((min(100, score / benchmark * 100), weight))
            if min_score := values.get("min_score"):
                gap = round(float(score) - float(min_score), 2)
                score_gaps.append({"subject": subject, "score": round(float(score), 2), "min_score": float(min_score), "gap": gap})
                if group == "primary" and gap < 0:
                    unmet_primary.append(subject)
        weight_total = sum(weight for _, weight in scored_subjects)
        academic = int(round(sum(score * weight for score, weight in scored_subjects) / weight_total)) if weight_total else 55
        tier = prodi_profile_service.tier(profile["prodi_id"])
        eligibility_penalty = 12 if tier == "competitive" and unmet_primary else 0
        trend_subjects = prodi_profile_service.trend_bonus_subjects(profile["prodi_id"]) or [subject for _, subject, _ in requirement_items[:3]]
        trends = [next((aggregates.subject_trend[key] for key in self._subject_key_candidates(subject) if key in aggregates.subject_trend), 0.0) for subject in trend_subjects]
        trend = int(round(50 + (sum(trends) / len(trends) * 50 if trends else 0)))
        trend = max(0, min(100, trend))
        min_gpa = prodi_profile_service.min_gpa(profile["prodi_id"])
        gpa = int(round(min(100, aggregates.overall_gpa / min_gpa * 100))) if min_gpa else int(aggregates.overall_gpa)
        gpa = max(0, min(100, gpa))

        free_text_values = [
            str(value)
            for source in [req.academic_context, req.subject_preferences, req.interest_deep_dive, req.career_direction, req.constraints]
            for value in source.values()
            for value in (value if isinstance(value, list) else [value])
        ]
        interest_values = " ".join([*req.interests, *free_text_values, req.expected_prodi or "", req.free_text_goal or ""]).lower()
        interest_aliases = {
            "technology": "technology_digital",
            "teknologi": "technology_digital",
            "computer": "technology_digital",
            "komputer": "technology_digital",
            "informatics": "technology_digital",
            "informatika": "technology_digital",
            "data / ai": "tech_ai_data",
            "ai / data": "tech_ai_data",
            "artificial intelligence": "tech_ai_data",
            "kecerdasan artifisial": "tech_ai_data",
            "sains data": "tech_ai_data",
            "data science": "tech_ai_data",
            "programming": "tech_software",
            "software": "tech_software",
            "perangkat lunak": "tech_software",
            "cybersecurity": "tech_software",
            "keamanan siber": "tech_software",
            "engineering": "engineering",
            "teknik": "engineering",
            "robotics": "engineering",
            "robotika": "engineering",
            "sipil": "engineering",
            "health": "health_life_science",
            "kesehatan": "health_life_science",
            "medicine": "health_life_science",
            "kedokteran": "health_life_science",
            "pharmacy": "health_life_science",
            "farmasi": "health_life_science",
            "biology": "health_life_science",
            "biologi": "health_life_science",
            "business": "business_management",
            "bisnis": "business_management",
            "management": "business_management",
            "manajemen": "business_management",
            "accounting": "business_management",
            "akuntansi": "business_management",
            "finance": "business_management",
            "keuangan": "business_management",
            "law": "social_law",
            "hukum": "social_law",
            "policy": "social_law",
            "kebijakan": "social_law",
            "psychology": "social_psychology",
            "psikologi": "social_psychology",
            "counseling": "social_psychology",
            "konseling": "social_psychology",
            "communication": "social_communication",
            "komunikasi": "social_communication",
            "media": "social_communication",
            "public speaking": "social_communication",
            "design": "creative_design",
            "desain": "creative_design",
            "visual": "creative_design",
            "creative": "creative_design",
            "kreatif": "creative_design",
            "language": "language_culture",
            "bahasa": "language_culture",
            "literature": "language_culture",
            "sastra": "language_culture",
            "translation": "language_culture",
            "penerjemahan": "language_culture",
            "education": "education_teaching",
            "pendidikan": "education_teaching",
            "teaching": "education_teaching",
            "mengajar": "education_teaching",
            "mentoring": "education_teaching",
            "tourism": "tourism_hospitality",
            "pariwisata": "tourism_hospitality",
            "environment": "environment_agriculture",
            "lingkungan": "environment_agriculture",
            "fieldwork": "environment_agriculture",
            "lapangan": "environment_agriculture",
            "agriculture": "environment_agriculture",
            "pertanian": "environment_agriculture",
        }
        active_interest_keys = {mapped for label, mapped in interest_aliases.items() if label in interest_values}
        interest_weights = profile.get("interest_weights", {})
        interest = 45 + int(sum(float(weight) * 22 for key, weight in interest_weights.items() if key in active_interest_keys))
        interest = max(0, min(100, interest))
        model_score = max(model_score, 45 + int(sum(float(weight) * 18 for key, weight in interest_weights.items() if key in active_interest_keys)))

        preference_values = " ".join([*(str(item) for value in {**req.preferences, **req.career_direction, **req.constraints}.values() for item in (value if isinstance(value, list) else [value])), req.free_text_goal or "", req.expected_prodi or ""]).lower()
        preference = 60 + sum(8 for key in profile.get("preference_weights", {}) if key.replace("_", " ") in preference_values or key in preference_values)
        preference = max(0, min(100, preference))

        career = 60 + sum(6 for key in profile.get("career_weights", {}) if key.replace("_", " ") in preference_values or key in preference_values)
        career = max(0, min(100, career))
        optional = int(self._optional_subject_features(req.scores)["optional_subject_boost"])
        breakdown = {
            "model_score": model_score,
            "model_group_score": model_score,
            "academic_fit_score": academic,
            "threshold_fit_score": max(0, 100 - eligibility_penalty * 5),
            "trend_fit_score": trend,
            "gpa_fit_score": gpa,
            "interest_fit_score": interest,
            "interest_depth_fit_score": interest,
            "preference_fit_score": preference,
            "career_fit_score": career,
            "optional_subject_boost": optional,
        }
        expected_bonus = 3 if req.expected_prodi and req.expected_prodi.lower() in profile["nama_prodi"].lower() else 0
        religion_bonus = 18 if self._religion_preference(req) == "Islamic studies / education" and profile["nama_prodi"] in {"Pendidikan Agama Islam", "Hukum Islam", "Ekonomi Syariah"} else 0
        suitability = max(0, min(100, int(round(model_score * 0.15 + academic * 0.35 + trend * 0.10 + interest * 0.25 + career * 0.15 + preference * 0.10 + gpa * 0.05 + optional * 0.03 + expected_bonus + religion_bonus - eligibility_penalty))))
        alternatives = prodi_profile_service.alternatives(profile["prodi_id"])
        why_specific = [
            f"{profile['nama_prodi']} berada dalam kelompok {profile['kelompok_prodi']} dengan mapel pendukung yang cocok untuk dibandingkan.",
            f"Kecocokan akademik dihitung dari {len(academic_requirements.get('primary', {}))} mapel primer dan {len(academic_requirements.get('supporting', {}))} mapel pendukung.",
        ]
        if unmet_primary:
            why_specific.append(f"Perlu penguatan pada mapel primer: {', '.join(unmet_primary[:3])}.")
        legacy_major = "Islamic Education" if profile["nama_prodi"] == "Pendidikan Agama Islam" else profile["nama_prodi"]
        if legacy_major == "Islamic Education":
            why_specific.append("This appears because you stated preference for Islamic studies / education; Apti does not infer personal beliefs.")
        return RecommendationItem(
            rank=0,
            major=legacy_major,
            cluster=profile["rumpun_ilmu"],
            suitability_score=suitability,
            match_level=self._match_level(suitability),
            score_breakdown=breakdown,
            confidence_label=self._confidence_label(suitability),
            explanation=why_specific,
            fit_summary=[profile["kelompok_prodi"], profile["rumpun_ilmu"]],
            strength_signals=list(academic_weights)[:4],
            tradeoffs=profile.get("challenge_areas", []),
            career_paths=profile.get("career_paths", []),
            alternative_majors=[item["nama_prodi"] for item in alternatives],
            caution="Recommendation supports exploration and counseling, not final decision.",
            shap_values={},
            major_requirements=prodi_profile_service.radar_benchmark(profile["prodi_id"]),
            user_scores={key: float(value) for key, value in req.scores.items() if value is not None},
            prodi_id=profile["prodi_id"],
            nama_prodi=profile["nama_prodi"],
            alias=profile.get("alias", []),
            kelompok_prodi=profile["kelompok_prodi"],
            rumpun_ilmu=profile["rumpun_ilmu"],
            supporting_subjects={**profile.get("supporting_subjects", {}), "threshold_gaps": score_gaps, "tier": tier},
            why_specific=why_specific,
            skill_gaps=profile.get("skill_gaps", []),
            llm_review=None,
        )

    def _prodi_recommendations(self, req: PredictRequest, group_scores: dict[str, int] | None = None) -> list[RecommendationItem]:
        avoid_ids = {prodi["prodi_id"] for value in req.prodi_to_avoid if (prodi := prodi_catalog_service.resolve_alias(value))}
        expected = prodi_catalog_service.resolve_alias(req.expected_prodi or "") if req.expected_prodi else None
        candidates = prodi_catalog_service.safe_prodi()
        if self._religion_preference(req) == "Islamic studies / education":
            preferred = [prodi_catalog_service.resolve_alias(name) for name in ["Pendidikan Agama Islam", "Hukum Islam", "Ekonomi Syariah"]]
            candidates = [item for item in preferred if item] + candidates
        deduped_candidates: list[dict[str, Any]] = []
        seen_candidate_ids: set[str] = set()
        for item in candidates:
            if item["prodi_id"] in seen_candidate_ids:
                continue
            seen_candidate_ids.add(item["prodi_id"])
            deduped_candidates.append(item)
        candidates = deduped_candidates
        if expected:
            candidates = [expected, *[item for item in candidates if item["prodi_id"] != expected["prodi_id"]]]
        recommendations = [
            self._score_prodi_profile(req, profile, (group_scores or {}).get(profile["kelompok_prodi"], 55))
            for item in candidates
            if item["prodi_id"] not in avoid_ids
            if (profile := prodi_profile_service.get_profile(item["prodi_id"]))
        ]
        ranked = self._spread_scores(sorted(recommendations, key=lambda item: item.suitability_score, reverse=True))
        return [item.model_copy(update={"rank": rank}) for rank, item in enumerate(ranked, start=1)]

    def predict(self, req: PredictRequest) -> PredictionOutput:
        features = self._to_v2_feature_row(req)
        profile_summary = self._build_profile_summary(req)
        notes = ["Optional missing subjects were treated neutrally, not as low scores."]
        fallback_used = False
        group_scores: dict[str, int] = {}

        if self.loaded:
            try:
                probabilities = self.model.predict_proba(features)[0]
                class_labels = self.label_encoder.classes_
                group_scores = {str(class_labels[index]): int(round(float(probabilities[index]) * 100)) for index in range(len(class_labels))}
            except Exception:
                fallback_used = True
                notes.insert(0, "Apti used temporary fallback recommendations because the predictive model could not finish this request.")
        else:
            fallback_used = True
            notes.insert(0, "Apti used temporary fallback recommendations because the predictive model is not ready.")

        recommendations = self._prodi_recommendations(req, group_scores if group_scores else None)[: req.top_n]

        return PredictionOutput(
            recommendations=recommendations,
            profile_summary=profile_summary,
            notes=notes,
            fallback_used=fallback_used,
            disclaimer=DISCLAIMER_TEXT,
            features=features.iloc[0].to_dict(),
        )


ml_service = MLService()
