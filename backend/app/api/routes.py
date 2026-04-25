# Purpose: Define API routes for health, metadata, prediction, feedback, retraining, metrics, and explainability retrieval.
# Callers: app.main includes this router.
# Deps: FastAPI, app.schemas, app.core.db, app.services modules.
# API: Router exposing /health, /majors, /interests, /predict, /feedback, /api/retrain, /metrics, /explanations/{session_id}.
# Side effects: Schedules background tasks for logging, explanations, and retraining.

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse

from app.config import settings
from app.recommendation_config import APP_IDENTIFIER, DATASET_VERSION, FEATURE_VERSION
from app.core.db import (
    clear_explanations,
    fetch_explanations,
    fetch_interests,
    fetch_majors,
    log_feedback,
    log_prediction,
    log_prediction_metrics,
    save_explanations,
)
from app.schemas import (
    ExplanationItem,
    ExplanationResponse,
    FeedbackRequest,
    FeedbackResponse,
    MetricsResponse,
    PredictRequest,
    PredictResponse,
    RetrainTriggerRequest,
    RetrainTriggerResponse,
)
from app.services.llm_review_service import llm_review_service
from app.services.ml_service import MAJOR_CLUSTER_MAP, ml_service
from app.services.retrain_service import retrain_service
from app.services.telemetry_service import compute_bias_score, compute_drift_score, snapshot_metrics

router = APIRouter()

DEFAULT_MAJORS = [
    {"id": 1, "name": "Computer Science", "cluster": "STEM"},
    {"id": 2, "name": "Information Systems", "cluster": "STEM"},
    {"id": 3, "name": "Civil Engineering", "cluster": "STEM"},
    {"id": 4, "name": "Electrical Engineering", "cluster": "STEM"},
    {"id": 5, "name": "Medicine", "cluster": "Health"},
    {"id": 6, "name": "Pharmacy", "cluster": "Health"},
    {"id": 7, "name": "Biology", "cluster": "Health"},
    {"id": 8, "name": "Mathematics", "cluster": "STEM"},
    {"id": 9, "name": "Psychology", "cluster": "Social"},
    {"id": 10, "name": "Communication Studies", "cluster": "Social"},
    {"id": 11, "name": "Law", "cluster": "Social"},
    {"id": 12, "name": "English Education", "cluster": "Social"},
    {"id": 13, "name": "Management", "cluster": "Business"},
    {"id": 14, "name": "Accounting", "cluster": "Business"},
    {"id": 15, "name": "Visual Communication Design", "cluster": "Arts"},
]

DEFAULT_INTERESTS = [
    {"id": 1, "name": "Technology"},
    {"id": 2, "name": "Engineering"},
    {"id": 3, "name": "Health"},
    {"id": 4, "name": "Business"},
    {"id": 5, "name": "Social"},
    {"id": 6, "name": "Law"},
    {"id": 7, "name": "Education"},
    {"id": 8, "name": "Psychology"},
    {"id": 9, "name": "Media"},
    {"id": 10, "name": "Design"},
    {"id": 11, "name": "Language"},
    {"id": 12, "name": "Environment"},
    {"id": 13, "name": "Data / AI"},
]


@router.get("/")
def root() -> dict[str, str]:
    return {
        "status": "ok" if ml_service.loaded else "degraded",
        "model_version": settings.model_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "app": APP_IDENTIFIER,
        "status": "ok" if ml_service.loaded else "degraded",
        "model_loaded": ml_service.loaded,
        "model_load_error": ml_service.load_error,
        "model_version": settings.model_version,
        "feature_version": FEATURE_VERSION,
        "supabase_configured": bool(settings.supabase_url and settings.supabase_service_key),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/majors")
def get_majors() -> dict[str, list[dict[str, str]]]:
    rows = fetch_majors()
    return {"data": rows if rows else DEFAULT_MAJORS}


@router.get("/interests")
def get_interests() -> dict[str, list[dict[str, str]]]:
    rows = fetch_interests()
    return {"data": rows if rows else DEFAULT_INTERESTS}


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest, background_tasks: BackgroundTasks) -> PredictResponse | JSONResponse:
    started = perf_counter()

    def _safe_task(func, *args, **kwargs) -> None:
        try:
            func(*args, **kwargs)
        except Exception:
            return

    try:
        prediction = ml_service.predict(req)
        elapsed_ms = (perf_counter() - started) * 1000

        top_major = prediction.recommendations[0].major if prediction.recommendations else None
        top_cluster = MAJOR_CLUSTER_MAP.get(top_major or "", "Other")
        bias_score = compute_bias_score(req.sma_track, top_cluster)
        drift = compute_drift_score(prediction.features)
        llm_review = llm_review_service.review(req, prediction.recommendations)
        recommendations = llm_review_service.apply(prediction.recommendations, llm_review)
        majors = [item.major for item in recommendations]

        def _build_and_save_explanations() -> None:
            rows = ml_service.build_explanations(req, majors)
            if rows:
                save_explanations(req.session_id, settings.model_version, rows)

        background_tasks.add_task(
            _safe_task,
            log_prediction,
            req,
            recommendations,
            latency_ms=elapsed_ms,
            fallback_used=prediction.fallback_used,
        )
        background_tasks.add_task(
            _safe_task,
            log_prediction_metrics,
            req.session_id,
            settings.model_version,
            elapsed_ms,
            req.sma_track,
            prediction.features,
            top_major,
            bias_score,
        )
        background_tasks.add_task(_safe_task, clear_explanations, req.session_id)
        background_tasks.add_task(_safe_task, _build_and_save_explanations)

        notes = list(prediction.notes)
        if drift.alerted:
            notes.append("Apti used extra caution because this profile differs from recent training examples.")

        return PredictResponse(
            app=APP_IDENTIFIER,
            model_version=settings.model_version,
            dataset_version=DATASET_VERSION,
            feature_version=FEATURE_VERSION,
            llm_provider=llm_review.provider,
            llm_review_used=llm_review.used,
            session_id=req.session_id,
            recommendations=recommendations,
            profile_summary=prediction.profile_summary,
            notes=notes,
            fallback_used=prediction.fallback_used,
            disclaimer=prediction.disclaimer,
            latency_ms=round(elapsed_ms),
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "error": "model_error",
                "message": "A system error occurred. Please try again shortly.",
            },
        )


@router.get("/explanations/{session_id}", response_model=ExplanationResponse)
def get_explanations(session_id: UUID) -> ExplanationResponse:
    rows = fetch_explanations(session_id)
    return ExplanationResponse(
        session_id=session_id,
        explanations=[ExplanationItem(major=item.get("major", "-"), shap_values=item.get("shap_values", {})) for item in rows],
        ready=len(rows) > 0,
        model_version=settings.model_version,
    )


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackRequest, background_tasks: BackgroundTasks) -> FeedbackResponse:
    background_tasks.add_task(log_feedback, payload)
    return FeedbackResponse(accepted=True, message="Feedback saved")


@router.get("/metrics", response_model=MetricsResponse)
def metrics() -> MetricsResponse:
    snap = snapshot_metrics(settings.model_version)
    return MetricsResponse(
        model_version=str(snap["model_version"]),
        total_predictions=int(snap["total_predictions"]),
        avg_latency_ms=float(snap["avg_latency_ms"]),
        bias_score=float(snap["bias_score"]),
        accuracy=float(snap["accuracy"]),
    )


@router.post("/api/retrain", response_model=RetrainTriggerResponse)
def retrain(payload: RetrainTriggerRequest, background_tasks: BackgroundTasks) -> RetrainTriggerResponse:
    def _run() -> None:
        retrain_service.run_retrain(min_feedback_rows=payload.min_feedback_rows)

    background_tasks.add_task(_run)
    return RetrainTriggerResponse(started=True, message="retraining started in background")
