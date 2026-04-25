# Purpose: Validate Apti backend prediction contract constants.
# Callers: pytest contract suite.
# Deps: app.recommendation_config.
# API: Pytest tests for version and religion preference constants.
# Side effects: None.

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.recommendation_config import (
    DATASET_VERSION,
    FEATURE_VERSION,
    MODEL_VERSION,
    RELIGION_RELATED_MAJORS,
    VALID_RELIGION_RELATED_MAJOR_PREFERENCES,
)
from app.schemas import PredictRequest, PredictResponse, RecommendationItem


def feature_row_for(req):
    from app.services.ml_service import MLService

    return MLService()._to_feature_row(req).iloc[0].to_dict()


def test_apti_versions_are_canonical():
    assert MODEL_VERSION == "apti_v2"
    assert FEATURE_VERSION == "apti_features_v2"
    assert DATASET_VERSION == "apti_dataset_v2"


def test_religion_preferences_are_not_identity_labels():
    assert "Not relevant" in VALID_RELIGION_RELATED_MAJOR_PREFERENCES
    assert "Islamic studies / education" in VALID_RELIGION_RELATED_MAJOR_PREFERENCES
    assert "What is your religion?" not in VALID_RELIGION_RELATED_MAJOR_PREFERENCES
    assert "Islamic Education" in RELIGION_RELATED_MAJORS


def route_payload():
    return {
        "sma_track": "IPA",
        "scores": {
            "mathematics": 91,
            "english": 86,
            "physics": 84,
            "chemistry": 78,
            "biology": 74,
        },
        "interests": ["Technology", "Data / AI", "Design"],
        "preferences": {"religion_related_major_preference": "Not relevant"},
        "top_n": 3,
        "language": "en",
    }


def test_health_route_returns_p0_contract(monkeypatch):
    from app.main import app
    from app.services.ml_service import ml_service

    monkeypatch.setattr(ml_service, "model", None)
    monkeypatch.setattr(ml_service, "label_encoder", None)
    response = TestClient(app).get("/health")
    data = response.json()

    assert response.status_code == 200
    assert data["app"] == "apti"
    assert data["status"] == "degraded"
    assert data["model_loaded"] is False
    assert data["model_version"] == MODEL_VERSION
    assert data["feature_version"] == FEATURE_VERSION
    assert isinstance(data["supabase_configured"], bool)
    assert "timestamp" in data
    assert "supabase_service_key" not in data


def test_predict_route_returns_p0_contract_when_model_disabled(monkeypatch):
    from app.main import app
    from app.services.ml_service import ml_service

    monkeypatch.setattr(ml_service, "model", None)
    monkeypatch.setattr(ml_service, "label_encoder", None)
    monkeypatch.setattr("app.api.routes.log_prediction", lambda *_, **__: (_ for _ in ()).throw(RuntimeError("log failed")))

    response = TestClient(app).post("/predict", json=route_payload())
    data = response.json()

    assert response.status_code == 200
    assert data["app"] == "apti"
    assert data["model_version"] == MODEL_VERSION
    assert data["feature_version"] == FEATURE_VERSION
    assert data["session_id"]
    assert data["fallback_used"] is True
    assert isinstance(data["latency_ms"], int)
    assert len(data["recommendations"]) >= 3
    assert isinstance(data["profile_summary"], dict)
    assert isinstance(data["notes"], list)


def test_predict_request_accepts_nullable_optional_scores():
    req = PredictRequest(
        sma_track="IPA",
        scores={
            "mathematics": 88,
            "bahasa_indonesia": 84,
            "english": 90,
            "history": 82,
            "civics": 80,
            "physics": 85,
            "chemistry": 78,
            "biology": 80,
            "regional_language": None,
            "arts_culture": 86,
            "religion_ethics": None,
            "informatics": 92,
        },
        interests=["Technology", "AI / Data", "Design"],
        preferences={
            "thinking_style": ["Numbers", "Systems"],
            "problem_type": ["Technical", "Creative"],
            "work_style": ["Independent"],
            "career_orientation": ["Technology oriented", "High growth"],
            "religion_related_major_preference": "Not relevant",
        },
        top_n=9,
        language="en",
    )

    assert req.scores["regional_language"] is None
    assert req.top_n == 5
    assert req.preferences["religion_related_major_preference"] == "Not relevant"


def test_optional_subjects_missing_are_neutral_feature_values():
    req = PredictRequest(
        sma_track="IPA",
        scores={
            "mathematics": 88,
            "bahasa_indonesia": 84,
            "english": 90,
            "history": 82,
            "civics": 80,
            "physics": 85,
            "chemistry": 78,
            "biology": 80,
            "regional_language": None,
            "arts_culture": None,
            "religion_ethics": None,
            "informatics": None,
        },
        interests=["Technology"],
        preferences={},
    )
    features = feature_row_for(req)

    assert features["has_regional_language"] == 0
    assert features["has_art"] == 0
    assert features["has_religion_ethics"] == 0
    assert features["has_pkwu"] == 0
    assert features["has_pe"] == 0
    assert features["has_informatics"] == 0
    assert features["optional_subject_count"] == 0
    assert features["optional_subject_boost"] == 50


def test_present_optional_subjects_add_bonus_feature_values():
    req = PredictRequest(
        sma_track="IPA",
        scores={
            "mathematics": 88,
            "bahasa_indonesia": 84,
            "english": 90,
            "history": 82,
            "civics": 80,
            "physics": 85,
            "chemistry": 78,
            "biology": 80,
            "regional_language": 86,
            "arts_culture": 90,
            "pkwu": 77,
            "prakarya": 79,
            "pe": 70,
            "religion_ethics": None,
            "informatics": 92,
        },
        interests=["Technology"],
        preferences={},
    )
    features = feature_row_for(req)

    assert features["has_regional_language"] == 1
    assert features["has_art"] == 1
    assert features["has_pkwu"] == 1
    assert features["has_pe"] == 1
    assert features["has_informatics"] == 1
    assert features["optional_subject_count"] == 6
    assert features["optional_subject_boost"] >= 50
    assert features["optional_completeness_score"] == round(6 / 7 * 100, 2)


def test_subject_group_aliases_and_defaults_are_neutral():
    req = PredictRequest(
        sma_track="IPA",
        scores={
            "mathematics": 90,
            "bahasa_indonesia": 80,
            "english": 70,
            "arts_culture": 85,
            "religion_ethics": 75,
            "regional_language": None,
        },
        interests=["Technology"],
        preferences={},
    )
    features = feature_row_for(req)

    assert features["science_score"] == 90
    assert features["technical_score"] == 90
    assert features["language_score"] == 75
    assert features["humanities_score"] == 80
    assert features["social_score"] == 50


def test_profile_summary_and_explanation_ignore_nullable_scores():
    req = PredictRequest(
        sma_track="IPA",
        scores={
            "mathematics": 88,
            "bahasa_indonesia": None,
            "english": 90,
            "regional_language": None,
        },
        interests=["Technology"],
        preferences={"approach": "Technical"},
    )
    service = __import__("app.services.ml_service", fromlist=["MLService"]).MLService()

    summary = service._build_profile_summary(req)
    explanation = service._generic_explanation("Computer Science", req)

    assert summary.avg_score == 89
    assert summary.strongest_subject == "Bahasa Inggris"
    assert "Bahasa Inggris" in explanation


def test_predict_request_rejects_out_of_range_scores():
    try:
        PredictRequest(sma_track="IPA", scores={"mathematics": 101}, interests=[], preferences={})
    except ValidationError as exc:
        assert "0 and 100" in str(exc) or "less than or equal" in str(exc)
    else:
        raise AssertionError("Expected validation error")


def test_predict_request_rejects_unknown_score_keys_even_when_partial():
    try:
        PredictRequest(sma_track="IPA", scores={"unsupported_subject": 90}, interests=[], preferences={})
    except ValidationError as exc:
        assert "unsupported subjects" in str(exc)
    else:
        raise AssertionError("Expected validation error")


def test_recommendation_item_accepts_legacy_fields_with_safe_defaults():
    item = RecommendationItem(
        rank=1,
        major="Data Science",
        cluster="STEM / Technology",
        suitability_score=87,
        explanation="Strong math and technology fit.",
    )

    assert item.match_level == "Match"
    assert item.score_breakdown == {}
    assert item.explanation == ["Strong math and technology fit."]


def test_predict_response_requires_feature_version():
    try:
        PredictResponse(
            app="apti",
            model_version="apti_rf_v1.0",
            recommendations=[],
            profile_summary={},
            latency_ms=123,
        )
    except ValidationError as exc:
        assert "feature_version" in str(exc)
    else:
        raise AssertionError("Expected validation error")


def test_predict_response_requires_latency_ms():
    try:
        PredictResponse(
            app="apti",
            model_version="apti_rf_v1.0",
            feature_version="apti_features_v1.0",
            recommendations=[],
            profile_summary={},
        )
    except ValidationError as exc:
        assert "latency_ms" in str(exc)
    else:
        raise AssertionError("Expected validation error")


def test_predict_returns_top_n_contract_when_model_unavailable():
    req = PredictRequest(
        sma_track="IPA",
        scores={
            "mathematics": 91,
            "english": 86,
            "physics": 84,
            "chemistry": 78,
            "biology": 74,
            "informatics": None,
        },
        interests=["Technology", "Data / AI", "Design"],
        preferences={
            "orientation": "Numbers",
            "approach": "Technical",
            "style": "Independent",
            "religion_related_major_preference": "Not relevant",
        },
        top_n=5,
        language="en",
    )
    service = __import__("app.services.ml_service", fromlist=["MLService"]).MLService()

    result = service.predict(req)

    assert result.fallback_used is True
    assert len(result.recommendations) == 5
    assert len({item.major for item in result.recommendations}) == 5
    assert any("fallback" in note.lower() for note in result.notes)
    assert any("neutral" in note.lower() for note in result.notes)
    for index, item in enumerate(result.recommendations, start=1):
        assert item.rank == index
        assert 0 <= item.suitability_score <= 100
        assert item.match_level in {"Strong match", "Good match", "Moderate match", "Exploratory match"}
        assert item.major
        assert {
            "model_score",
            "academic_fit_score",
            "interest_fit_score",
            "preference_fit_score",
            "optional_subject_boost",
        }.issubset(item.score_breakdown)
        assert item.explanation
        assert item.tradeoffs
        assert item.career_paths
        assert item.alternative_majors
        assert item.caution


def test_match_level_thresholds_are_exact():
    service = __import__("app.services.ml_service", fromlist=["MLService"]).MLService()

    assert service._match_level(85) == "Strong match"
    assert service._match_level(84) == "Good match"
    assert service._match_level(70) == "Good match"
    assert service._match_level(69) == "Moderate match"
    assert service._match_level(55) == "Moderate match"
    assert service._match_level(54) == "Exploratory match"


def test_weighted_score_uses_contract_weights_and_clamps():
    service = __import__("app.services.ml_service", fromlist=["MLService"]).MLService()

    assert service._weighted_score(
        {
            "model_score": 80,
            "academic_fit_score": 70,
            "interest_fit_score": 60,
            "preference_fit_score": 50,
            "optional_subject_boost": 40,
        }
    ) == 70
    assert service._weighted_score(
        {
            "model_score": 200,
            "academic_fit_score": 200,
            "interest_fit_score": 200,
            "preference_fit_score": 200,
            "optional_subject_boost": 200,
        }
    ) == 100


def test_fallback_handles_empty_interests_and_preferences():
    req = PredictRequest(
        sma_track="Merdeka",
        scores={"math": 82, "english": 79, "biology": 75, "chemistry": 76, "physics": 77, "advanced_math": 78},
        interests=[],
        preferences={"approach": ["Technical", "Social"]},
        selected_electives=["biology", "chemistry", "physics", "advanced_math"],
        top_n=3,
        language="en",
    )
    service = __import__("app.services.ml_service", fromlist=["MLService"]).MLService()

    result = service.predict(req)

    assert result.fallback_used is True
    assert len(result.recommendations) == 3
    assert result.recommendations[0].fit_summary


def test_load_missing_artifacts_does_not_raise(monkeypatch):
    service = __import__("app.services.ml_service", fromlist=["MLService"]).MLService()

    def missing(_path):
        raise FileNotFoundError("missing artifact")

    monkeypatch.setattr("app.services.ml_service.joblib.load", missing)

    service.load()

    assert service.model is None
    assert service.label_encoder is None


def test_model_prediction_failure_uses_fallback():
    class BrokenModel:
        def predict_proba(self, _features):
            raise RuntimeError("broken proba")

    class Labels:
        classes_ = ["Computer Science"]

    req = PredictRequest(
        sma_track="IPA",
        scores={"mathematics": 90, "english": 85},
        interests=[],
        preferences={},
        top_n=2,
        language="en",
    )
    service = __import__("app.services.ml_service", fromlist=["MLService"]).MLService()
    service.model = BrokenModel()
    service.label_encoder = Labels()

    result = service.predict(req)

    assert result.fallback_used is True
    assert any("fallback" in note.lower() for note in result.notes)
    assert len(result.recommendations) == 3


def test_log_prediction_payload_uses_canonical_score_keys_and_preserves_zero(monkeypatch):
    from app.core import db

    captured = {}

    class Query:
        def insert(self, payload):
            captured["payload"] = payload
            return self

        def execute(self):
            return None

    class Client:
        def table(self, name):
            captured["table"] = name
            return Query()

    req = PredictRequest(
        sma_track="IPA",
        scores={"mathematics": 0, "bahasa_indonesia": 0, "english": 0},
        interests=["Technology"],
        preferences={},
    )
    rec = RecommendationItem(
        rank=1,
        major="Computer Science",
        cluster="STEM / Technology",
        suitability_score=80,
        explanation=["fit"],
    )
    monkeypatch.setattr(db, "get_supabase", lambda: Client())

    db.log_prediction(req, [rec], latency_ms=12.345, fallback_used=True)

    assert captured["table"] == "prediction_log"
    assert captured["payload"]["math_score"] == 0
    assert captured["payload"]["indonesian_score"] == 0
    assert captured["payload"]["english_score"] == 0
    assert captured["payload"]["latency_ms"] == 12.35
    assert captured["payload"]["fallback_used"] is True
    assert captured["payload"]["model_version"] == MODEL_VERSION


def test_recommendation_response_contains_p0_contract_fields():
    item = RecommendationItem(
        rank=1,
        major="Data Science",
        cluster="STEM / Technology",
        suitability_score=87,
        match_level="Strong match",
        score_breakdown={
            "model_score": 84,
            "academic_fit_score": 90,
            "interest_fit_score": 92,
            "preference_fit_score": 85,
            "optional_subject_boost": 80,
        },
        explanation=["Your Mathematics and Informatics scores support technology-related fields."],
        tradeoffs=["This major may require consistency in mathematics and programming."],
        career_paths=["Data Analyst"],
        alternative_majors=["Computer Science"],
        caution="This recommendation is an exploration aid, not a final decision.",
    )
    response = PredictResponse(
        app="apti",
        model_version="apti_rf_v1.0",
        feature_version="apti_features_v1.0",
        recommendations=[item],
        profile_summary={
            "strongest_area": "Technology & Quantitative",
            "academic_pattern": "Strong in math and technology-related subjects",
            "interest_pattern": "Technology-oriented",
            "preference_pattern": "Independent and systems-oriented",
            "input_completeness_score": 82,
        },
        notes=["Optional missing subjects were treated neutrally, not as low scores."],
        fallback_used=False,
        latency_ms=123,
    )

    assert response.app == "apti"
    assert response.recommendations[0].score_breakdown["model_score"] == 84
