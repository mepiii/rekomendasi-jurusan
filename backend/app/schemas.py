# Purpose: Define validated request/response models for recommendation API.
# Callers: FastAPI endpoint handlers and ML service layer.
# Deps: pydantic v2.
# API: PredictRequest, PredictResponse, retrain and feedback schemas.
# Side effects: Enforces API input constraints at runtime.

from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

VALID_SMA_TRACKS = {"Science", "Social Studies", "Language"}
VALID_INTERESTS = {
    "Technology",
    "Data & AI",
    "Engineering",
    "Social Sciences & Humanities",
    "Communication",
    "Law & Politics",
    "Science & Health",
    "Business & Management",
    "Arts & Creativity",
    "Education & Languages",
}


class ScoreInput(BaseModel):
    math: float = Field(..., ge=0, le=100)
    physics: float = Field(..., ge=0, le=100)
    chemistry: float = Field(..., ge=0, le=100)
    biology: float = Field(..., ge=0, le=100)
    economics: float = Field(..., ge=0, le=100)
    indonesian: float = Field(..., ge=0, le=100)
    english: float = Field(..., ge=0, le=100)


class PredictRequest(BaseModel):
    session_id: Optional[UUID] = Field(default_factory=uuid4)
    sma_track: str = Field(..., description="Science, Social Studies, or Language")
    scores: ScoreInput
    interests: list[str] = Field(..., min_length=1, max_length=5)
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


class RecommendationItem(BaseModel):
    rank: int
    major: str
    cluster: str
    suitability_score: int
    explanation: str
    shap_values: dict[str, float] = Field(default_factory=dict)
    major_requirements: dict[str, float] = Field(default_factory=dict)


class ProfileSummary(BaseModel):
    strongest_subject: str
    strongest_group: str
    avg_score: float


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
