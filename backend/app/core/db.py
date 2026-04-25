# Purpose: Supabase access helpers for master data, telemetry, explanations, and feedback.
# Callers: FastAPI routes, retrain service, background tasks.
# Deps: supabase-py client and app config.
# API: fetch_majors, fetch_interests, log_prediction, log_prediction_metrics, feedback/explanation helpers.
# Side effects: Inserts rows into prediction_log, prediction_metrics, prediction_explanations, and user_feedback tables.

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

if TYPE_CHECKING:
    from supabase import Client
else:
    Client = Any

try:
    from supabase import create_client
except ImportError:
    create_client = None

from app.config import settings
from app.recommendation_config import DATASET_VERSION, FEATURE_VERSION
from app.schemas import FeedbackRequest, PredictRequest, RecommendationItem

_supabase: Client | None = None


def get_supabase() -> Client | None:
    global _supabase
    if _supabase is not None:
        return _supabase

    if create_client is None or not settings.supabase_url or not settings.supabase_service_key:
        return None

    _supabase = create_client(settings.supabase_url, settings.supabase_service_key)
    return _supabase


def fetch_majors() -> list[dict[str, Any]]:
    client = get_supabase()
    if client is None:
        return []

    try:
        response = (
            client.table("majors")
            .select("id,name,cluster")
            .eq("is_active", True)
            .order("name")
            .execute()
        )
        return response.data or []
    except Exception:
        return []


def fetch_interests() -> list[dict[str, Any]]:
    client = get_supabase()
    if client is None:
        return []

    try:
        response = (
            client.table("interests")
            .select("id,name")
            .eq("is_active", True)
            .order("id")
            .execute()
        )
        return response.data or []
    except Exception:
        return []


def fetch_feedback_for_retrain(limit: int = 5000) -> list[dict[str, Any]]:
    client = get_supabase()
    if client is None:
        return []

    try:
        response = (
            client.table("user_feedback")
            .select("session_id,selected_major,selected_prodi_id,selected_kelompok_prodi,recommendation_snapshot,aligns_with_goals,rating,notes,created_at")
            .gte("rating", 4)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception:
        return []


def count_feedback_rows() -> int:
    client = get_supabase()
    if client is None:
        return 0

    try:
        response = client.table("user_feedback").select("id", count="exact").execute()
        return int(response.count or 0)
    except Exception:
        return 0


def _first_present(score_map: dict[str, Any], *keys: str) -> Any:
    return next((score_map[key] for key in keys if score_map.get(key) is not None), None)


def log_prediction(
    req: PredictRequest,
    recs: list[RecommendationItem],
    source: str = "web",
    latency_ms: float | None = None,
    fallback_used: bool | None = None,
) -> None:
    client = get_supabase()
    if client is None:
        return

    try:
        score_map = req.scores
        payload = {
            "session_id": str(req.session_id),
            "sma_track": req.sma_track,
            "curriculum_type": req.curriculum_type,
            "dataset_version": DATASET_VERSION,
            "feature_version": FEATURE_VERSION,
            "math_score": _first_present(score_map, "mathematics", "math", "general_math", "basic_math"),
            "physics_score": score_map.get("physics"),
            "chemistry_score": score_map.get("chemistry"),
            "biology_score": score_map.get("biology"),
            "economics_score": score_map.get("economics"),
            "indonesian_score": _first_present(score_map, "bahasa_indonesia", "indonesian", "indonesian_literature"),
            "english_score": _first_present(score_map, "english", "english_literature"),
            "interests": req.interests,
            "academic_context": req.academic_context,
            "subject_preferences": req.subject_preferences,
            "interest_deep_dive": req.interest_deep_dive,
            "career_direction": req.career_direction,
            "constraints": req.constraints,
            "expected_prodi": req.expected_prodi,
            "prodi_to_avoid": req.prodi_to_avoid,
            "free_text_goal": req.free_text_goal,
            "language": req.language,
            "top_1_major": recs[0].major if len(recs) > 0 else None,
            "top_1_score": (recs[0].suitability_score / 100) if len(recs) > 0 else None,
            "top_1_prodi_id": recs[0].prodi_id if len(recs) > 0 else None,
            "top_1_kelompok_prodi": recs[0].kelompok_prodi if len(recs) > 0 else None,
            "top_1_rumpun_ilmu": recs[0].rumpun_ilmu if len(recs) > 0 else None,
            "top_2_major": recs[1].major if len(recs) > 1 else None,
            "top_2_score": (recs[1].suitability_score / 100) if len(recs) > 1 else None,
            "top_2_prodi_id": recs[1].prodi_id if len(recs) > 1 else None,
            "top_2_kelompok_prodi": recs[1].kelompok_prodi if len(recs) > 1 else None,
            "top_2_rumpun_ilmu": recs[1].rumpun_ilmu if len(recs) > 1 else None,
            "top_3_major": recs[2].major if len(recs) > 2 else None,
            "top_3_score": (recs[2].suitability_score / 100) if len(recs) > 2 else None,
            "top_3_prodi_id": recs[2].prodi_id if len(recs) > 2 else None,
            "top_3_kelompok_prodi": recs[2].kelompok_prodi if len(recs) > 2 else None,
            "top_3_rumpun_ilmu": recs[2].rumpun_ilmu if len(recs) > 2 else None,
            "model_version": settings.model_version,
            "source": source,
        }
        if latency_ms is not None:
            payload["latency_ms"] = round(float(latency_ms), 2)
        if fallback_used is not None:
            payload["fallback_used"] = bool(fallback_used)
        client.table("prediction_log").insert(payload).execute()
    except Exception:
        try:
            legacy_payload = {key: payload[key] for key in ["session_id", "sma_track", "math_score", "physics_score", "chemistry_score", "biology_score", "economics_score", "indonesian_score", "english_score", "interests", "top_1_major", "top_1_score", "top_2_major", "top_2_score", "top_3_major", "top_3_score", "model_version", "source"]}
            if latency_ms is not None:
                legacy_payload["latency_ms"] = round(float(latency_ms), 2)
            if fallback_used is not None:
                legacy_payload["fallback_used"] = bool(fallback_used)
            client.table("prediction_log").insert(legacy_payload).execute()
        except Exception:
            return


def log_prediction_metrics(
    session_id: UUID,
    model_version: str,
    latency_ms: float,
    sma_track: str,
    features: dict[str, Any],
    top_major: str | None,
    bias_score: float,
) -> None:
    client = get_supabase()
    if client is None:
        return

    try:
        payload = {
            "session_id": str(session_id),
            "model_version": model_version,
            "latency_ms": round(float(latency_ms), 2),
            "sma_track": sma_track,
            "features": features,
            "top_major": top_major,
            "bias_score": round(float(bias_score), 4),
        }
        client.table("prediction_metrics").insert(payload).execute()
    except Exception:
        return


def log_feedback(payload: FeedbackRequest) -> None:
    client = get_supabase()
    if client is None:
        return

    try:
        row = {
            "session_id": str(payload.session_id),
            "selected_major": payload.selected_major,
            "selected_prodi_id": payload.selected_prodi_id,
            "selected_kelompok_prodi": payload.selected_kelompok_prodi,
            "recommendation_snapshot": payload.recommendation_snapshot,
            "aligns_with_goals": payload.aligns_with_goals,
            "rating": payload.rating,
            "notes": payload.notes,
        }
        client.table("user_feedback").insert(row).execute()
    except Exception:
        try:
            client.table("user_feedback").insert({"session_id": row["session_id"], "selected_major": row["selected_major"], "aligns_with_goals": row["aligns_with_goals"], "rating": row["rating"], "notes": row["notes"]}).execute()
        except Exception:
            return


def save_explanations(session_id: UUID, model_version: str, explanations: list[dict[str, Any]]) -> None:
    client = get_supabase()
    if client is None:
        return

    try:
        rows = [
            {
                "session_id": str(session_id),
                "model_version": model_version,
                "major": item.get("major"),
                "shap_values": item.get("shap_values", {}),
            }
            for item in explanations
        ]
        if rows:
            client.table("prediction_explanations").insert(rows).execute()
    except Exception:
        return


def fetch_explanations(session_id: UUID) -> list[dict[str, Any]]:
    client = get_supabase()
    if client is None:
        return []

    try:
        response = (
            client.table("prediction_explanations")
            .select("major,shap_values")
            .eq("session_id", str(session_id))
            .order("created_at", desc=False)
            .execute()
        )
        return response.data or []
    except Exception:
        return []


def clear_explanations(session_id: UUID) -> None:
    client = get_supabase()
    if client is None:
        return

    try:
        client.table("prediction_explanations").delete().eq("session_id", str(session_id)).execute()
    except Exception:
        return


def fetch_metrics_snapshot() -> dict[str, float | int]:
    client = get_supabase()
    if client is None:
        return {
            "total_predictions": 0,
            "avg_latency_ms": 0.0,
            "bias_score": 0.0,
            "accuracy": 0.0,
        }

    try:
        total = client.table("prediction_metrics").select("id", count="exact").execute()
        metric_rows = (
            client.table("prediction_metrics")
            .select("latency_ms,bias_score")
            .order("created_at", desc=True)
            .limit(1000)
            .execute()
        )
        feedback_rows = (
            client.table("user_feedback")
            .select("aligns_with_goals")
            .order("created_at", desc=True)
            .limit(1000)
            .execute()
        )

        metrics = metric_rows.data or []
        feedback = feedback_rows.data or []

        avg_latency = 0.0
        avg_bias = 0.0
        if metrics:
            avg_latency = sum(float(item.get("latency_ms", 0.0)) for item in metrics) / len(metrics)
            avg_bias = sum(float(item.get("bias_score", 0.0)) for item in metrics) / len(metrics)

        accuracy = 0.0
        if feedback:
            hits = sum(1 for item in feedback if item.get("aligns_with_goals") is True)
            accuracy = (hits / len(feedback)) * 100

        return {
            "total_predictions": int(total.count or 0),
            "avg_latency_ms": round(avg_latency, 2),
            "bias_score": round(avg_bias, 4),
            "accuracy": round(accuracy, 2),
        }
    except Exception:
        return {
            "total_predictions": 0,
            "avg_latency_ms": 0.0,
            "bias_score": 0.0,
            "accuracy": 0.0,
        }
