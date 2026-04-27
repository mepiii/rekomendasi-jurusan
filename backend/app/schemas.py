# Purpose: Define validated request/response models for recommendation API.
# Callers: FastAPI endpoint handlers and ML service layer.
# Deps: pydantic v2, recommendation config.
# API: PredictRequest, PredictResponse, retrain and feedback schemas.
# Side effects: Enforces API input constraints at runtime.

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from app.recommendation_config import TRACK_SUBJECT_RULES, VALID_SMA_TRACKS

LEGACY_SUBJECT_ALIASES = {
    "mathematics": "general_math",
    "bahasa_indonesia": "indonesian",
    "arts_culture": "arts",
    "religion_ethics": "religion",
}
LEGACY_OPTIONAL_SUBJECTS = {"history", "regional_language", "pkwu", "prakarya", "pe"}


class SemesterScore(BaseModel):
    semester: int = Field(..., ge=1, le=6)
    subject: str = Field(..., min_length=1)
    score: float | None = Field(default=None, ge=0, le=100)

    @field_validator("subject")
    @classmethod
    def normalize_subject(cls, value: str) -> str:
        return LEGACY_SUBJECT_ALIASES.get(value.strip(), value.strip())


class RaporInput(BaseModel):
    kelas_10: list[SemesterScore] = Field(default_factory=list)
    kelas_11: list[SemesterScore] = Field(default_factory=list)
    kelas_12: list[SemesterScore] = Field(default_factory=list)
    sma_track: str | None = None
    curriculum_type: str | None = None
    merdeka_electives: list[str] = Field(default_factory=list, max_length=5)

    def all_scores(self) -> list[SemesterScore]:
        return [*self.kelas_10, *self.kelas_11, *self.kelas_12]

    def average_scores(self) -> dict[str, float | None]:
        grouped: dict[str, list[float]] = {}
        for item in self.all_scores():
            if item.score is not None:
                grouped.setdefault(item.subject, []).append(float(item.score))
        return {subject: round(sum(values) / len(values), 2) for subject, values in grouped.items()}

    @model_validator(mode="after")
    def validate_semester_buckets(self) -> "RaporInput":
        expected = {"kelas_10": {1, 2}, "kelas_11": {3, 4}, "kelas_12": {5, 6}}
        for field_name, semesters in expected.items():
            invalid = [item.semester for item in getattr(self, field_name) if item.semester not in semesters]
            if invalid:
                raise ValueError(f"{field_name} only accepts semesters {sorted(semesters)}")
        return self


class DerivedAggregates(BaseModel):
    subject_avg: dict[str, float] = Field(default_factory=dict)
    subject_trend: dict[str, float] = Field(default_factory=dict)
    kelas_12_avg: float = 0.0
    overall_gpa: float = 0.0


class PredictRequest(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    sma_track: str = Field(..., description="IPA, IPS, Bahasa, or Merdeka")
    curriculum_type: str | None = None
    scores: dict[str, float | None] = Field(default_factory=dict)
    rapor: RaporInput | None = None
    selected_electives: list[str] = Field(default_factory=list, max_length=5)
    interests: list[str] = Field(default_factory=list)
    preferences: dict[str, str | list[str]] = Field(default_factory=dict)
    academic_context: dict[str, str | list[str] | int | float | bool | None] = Field(default_factory=dict)
    subject_preferences: dict[str, list[str]] = Field(default_factory=dict)
    interest_deep_dive: dict[str, list[str] | str] = Field(default_factory=dict)
    career_direction: dict[str, list[str] | str] = Field(default_factory=dict)
    constraints: dict[str, str | list[str] | int | float | bool | None] = Field(default_factory=dict)
    expected_prodi: str | None = None
    prodi_to_avoid: list[str] = Field(default_factory=list)
    free_text_goal: str | None = None
    top_n: int = Field(default=5, ge=3, le=5)
    language: str = "en"

    @field_validator("top_n", mode="before")
    @classmethod
    def clamp_top_n(cls, value: int | None) -> int:
        if value is None:
            return 5
        return min(5, max(3, int(value)))

    @field_validator("sma_track")
    @classmethod
    def validate_sma_track(cls, value: str) -> str:
        if value not in VALID_SMA_TRACKS:
            raise ValueError(f"sma_track must be one of: {sorted(VALID_SMA_TRACKS)}")
        return value

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, values: list[str]) -> list[str]:
        return [value.strip() for value in values if value and value.strip()]

    @field_validator("preferences")
    @classmethod
    def validate_preferences(cls, values: dict[str, str | list[str]]) -> dict[str, str | list[str]]:
        cleaned: dict[str, str | list[str]] = {}
        for key, value in values.items():
            if isinstance(value, list):
                cleaned[key] = [item.strip() for item in value if item and item.strip()]
            elif isinstance(value, str):
                cleaned[key] = value.strip()
        return cleaned

    @field_validator("scores")
    @classmethod
    def validate_scores(cls, values: dict[str, float | None]) -> dict[str, float | None]:
        for subject, score in values.items():
            if score is None:
                continue
            if score < 0 or score > 100:
                raise ValueError(f"{subject} must be between 0 and 100")
        return values

    @model_validator(mode="after")
    def validate_track_subject_rules(self) -> "PredictRequest":
        rules = TRACK_SUBJECT_RULES[self.sma_track]
        if self.rapor and not self.scores:
            self.scores = self.rapor.average_scores()
        score_keys = set(self.scores)

        optional = rules.get("optional", set())
        elective_pool = rules.get("electives", set())
        common_rapor_keys = TRACK_SUBJECT_RULES["Merdeka"]["required"] | {"general_math"}
        allowed_keys = rules["required"] | optional | elective_pool | common_rapor_keys | set(LEGACY_SUBJECT_ALIASES) | LEGACY_OPTIONAL_SUBJECTS
        unknown = sorted(score_keys - allowed_keys)
        if unknown:
            raise ValueError(f"Scores contain unsupported subjects for {self.sma_track}: {unknown}")

        if self.sma_track == "Merdeka":
            min_elective, max_elective = rules["elective_range"]
            if not (min_elective <= len(self.selected_electives) <= max_elective):
                raise ValueError(f"selected_electives must contain between {min_elective} and {max_elective} items")
            if not set(self.selected_electives).issubset(elective_pool):
                raise ValueError("selected_electives contain unsupported values")
            if not set(self.selected_electives).issubset(score_keys):
                raise ValueError("selected_electives must have corresponding scores")
        elif self.selected_electives:
            raise ValueError("selected_electives are only supported for Merdeka track")

        return self


class RecommendationItem(BaseModel):
    rank: int
    major: str
    cluster: str = "General"
    suitability_score: int
    match_level: str = "Match"
    score_breakdown: dict[str, int] = Field(default_factory=dict)
    explanation: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)
    career_paths: list[str] = Field(default_factory=list)
    alternative_majors: list[str] = Field(default_factory=list)
    caution: str | None = None
    confidence_label: str | None = None
    fit_summary: list[str] = Field(default_factory=list)
    strength_signals: list[str] = Field(default_factory=list)
    shap_values: dict[str, float] = Field(default_factory=dict)
    major_requirements: dict[str, float] = Field(default_factory=dict)
    user_scores: dict[str, float] = Field(default_factory=dict)
    prodi_id: str | None = None
    nama_prodi: str | None = None
    alias: list[str] = Field(default_factory=list)
    kelompok_prodi: str | None = None
    rumpun_ilmu: str | None = None
    supporting_subjects: dict[str, object] = Field(default_factory=dict)
    why_specific: list[str] = Field(default_factory=list)
    skill_gaps: list[str] = Field(default_factory=list)
    llm_review: dict[str, object] | None = None

    @field_validator("explanation", mode="before")
    @classmethod
    def normalize_explanation(cls, value: str | list[str] | None) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            cleaned = value.strip()
            return [cleaned] if cleaned else []
        return value


class ProfileSummary(BaseModel):
    strongest_subject: str | None = None
    strongest_group: str | None = None
    avg_score: float | None = None
    confidence_label: str | None = None
    strongest_area: str | None = None
    academic_pattern: str | None = None
    interest_pattern: str | None = None
    preference_pattern: str | None = None
    input_completeness_score: int | None = None


class PredictResponse(BaseModel):
    app: str = "apti"
    model_version: str
    dataset_version: str | None = None
    feature_version: str
    llm_provider: str = "none"
    llm_review_used: bool = False
    session_id: UUID | None = None
    recommendations: list[RecommendationItem]
    profile_summary: ProfileSummary | dict[str, object]
    notes: list[str] = Field(default_factory=list)
    fallback_used: bool = False
    latency_ms: int
    disclaimer: str | None = None


class HealthResponse(BaseModel):
    status: str
    model_version: str
    timestamp: str


class ErrorItem(BaseModel):
    field: str
    issue: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: list[ErrorItem] | None = None


class FeedbackRequest(BaseModel):
    session_id: UUID
    selected_major: str | None = None
    selected_prodi_id: str | None = None
    selected_kelompok_prodi: str | None = None
    recommendation_snapshot: dict[str, object] = Field(default_factory=dict)
    aligns_with_goals: bool
    rating: int = Field(..., ge=1, le=5)
    notes: str | None = None


class FeedbackResponse(BaseModel):
    accepted: bool
    message: str


class MetricsResponse(BaseModel):
    model_version: str
    total_predictions: int
    avg_latency_ms: float
    bias_score: float
    accuracy: float


class ExplanationItem(BaseModel):
    major: str
    shap_values: dict[str, float]


class ExplanationResponse(BaseModel):
    session_id: UUID
    explanations: list[ExplanationItem]
    ready: bool
    model_version: str


class RetrainTriggerRequest(BaseModel):
    min_feedback_rows: int = Field(default=100, ge=10, le=10000)


class RetrainTriggerResponse(BaseModel):
    started: bool
    message: str
