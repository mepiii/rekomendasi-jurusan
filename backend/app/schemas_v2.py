# Purpose: Define Apti V2 option-only request/response schemas for phased recommendation rollout.
# Callers: Future V2 API routes, scoring services, schema tests.
# Deps: pydantic v2, subject normalization.
# API: AptiV2PredictRequest, AptiV2ScoreBreakdown, AptiV2RecommendationItem, AptiV2PredictResponse.
# Side effects: Validates V2 payloads at runtime.

from __future__ import annotations

from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from app.subject_normalization import normalize_score_map, normalize_subject_key

TrackKey = Literal["IPA", "IPS", "Bahasa", "Merdeka"]

FREE_TEXT_KEYS = {"free_text", "free_text_goal", "notes", "custom", "textarea"}
MERDEKA_ELECTIVE_POOL = {
    "biology",
    "chemistry",
    "physics",
    "math_advanced",
    "informatics",
    "sociology",
    "economics",
    "geography",
    "anthropology",
    "foreign_language",
    "entrepreneurship",
}


class AptiV2ScoreBreakdown(BaseModel):
    academic_fit: float = Field(..., ge=0, le=1)
    interest_fit: float = Field(..., ge=0, le=1)
    career_fit: float = Field(..., ge=0, le=1)
    learning_style_fit: float = Field(..., ge=0, le=1)
    goal_fit: float = Field(..., ge=0, le=1)
    constraint_fit: float = Field(..., ge=0, le=1)
    target_alignment: float = Field(..., ge=0, le=1)
    avoid_penalty: float = Field(default=0, ge=0, le=1)
    final_score: float = Field(..., ge=0, le=1)


class AptiV2PredictRequest(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    sma_track: TrackKey
    scores: dict[str, float | None] = Field(default_factory=dict)
    selected_electives: list[str] = Field(default_factory=list)
    survey_options: dict[str, list[str]] = Field(default_factory=dict)
    target_majors: list[str] = Field(default_factory=list)
    avoided_majors: list[str] = Field(default_factory=list)
    top_n: int = Field(default=5, ge=3, le=5)
    language: Literal["en", "id"] = "en"

    @field_validator("scores")
    @classmethod
    def validate_scores(cls, values: dict[str, float | None]) -> dict[str, float | None]:
        normalized = normalize_score_map(values)
        for subject, score in normalized.items():
            if score is None:
                continue
            if score < 0 or score > 100:
                raise ValueError(f"{subject} must be between 0 and 100")
        return normalized

    @field_validator("selected_electives")
    @classmethod
    def normalize_electives(cls, values: list[str]) -> list[str]:
        return [normalize_subject_key(value) for value in values]

    @field_validator("survey_options")
    @classmethod
    def validate_option_only_survey(cls, values: dict[str, list[str]]) -> dict[str, list[str]]:
        blocked = FREE_TEXT_KEYS & set(values)
        if blocked:
            raise ValueError(f"free-text survey keys are not allowed: {sorted(blocked)}")
        cleaned: dict[str, list[str]] = {}
        for page, selections in values.items():
            if not isinstance(selections, list):
                raise ValueError(f"{page} must be an option list")
            cleaned[page] = [selection.strip() for selection in selections if selection and selection.strip()]
        return cleaned

    @model_validator(mode="after")
    def validate_track_rules(self) -> "AptiV2PredictRequest":
        if self.sma_track == "Merdeka":
            if not 2 <= len(self.selected_electives) <= 8:
                raise ValueError("selected_electives must contain between 2 and 8 items")
            if not set(self.selected_electives).issubset(MERDEKA_ELECTIVE_POOL):
                raise ValueError("selected_electives contain unsupported values")
        elif self.selected_electives:
            raise ValueError("selected_electives are only supported for Merdeka track")
        return self


class AptiV2RecommendationItem(BaseModel):
    rank: int = Field(..., ge=1)
    prodi_id: str
    major: str
    label: dict[Literal["en", "id"], str]
    score_breakdown: AptiV2ScoreBreakdown
    target_analysis: dict[str, object] = Field(default_factory=dict)
    avoided_major_analysis: dict[str, object] = Field(default_factory=dict)
    skill_gaps: list[str] = Field(default_factory=list)
    chart_data: dict[str, object] = Field(default_factory=dict)


class AptiV2PredictResponse(BaseModel):
    app: str = "apti"
    schema_version: str = "v2"
    session_id: UUID | None = None
    recommendations: list[AptiV2RecommendationItem]
    profile_summary: dict[str, object]
    confidence: dict[str, object]
    notes: list[str] = Field(default_factory=list)
