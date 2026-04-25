# Purpose: Verify religion-major preference sanity without inferring user identity.
# Callers: pytest religion sanity suite.
# Deps: app.schemas, app.services.ml_service.
# API: Pytest tests for preference-based filtering and explanations.
# Side effects: None.

from app.schemas import PredictRequest
from app.services.ml_service import MLService


def base_request(preference: str) -> PredictRequest:
    return PredictRequest(
        sma_track="IPS",
        scores={"religion": 92, "history": 86, "sociology": 84, "english": 82, "indonesian": 80},
        interests=["Education", "Social"],
        preferences={"approach": "Social", "religion_related_major_preference": preference},
        top_n=5,
        language="en",
    )


def test_not_relevant_downranks_religion_majors_from_top_three():
    service = MLService()
    req = base_request("Not relevant")
    scored = [("Islamic Education", 99), ("Islamic Studies", 98), ("Theology", 97), ("Psychology", 60), ("Management", 55)]
    recommendations = [service._build_recommendation(req, rank, major, score) for rank, (major, score) in enumerate(scored, start=1)]

    majors = [item.major for item in service._apply_sanity_layer(req, recommendations)[:3]]

    assert "Islamic Education" not in majors
    assert "Islamic Studies" not in majors
    assert "Theology" not in majors


def test_final_recommendation_scores_are_non_increasing_by_rank():
    service = MLService()
    req = base_request("Not relevant")

    result = service.predict(req)
    scores = [item.suitability_score for item in result.recommendations]

    assert scores == sorted(scores, reverse=True)


def test_not_relevant_can_retain_religion_majors_outside_top_three():
    service = MLService()
    req = base_request("Not relevant")
    scored = [("Islamic Education", 99), ("Islamic Studies", 98), ("Theology", 97), ("Psychology", 60), ("Management", 55)]
    recommendations = [service._build_recommendation(req, rank, major, score) for rank, (major, score) in enumerate(scored, start=1)]

    adjusted = service._apply_sanity_layer(req, recommendations)
    majors = [item.major for item in adjusted]

    assert any(major in {"Islamic Education", "Islamic Studies", "Theology"} for major in majors[3:])
    assert all(major not in {"Islamic Education", "Islamic Studies", "Theology"} for major in majors[:3])


def test_islamic_studies_preference_allows_islamic_education_with_safe_explanation():
    service = MLService()
    req = base_request("Islamic studies / education")

    result = service.predict(req)
    islamic = next(item for item in result.recommendations if item.major == "Islamic Education")
    explanation = " ".join(islamic.explanation).lower()

    assert islamic.major == "Islamic Education"
    assert "selected preference" in explanation or "stated preference" in explanation
    assert "identity" not in explanation
    assert "your religion" not in explanation
