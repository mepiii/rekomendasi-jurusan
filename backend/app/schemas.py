# Purpose: Define validated request/response models for recommendation API.
# Callers: FastAPI endpoint handlers and ML service layer.
# Deps: pydantic v2, recommendation config.
# API: PredictRequest, PredictResponse, retrain and feedback schemas.
# Side effects: Enforces API input constraints at runtime.

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from app.recommendation_config import TRACK_SUBJECT_RULES, VALID_INTERESTS, VALID_PREFERENCE_VALUES, VALID_SMA_TRACKS


class PredictRequest(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    sma_track: str = Field(..., description="IPA, IPS, Bahasa, or Merdeka")
    curriculum_type: str = Field(..., min_length=2)
    scores: dict[str, float] = Field(..., min_length=6)
    selected_electives: list[str] = Field(default_factory=list, max_length=5)
    interests: list[str] = Field(..., min_length=3, max_length=6)
    preferences: dict[str, str] = Field(..., min_length=3, max_length=3)
    top_n: int = Field(default=3, ge=3, le=5)

    @field_validator("sma_track")
    @classmethod
    def validate_sma_track(cls, value: str) -> str:
        if value not in VALID_SMA_TRACKS:
            raise ValueError(f"sma_track must be one of: {sorted(VALID_SMA_TRACKS)}")
        return value

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, values: list[str]) -> list[str]:
        seen = set()
        cleaned: list[str] = []
        for interest in values:
            if interest not in VALID_INTERESTS:
                raise ValueError(f"Interest '{interest}' is not recognized.")
            if interest not in seen:
                seen.add(interest)
                cleaned.append(interest)
        return cleaned

    @field_validator("preferences")
    @classmethod
    def validate_preferences(cls, values: dict[str, str]) -> dict[str, str]:
        required = {"orientation", "approach", "style"}
        if set(values) != required:
            raise ValueError("preferences must contain orientation, approach, and style")
        for value in values.values():
            if value not in VALID_PREFERENCE_VALUES:
                raise ValueError(f"Preference value '{value}' is not recognized.")
        return values

    @field_validator("scores")
    @classmethod
    def validate_scores(cls, values: dict[str, float]) -> dict[str, float]:
        for key, value in values.items():
            if value < 0 or value > 100:
                raise ValueError(f"Score for '{key}' must be between 0 and 100.")
        return values

    @model_validator(mode="after")
    def validate_track_subject_rules(self) -> "PredictRequest":
        rules = TRACK_SUBJECT_RULES[self.sma_track]
        score_keys = set(self.scores)
        missing_required = sorted(rules["required"] - score_keys)
        if missing_required:
            raise ValueError(f"Missing required subjects: {missing_required}")

        optional = rules.get("optional", set())
        elective_pool = rules.get("electives", set())
        allowed_keys = rules["required"] | optional | elective_pool
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
    cluster: str
    suitability_score: int
    confidence_label: str
    explanation: str
    fit_summary: list[str] = Field(default_factory=list)
    strength_signals: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)
    career_paths: list[str] = Field(default_factory=list)
    alternative_majors: list[str] = Field(default_factory=list)
    shap_values: dict[str, float] = Field(default_factory=dict)
    major_requirements: dict[str, float] = Field(default_factory=dict)


class ProfileSummary(BaseModel):
    strongest_subject: str
    strongest_group: str
    avg_score: float
    confidence_label: str


class PredictResponse(BaseModel):
    session_id: UUID
    recommendations: list[RecommendationItem]
    profile_summary: ProfileSummary
    model_version: str
    disclaimer: str
    latency_ms: float | None = None


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
