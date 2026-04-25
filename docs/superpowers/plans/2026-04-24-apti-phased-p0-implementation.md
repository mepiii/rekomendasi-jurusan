# Apti Phased P0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stabilize current Apti frontend changes, then implement robust backend/ML P0 prediction contract, then integrate frontend result UI against that contract.

**Architecture:** Work in three ordered slices: stabilize existing frontend diff, upgrade backend prediction pipeline and response contract, then adapt frontend form/results. Backend keeps current FastAPI service boundaries and adds focused helpers inside `app/services/ml_service.py` and `app/recommendation_config.py` before extracting only if files become hard to reason about.

**Tech Stack:** React, Vite, Vitest, Tailwind, Framer Motion, FastAPI, Pydantic v2, scikit-learn, pandas, joblib, Supabase Python client.

---

## File map

### Phase 1 stabilization

- Modify only if tests fail: `frontend/src/App.jsx`
- Modify only if tests fail: `frontend/src/components/features/AptiIntroFlow.jsx`
- Modify only if tests fail: `frontend/src/components/features/RecommendationJourney.jsx`
- Modify only if tests fail: `frontend/src/lib/recommendationConfig.js`
- Modify only if tests fail: `frontend/src/styles.css`
- Test existing: `frontend/src/App.test.jsx`
- Test existing: `frontend/src/lib/introState.test.js`
- Test existing: `frontend/src/lib/themeState.test.js`

### Phase 2 backend/ML P0

- Modify: `backend/app/recommendation_config.py` — canonical constants, major metadata, interest clusters, religion-related majors, version constants.
- Modify: `backend/app/schemas.py` — request/response schema and validators.
- Modify: `backend/app/services/ml_service.py` — feature row, fallback, top-N scoring, explanation engine, sanity reranking.
- Modify: `backend/app/api/routes.py` — response assembly, latency, health response, logging payload.
- Modify: `backend/app/core/db.py` — non-blocking logging payload compatibility if needed.
- Modify: `backend/app/config.py` — Apti app metadata/version defaults if missing.
- Create if test directory exists or create minimal package: `backend/tests/test_predict_contract.py` — schema and service contract tests.
- Create if test directory exists or create minimal package: `backend/tests/test_religion_sanity.py` — religion preference safety tests.

### Phase 3 frontend integration

- Modify: `frontend/src/lib/api.js` — preserve `/predict` call and tolerate improved response.
- Modify: `frontend/src/components/features/RecommendationJourney.jsx` — advanced preferences and payload shape.
- Modify: `frontend/src/components/features/ResultCardAdvanced.jsx` — display new recommendation fields.
- Modify: `frontend/src/components/features/ResultSectionAdvanced.jsx` — notes/profile summary/fallback state.
- Modify: `frontend/src/lib/recommendationConfig.js` — richer interests/preferences compatible with backend.
- Modify/add tests near existing frontend tests if current test style supports it.

### Documentation after implementation

- Modify: `README.md` — only after behavior is implemented and verified.

---

## Task 1: Stabilize current frontend diff

**Files:**
- Read/verify: `frontend/src/App.jsx`
- Read/verify: `frontend/src/components/features/AptiIntroFlow.jsx`
- Read/verify: `frontend/src/components/features/RecommendationJourney.jsx`
- Read/verify: `frontend/src/lib/recommendationConfig.js`
- Read/verify: `frontend/src/styles.css`

- [ ] **Step 1: Run frontend tests**

Run:

```bash
cd frontend && npm test -- --run
```

Expected: tests pass. If they fail, capture failing test name and exact error.

- [ ] **Step 2: Run frontend production build**

Run:

```bash
cd frontend && npm run build
```

Expected: build succeeds. Vite deprecation or bundle warnings may appear; do not treat warnings as failures unless build exits non-zero.

- [ ] **Step 3: If tests/build fail, inspect only changed frontend files**

Use targeted reads for failing file(s). Expected failure classes from current diff:

- `AptiIntroFlow` missing default `locale` fallback.
- `RecommendationJourney` tests expecting string interests/preferences but config now stores `{ value, label }` objects.
- `recommendationConfig` changed option data shape but downstream code still expects strings.

- [ ] **Step 4: Fix only stabilization failures**

Allowed fixes:

```jsx
const content = introCopy[locale] || introCopy.en;
```

```jsx
const optionValue = typeof option === 'string' ? option : option.value;
const optionLabel = typeof option === 'string' ? option : option.label[locale] || option.label.en;
```

Do not add backend/ML/documentation work in this task.

- [ ] **Step 5: Re-run frontend tests and build**

Run:

```bash
cd frontend && npm test -- --run && npm run build
```

Expected: both pass, or exact blocker documented.

---

## Task 2: Add backend version and recommendation constants

**Files:**
- Modify: `backend/app/recommendation_config.py`
- Test: `backend/tests/test_predict_contract.py`

- [ ] **Step 1: Create failing constants test**

Create `backend/tests/test_predict_contract.py` if missing:

```python
from app.recommendation_config import (
    DATASET_VERSION,
    FEATURE_VERSION,
    MODEL_VERSION,
    RELIGION_RELATED_MAJORS,
    VALID_RELIGION_RELATED_MAJOR_PREFERENCES,
)


def test_apti_versions_are_canonical():
    assert MODEL_VERSION == "apti_rf_v1.0"
    assert FEATURE_VERSION == "apti_features_v1.0"
    assert DATASET_VERSION == "apti_dataset_v1.0"


def test_religion_preferences_are_not_identity_labels():
    assert "Not relevant" in VALID_RELIGION_RELATED_MAJOR_PREFERENCES
    assert "Islamic studies / education" in VALID_RELIGION_RELATED_MAJOR_PREFERENCES
    assert "What is your religion?" not in VALID_RELIGION_RELATED_MAJOR_PREFERENCES
    assert "Islamic Education" in RELIGION_RELATED_MAJORS
```

- [ ] **Step 2: Run failing test**

Run:

```bash
PYTHONPATH=backend pytest backend/tests/test_predict_contract.py -q
```

Expected before implementation: import failure or assertion failure for missing constants.

- [ ] **Step 3: Add constants**

In `backend/app/recommendation_config.py`, add or preserve existing data and include:

```python
MODEL_VERSION = "apti_rf_v1.0"
FEATURE_VERSION = "apti_features_v1.0"
DATASET_VERSION = "apti_dataset_v1.0"
APP_IDENTIFIER = "apti"

VALID_RELIGION_RELATED_MAJOR_PREFERENCES = {
    "Not relevant",
    "Open to religious studies",
    "Islamic studies / education",
    "Christian theology / education",
    "Catholic theology / education",
    "Hindu studies",
    "Buddhist studies",
    "Other / unsure",
}

RELIGION_RELATED_MAJORS = {
    "Islamic Education",
    "Islamic Studies",
    "Theology",
    "Christian Religious Education",
    "Catholic Religious Education",
    "Religious Studies",
}

MAJOR_CLUSTERS = {
    "STEM / Technology": [
        "Computer Science",
        "Informatics Engineering",
        "Information Systems",
        "Data Science",
        "Electrical Engineering",
        "Mechanical Engineering",
        "Civil Engineering",
        "Industrial Engineering",
        "Architecture",
        "Cybersecurity",
    ],
    "Health / Natural Science": [
        "Medicine",
        "Nursing",
        "Pharmacy",
        "Nutrition",
        "Public Health",
        "Biology",
        "Chemistry",
        "Mathematics",
        "Statistics",
        "Environmental Science",
    ],
    "Business / Economy": [
        "Management",
        "Accounting",
        "Development Economics",
        "Digital Business",
        "Entrepreneurship",
        "Business Administration",
        "Finance",
    ],
    "Social / Humanities": [
        "Psychology",
        "Law",
        "Communication Science",
        "International Relations",
        "Sociology",
        "Political Science",
        "Public Administration",
    ],
    "Language / Culture": [
        "Indonesian Literature",
        "English Literature",
        "Japanese Literature",
        "French Literature",
        "Linguistics",
        "Anthropology",
        "Indonesian Language Education",
        "English Education",
        "Translation Studies",
    ],
    "Creative": [
        "Visual Communication Design",
        "Product Design",
        "Film and Television",
        "Fine Arts",
        "Music",
        "Animation",
        "Creative Media",
    ],
    "Education": [
        "Elementary Teacher Education",
        "Guidance and Counseling",
        "Educational Technology",
        "Mathematics Education",
        "Biology Education",
        "Economics Education",
        "Language Education",
    ],
    "Religion-related": sorted(RELIGION_RELATED_MAJORS),
}

MAJOR_CLUSTER_MAP = {
    major: cluster for cluster, majors in MAJOR_CLUSTERS.items() for major in majors
}
```

Preserve existing `VALID_INTERESTS`, `VALID_PREFERENCE_VALUES`, `VALID_SMA_TRACKS`, `TRACK_SUBJECT_RULES`, and `MAJOR_METADATA`; extend rather than delete unless duplicated.

- [ ] **Step 4: Run constants test**

Run:

```bash
PYTHONPATH=backend pytest backend/tests/test_predict_contract.py -q
```

Expected: new constants tests pass or only later contract tests fail after they are added.

---

## Task 3: Update schemas for nullable optionals and richer response

**Files:**
- Modify: `backend/app/schemas.py`
- Test: `backend/tests/test_predict_contract.py`

- [ ] **Step 1: Add failing schema tests**

Append to `backend/tests/test_predict_contract.py`:

```python
from pydantic import ValidationError

from app.schemas import PredictRequest, PredictResponse, RecommendationItem


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


def test_predict_request_rejects_out_of_range_scores():
    try:
        PredictRequest(sma_track="IPA", scores={"mathematics": 101}, interests=[], preferences={})
    except ValidationError as exc:
        assert "0 and 100" in str(exc) or "less than or equal" in str(exc)
    else:
        raise AssertionError("Expected validation error")


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
```

- [ ] **Step 2: Run failing schema tests**

Run:

```bash
PYTHONPATH=backend pytest backend/tests/test_predict_contract.py -q
```

Expected: failures for schema field types or missing response fields.

- [ ] **Step 3: Update `PredictRequest` fields**

In `backend/app/schemas.py`, use these field shapes while preserving existing names where possible:

```python
class PredictRequest(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    sma_track: str
    scores: dict[str, float | None] = Field(default_factory=dict)
    interests: list[str] = Field(default_factory=list)
    preferences: dict[str, str | list[str]] = Field(default_factory=dict)
    top_n: int = Field(default=5, ge=3, le=5)
    language: str = "en"
```

If existing `top_n` has no clamp, add a `field_validator("top_n", mode="before")`:

```python
@field_validator("top_n", mode="before")
@classmethod
def clamp_top_n(cls, value: int | None) -> int:
    if value is None:
        return 5
    return min(5, max(3, int(value)))
```

- [ ] **Step 4: Update validators**

Use this behavior:

```python
@field_validator("scores")
@classmethod
def validate_scores(cls, values: dict[str, float | None]) -> dict[str, float | None]:
    for subject, score in values.items():
        if score is None:
            continue
        if score < 0 or score > 100:
            raise ValueError(f"{subject} must be between 0 and 100")
    return values
```

For interests, keep known interests but do not crash on unknown values:

```python
@field_validator("interests")
@classmethod
def validate_interests(cls, values: list[str]) -> list[str]:
    return [value.strip() for value in values if value and value.strip()]
```

For preferences, allow strings and lists:

```python
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
```

- [ ] **Step 5: Update response models**

In `RecommendationItem`, include:

```python
rank: int
major: str
cluster: str
suitability_score: int
match_level: str
score_breakdown: dict[str, int]
explanation: list[str]
tradeoffs: list[str] = Field(default_factory=list)
career_paths: list[str] = Field(default_factory=list)
alternative_majors: list[str] = Field(default_factory=list)
caution: str | None = None
```

In `PredictResponse`, include:

```python
app: str = "apti"
model_version: str
feature_version: str
session_id: UUID | None = None
recommendations: list[RecommendationItem]
profile_summary: ProfileSummary | dict[str, object]
notes: list[str] = Field(default_factory=list)
fallback_used: bool = False
latency_ms: int
```

- [ ] **Step 6: Run schema tests**

Run:

```bash
PYTHONPATH=backend pytest backend/tests/test_predict_contract.py -q
```

Expected: schema tests pass; service tests may not exist yet.

---

## Task 4: Implement safe feature helpers and optional handling

**Files:**
- Modify: `backend/app/services/ml_service.py`
- Test: `backend/tests/test_predict_contract.py`

- [ ] **Step 1: Add failing feature helper tests**

Append:

```python
from app.services.ml_service import ml_service


def test_optional_subjects_are_neutral_when_missing():
    req = PredictRequest(
        sma_track="IPA",
        scores={
            "mathematics": 80,
            "bahasa_indonesia": 80,
            "english": 80,
            "history": 80,
            "civics": 80,
            "physics": 80,
            "chemistry": 80,
            "biology": 80,
            "informatics": None,
            "religion_ethics": None,
        },
        interests=["Technology"],
        preferences={"religion_related_major_preference": "Not relevant"},
    )

    row = ml_service._to_feature_row(req).iloc[0].to_dict()

    assert row["has_informatics"] == 0
    assert row["has_religion_ethics"] == 0
    assert row["optional_subject_count"] == 0
    assert row["optional_subject_boost"] == 50


def test_optional_subjects_are_bonus_when_present():
    req = PredictRequest(
        sma_track="IPA",
        scores={"mathematics": 80, "informatics": 92, "religion_ethics": 88},
        interests=["Technology"],
        preferences={"religion_related_major_preference": "Not relevant"},
    )

    row = ml_service._to_feature_row(req).iloc[0].to_dict()

    assert row["has_informatics"] == 1
    assert row["has_religion_ethics"] == 1
    assert row["optional_subject_count"] == 2
    assert row["optional_subject_boost"] >= 50
```

- [ ] **Step 2: Run failing helper tests**

Run:

```bash
PYTHONPATH=backend pytest backend/tests/test_predict_contract.py::test_optional_subjects_are_neutral_when_missing backend/tests/test_predict_contract.py::test_optional_subjects_are_bonus_when_present -q
```

Expected: missing feature columns or incorrect null handling.

- [ ] **Step 3: Add optional subject constants inside `MLService` or module level**

Add near existing subject group constants:

```python
OPTIONAL_SUBJECTS = {
    "regional_language": "has_regional_language",
    "arts_culture": "has_art",
    "pkwu": "has_pkwu",
    "prakarya": "has_pkwu",
    "pe": "has_pe",
    "religion_ethics": "has_religion_ethics",
    "informatics": "has_informatics",
}
```

- [ ] **Step 4: Update `_subject_groups` to ignore `None`**

Use helper:

```python
def _avg(scores: dict[str, float | None], subjects: list[str], default: float = 50.0) -> float:
    values = [float(scores[name]) for name in subjects if scores.get(name) is not None]
    return round(sum(values) / len(values), 2) if values else default
```

Then group averages must call `_avg` instead of treating missing values as zero.

- [ ] **Step 5: Update `_to_feature_row` optional fields**

After copying scores and derived averages, add:

```python
present_optional_scores = [
    float(req.scores[name])
    for name in OPTIONAL_SUBJECTS
    if req.scores.get(name) is not None
]

for subject, flag_name in OPTIONAL_SUBJECTS.items():
    row[flag_name] = 1 if req.scores.get(subject) is not None else 0

row["optional_subject_count"] = len(present_optional_scores)
row["avg_optional_available"] = round(sum(present_optional_scores) / len(present_optional_scores), 2) if present_optional_scores else 50
row["optional_subject_boost"] = row["avg_optional_available"] if present_optional_scores else 50
row["optional_completeness_score"] = round(100 * len(present_optional_scores) / len(OPTIONAL_SUBJECTS))
```

- [ ] **Step 6: Run helper tests**

Run:

```bash
PYTHONPATH=backend pytest backend/tests/test_predict_contract.py -q
```

Expected: helper/schema tests pass.

---

## Task 5: Add scoring, match levels, and fallback recommendations

**Files:**
- Modify: `backend/app/services/ml_service.py`
- Test: `backend/tests/test_predict_contract.py`

- [ ] **Step 1: Add failing prediction contract test**

Append:

```python

def test_predict_returns_top_n_contract_when_model_unavailable(monkeypatch):
    monkeypatch.setattr(ml_service, "model", None, raising=False)
    monkeypatch.setattr(ml_service, "label_encoder", None, raising=False)

    req = PredictRequest(
        sma_track="IPA",
        scores={
            "mathematics": 88,
            "bahasa_indonesia": 84,
            "english": 90,
            "physics": 85,
            "chemistry": 78,
            "biology": 80,
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
        top_n=5,
    )

    output = ml_service.predict(req)

    assert output.fallback_used is True
    assert len(output.recommendations) == 5
    first = output.recommendations[0]
    assert first.rank == 1
    assert 0 <= first.suitability_score <= 100
    assert first.score_breakdown["optional_subject_boost"] >= 50
    assert first.explanation
    assert first.tradeoffs
```

- [ ] **Step 2: Run failing test**

Run:

```bash
PYTHONPATH=backend pytest backend/tests/test_predict_contract.py::test_predict_returns_top_n_contract_when_model_unavailable -q
```

Expected: `PredictionOutput` lacks `fallback_used`, response item lacks fields, or predict crashes when model unavailable.

- [ ] **Step 3: Update `PredictionOutput` dataclass**

In `backend/app/services/ml_service.py`:

```python
@dataclass
class PredictionOutput:
    recommendations: list[RecommendationItem]
    profile_summary: ProfileSummary
    notes: list[str]
    fallback_used: bool
```

- [ ] **Step 4: Add scoring helpers**

Add methods on `MLService`:

```python
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
        0.45 * breakdown["model_score"]
        + 0.25 * breakdown["academic_fit_score"]
        + 0.15 * breakdown["interest_fit_score"]
        + 0.10 * breakdown["preference_fit_score"]
        + 0.05 * breakdown["optional_subject_boost"]
    )
    return int(round(max(0, min(100, score))))
```

- [ ] **Step 5: Add fallback candidate generation**

Use major metadata and cluster fit. Minimal fallback logic:

```python
def _fallback_candidates(self, req: PredictRequest) -> list[str]:
    interests = {interest.lower() for interest in req.interests}
    groups = self._subject_groups(req.scores)
    candidates: list[str] = []

    if groups.get("science", 50) >= 75 or groups.get("math", 50) >= 75 or {"technology", "ai / data", "data / ai"} & interests:
        candidates.extend(["Data Science", "Computer Science", "Information Systems"])
    if groups.get("social", 50) >= 70 or {"business", "law", "psychology", "social"} & interests:
        candidates.extend(["Psychology", "Management", "Communication Science"])
    if groups.get("language", 50) >= 70 or {"language", "media"} & interests:
        candidates.extend(["English Literature", "Communication Science", "Translation Studies"])
    if {"design", "creative", "media"} & interests:
        candidates.extend(["Visual Communication Design", "Creative Media", "Product Design"])

    candidates.extend(["Management", "Public Administration", "Educational Technology"])
    return list(dict.fromkeys(candidates))
```

Adapt subject group keys to current `_subject_groups` output.

- [ ] **Step 6: Add recommendation builder**

Add:

```python
def _build_recommendation(self, req: PredictRequest, major: str, rank: int, model_score: int, fallback_used: bool) -> RecommendationItem:
    row = self._to_feature_row(req).iloc[0].to_dict()
    academic_fit = self._academic_fit_score(req, major)
    interest_fit = self._interest_fit_score(req, major)
    preference_fit = self._preference_fit_score(req, major)
    optional_boost = int(row.get("optional_subject_boost", 50))
    breakdown = {
        "model_score": int(model_score),
        "academic_fit_score": int(academic_fit),
        "interest_fit_score": int(interest_fit),
        "preference_fit_score": int(preference_fit),
        "optional_subject_boost": optional_boost,
    }
    suitability = self._weighted_score(breakdown)
    return RecommendationItem(
        rank=rank,
        major=major,
        cluster=MAJOR_CLUSTER_MAP.get(major, MAJOR_METADATA.get(major, {}).get("cluster", "General")),
        suitability_score=suitability,
        match_level=self._match_level(suitability),
        score_breakdown=breakdown,
        explanation=self._explanation_bullets(req, major),
        tradeoffs=self._tradeoffs_for_major(major),
        career_paths=MAJOR_METADATA.get(major, {}).get("career_paths", []),
        alternative_majors=MAJOR_METADATA.get(major, {}).get("alternative_majors", []),
        caution="This recommendation is an exploration aid, not a final decision.",
    )
```

If helper names do not exist yet, implement them in next step before running tests.

- [ ] **Step 7: Add minimal fit/explanation helpers**

Implement deterministic helpers returning 0–100:

```python
def _academic_fit_score(self, req: PredictRequest, major: str) -> int:
    groups = self._subject_groups(req.scores)
    cluster = MAJOR_CLUSTER_MAP.get(major, MAJOR_METADATA.get(major, {}).get("cluster", ""))
    if "Technology" in cluster:
        return int(round((groups.get("math", 50) + groups.get("science", 50)) / 2))
    if "Health" in cluster:
        return int(round(groups.get("science", 50)))
    if "Business" in cluster:
        return int(round((groups.get("math", 50) + groups.get("social", 50)) / 2))
    if "Social" in cluster:
        return int(round((groups.get("social", 50) + groups.get("language", 50)) / 2))
    if "Language" in cluster:
        return int(round(groups.get("language", 50)))
    if "Creative" in cluster:
        return int(round((groups.get("language", 50) + groups.get("creative", 50)) / 2))
    return int(round(sum(groups.values()) / len(groups))) if groups else 50
```

```python
def _interest_fit_score(self, req: PredictRequest, major: str) -> int:
    wanted = {item.lower() for item in MAJOR_METADATA.get(major, {}).get("interests", [])}
    selected = {item.lower() for item in req.interests}
    if not selected:
        return 50
    overlap = len(wanted & selected)
    return int(min(100, 55 + overlap * 15)) if overlap else 50
```

```python
def _preference_fit_score(self, req: PredictRequest, major: str) -> int:
    values: list[str] = []
    for value in req.preferences.values():
        values.extend(value if isinstance(value, list) else [value])
    selected = {item.lower() for item in values}
    wanted = {item.lower() for item in MAJOR_METADATA.get(major, {}).get("preferences", [])}
    if not selected:
        return 50
    overlap = len(wanted & selected)
    return int(min(100, 55 + overlap * 15)) if overlap else 50
```

```python
def _explanation_bullets(self, req: PredictRequest, major: str) -> list[str]:
    interests = ", ".join(req.interests[:3]) or "your selected interests"
    return [
        f"Your academic profile provides useful signals for {major}.",
        f"Your interest in {interests} helps shape this recommendation.",
        "This recommendation is a starting point for exploration, not a final decision.",
    ]

@staticmethod
def _tradeoffs_for_major(major: str) -> list[str]:
    return [f"{major} may require building consistent study habits and field-specific skills."]
```

- [ ] **Step 8: Update `predict` fallback path**

At start of `predict`, compute candidates even if model missing:

```python
fallback_used = not self.loaded
notes = []

if fallback_used:
    majors = self._fallback_candidates(req)
    notes.append("The ML model was unavailable, so Apti used a rule-based fallback recommendation.")
else:
    # keep existing model probability path, then map top classes to majors and model_score 0-100
```

For fallback:

```python
items = [self._build_recommendation(req, major, idx + 1, 60, True) for idx, major in enumerate(majors[: req.top_n])]
items = self._apply_sanity_layer(req, items)[: req.top_n]
for idx, item in enumerate(items, start=1):
    item.rank = idx
return PredictionOutput(
    recommendations=items,
    profile_summary=self._build_profile_summary(req),
    notes=notes + ["Optional missing subjects were treated neutrally, not as low scores."],
    fallback_used=fallback_used,
)
```

If Pydantic models are frozen, recreate items with `model_copy(update={"rank": idx})`.

- [ ] **Step 9: Run prediction contract test**

Run:

```bash
PYTHONPATH=backend pytest backend/tests/test_predict_contract.py -q
```

Expected: tests pass or only sanity-layer tests still missing.

---

## Task 6: Add religion sanity layer

**Files:**
- Modify: `backend/app/services/ml_service.py`
- Test: `backend/tests/test_religion_sanity.py`

- [ ] **Step 1: Add failing religion tests**

Create `backend/tests/test_religion_sanity.py`:

```python
from app.schemas import PredictRequest
from app.services.ml_service import ml_service
from app.recommendation_config import RELIGION_RELATED_MAJORS


def _request(preference: str) -> PredictRequest:
    return PredictRequest(
        sma_track="IPS",
        scores={
            "mathematics": 72,
            "bahasa_indonesia": 84,
            "english": 82,
            "history": 85,
            "civics": 83,
            "religion_ethics": 90,
        },
        interests=["Education", "Social"],
        preferences={"religion_related_major_preference": preference},
        top_n=5,
    )


def test_not_relevant_religion_preference_downranks_religion_majors(monkeypatch):
    monkeypatch.setattr(ml_service, "model", None, raising=False)
    monkeypatch.setattr(ml_service, "label_encoder", None, raising=False)

    output = ml_service.predict(_request("Not relevant"))

    top_majors = [item.major for item in output.recommendations[:3]]
    assert not any(major in RELIGION_RELATED_MAJORS for major in top_majors)


def test_explicit_islamic_preference_allows_religion_major(monkeypatch):
    monkeypatch.setattr(ml_service, "model", None, raising=False)
    monkeypatch.setattr(ml_service, "label_encoder", None, raising=False)

    output = ml_service.predict(_request("Islamic studies / education"))

    assert any(item.major == "Islamic Education" for item in output.recommendations)
    explanation_text = " ".join(" ".join(item.explanation) for item in output.recommendations if item.major == "Islamic Education")
    assert "selected" in explanation_text.lower() or "preference" in explanation_text.lower()
```

- [ ] **Step 2: Run failing religion tests**

Run:

```bash
PYTHONPATH=backend pytest backend/tests/test_religion_sanity.py -q
```

Expected: religion major ranking not controlled yet or fallback lacks Islamic Education candidate.

- [ ] **Step 3: Add preference reader**

In `MLService`:

```python
@staticmethod
def _religion_preference(req: PredictRequest) -> str:
    value = req.preferences.get("religion_related_major_preference", "Not relevant")
    return value if isinstance(value, str) else "Not relevant"
```

- [ ] **Step 4: Update fallback candidates for religion preference**

In `_fallback_candidates`:

```python
religion_preference = self._religion_preference(req)
if religion_preference == "Islamic studies / education":
    candidates.extend(["Islamic Education", "Islamic Studies"])
elif religion_preference in {"Christian theology / education", "Catholic theology / education", "Open to religious studies", "Other / unsure"}:
    candidates.extend(["Religious Studies", "Theology"])
```

- [ ] **Step 5: Add `_apply_sanity_layer`**

```python
def _apply_sanity_layer(self, req: PredictRequest, items: list[RecommendationItem]) -> list[RecommendationItem]:
    religion_preference = self._religion_preference(req)
    adjusted: list[RecommendationItem] = []
    for item in items:
        score = item.suitability_score
        breakdown = dict(item.score_breakdown)
        if item.major in RELIGION_RELATED_MAJORS and religion_preference == "Not relevant":
            score = min(score, 54)
            breakdown["preference_fit_score"] = min(breakdown.get("preference_fit_score", 50), 40)
        elif item.major in RELIGION_RELATED_MAJORS and religion_preference != "Not relevant":
            score = min(100, score + 12)
            breakdown["preference_fit_score"] = max(breakdown.get("preference_fit_score", 50), 85)
        adjusted.append(item.model_copy(update={
            "suitability_score": score,
            "match_level": self._match_level(score),
            "score_breakdown": breakdown,
        }))
    return sorted(adjusted, key=lambda recommendation: recommendation.suitability_score, reverse=True)
```

- [ ] **Step 6: Add religion explanation branch**

In `_explanation_bullets`, before generic return:

```python
if major in RELIGION_RELATED_MAJORS:
    preference = self._religion_preference(req)
    return [
        f"{major} appears because you selected a preference for {preference}.",
        "Apti treats this as an academic preference, not as an assumption about personal identity.",
        "This recommendation is a starting point for exploration, not a final decision.",
    ]
```

- [ ] **Step 7: Run religion tests**

Run:

```bash
PYTHONPATH=backend pytest backend/tests/test_religion_sanity.py backend/tests/test_predict_contract.py -q
```

Expected: all backend tests pass.

---

## Task 7: Wire route response, latency, health, and non-blocking logging

**Files:**
- Modify: `backend/app/api/routes.py`
- Modify: `backend/app/core/db.py` if logging serialization fails
- Test: `backend/tests/test_predict_contract.py`

- [ ] **Step 1: Add route-level tests if FastAPI TestClient dependencies are available**

Append to `backend/tests/test_predict_contract.py`:

```python
from fastapi.testclient import TestClient
from app.main import app


def test_health_contract():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["app"] == "apti"
    assert "model_version" in body
    assert "feature_version" in body
    assert "supabase_configured" in body


def test_predict_route_contract(monkeypatch):
    monkeypatch.setattr(ml_service, "model", None, raising=False)
    monkeypatch.setattr(ml_service, "label_encoder", None, raising=False)
    client = TestClient(app)
    response = client.post("/predict", json={
        "sma_track": "IPA",
        "scores": {"mathematics": 88, "english": 90, "informatics": 92},
        "interests": ["Technology", "AI / Data"],
        "preferences": {"religion_related_major_preference": "Not relevant"},
        "top_n": 5,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["app"] == "apti"
    assert body["fallback_used"] is True
    assert isinstance(body["latency_ms"], int)
    assert len(body["recommendations"]) >= 3
```

- [ ] **Step 2: Run failing route tests**

Run:

```bash
PYTHONPATH=backend pytest backend/tests/test_predict_contract.py::test_health_contract backend/tests/test_predict_contract.py::test_predict_route_contract -q
```

Expected: health schema lacks fields or predict route response assembly lacks new fields.

- [ ] **Step 3: Update health route**

In `backend/app/api/routes.py`, return:

```python
return {
    "app": "apti",
    "status": "ok",
    "model_loaded": ml_service.loaded,
    "model_version": MODEL_VERSION,
    "feature_version": FEATURE_VERSION,
    "supabase_configured": bool(settings.supabase_url and settings.supabase_key),
    "timestamp": datetime.now(timezone.utc).isoformat(),
}
```

Import `MODEL_VERSION`, `FEATURE_VERSION` from `app.recommendation_config`.

- [ ] **Step 4: Update predict route response assembly**

In `predict`, measure latency with existing `perf_counter`:

```python
start = perf_counter()
output = ml_service.predict(payload)
latency_ms = int((perf_counter() - start) * 1000)
response = PredictResponse(
    app="apti",
    model_version=MODEL_VERSION,
    feature_version=FEATURE_VERSION,
    session_id=payload.session_id,
    recommendations=output.recommendations,
    profile_summary=output.profile_summary,
    notes=output.notes,
    fallback_used=output.fallback_used,
    latency_ms=latency_ms,
)
```

Return `response`.

- [ ] **Step 5: Make logging non-blocking**

Wrap prediction logging in route with broad exception catch if not already done:

```python
try:
    log_prediction(payload, response.recommendations, latency_ms=latency_ms, fallback_used=response.fallback_used)
except Exception:
    pass
```

If `log_prediction` signature differs, update `backend/app/core/db.py` to accept optional keyword args with defaults:

```python
def log_prediction(request: PredictRequest, recommendations: list[RecommendationItem], latency_ms: int | None = None, fallback_used: bool = False) -> None:
    ...
```

- [ ] **Step 6: Run route tests and compile**

Run:

```bash
PYTHONPATH=backend pytest backend/tests/test_predict_contract.py backend/tests/test_religion_sanity.py -q
python -m compileall backend/app
```

Expected: tests pass and compile succeeds.

---

## Task 8: Frontend integration for advanced preferences and improved result cards

**Files:**
- Modify: `frontend/src/lib/recommendationConfig.js`
- Modify: `frontend/src/components/features/RecommendationJourney.jsx`
- Modify: `frontend/src/components/features/ResultCardAdvanced.jsx`
- Modify: `frontend/src/components/features/ResultSectionAdvanced.jsx`
- Modify only if needed: `frontend/src/lib/api.js`

- [ ] **Step 1: Add frontend config values**

In `frontend/src/lib/recommendationConfig.js`, add preferences without removing existing values abruptly:

```js
export const religionRelatedMajorPreferences = [
  { value: 'Not relevant', label: { en: 'Not relevant', id: 'Tidak relevan' } },
  { value: 'Open to religious studies', label: { en: 'Open to religious studies', id: 'Terbuka untuk studi keagamaan' } },
  { value: 'Islamic studies / education', label: { en: 'Islamic studies / education', id: 'Studi / pendidikan Islam' } },
  { value: 'Christian theology / education', label: { en: 'Christian theology / education', id: 'Teologi / pendidikan Kristen' } },
  { value: 'Catholic theology / education', label: { en: 'Catholic theology / education', id: 'Teologi / pendidikan Katolik' } },
  { value: 'Hindu studies', label: { en: 'Hindu studies', id: 'Studi Hindu' } },
  { value: 'Buddhist studies', label: { en: 'Buddhist studies', id: 'Studi Buddha' } },
  { value: 'Other / unsure', label: { en: 'Other / unsure', id: 'Lainnya / belum yakin' } }
];
```

- [ ] **Step 2: Add advanced preferences UI**

In `RecommendationJourney.jsx`, place after main preferences section:

```jsx
<section className="rounded-3xl border border-borderSoft bg-surfaceSoft/70 p-5">
  <button
    type="button"
    onClick={() => setAdvancedOpen((value) => !value)}
    className="flex w-full items-center justify-between text-left"
  >
    <span className="text-sm font-semibold text-textPrimary">
      {locale === 'id' ? 'Preferensi lanjutan' : 'Advanced preferences'}
    </span>
    <span className="text-xs text-textSubtle">
      {advancedOpen ? (locale === 'id' ? 'Tutup' : 'Hide') : (locale === 'id' ? 'Buka' : 'Show')}
    </span>
  </button>
  {advancedOpen ? (
    <div className="mt-4 space-y-3">
      <p className="text-sm text-textSecondary">
        {locale === 'id' ? 'Apakah kamu tertarik dengan program studi terkait agama?' : 'Are you interested in religion-related study programs?'}
      </p>
      <div className="flex flex-wrap gap-2">
        {religionRelatedMajorPreferences.map((option) => {
          const active = preferences.religion_related_major_preference === option.value;
          return (
            <button
              key={option.value}
              type="button"
              onClick={() => setPreferences((prev) => ({ ...prev, religion_related_major_preference: option.value }))}
              className={`editorial-chip rounded-full px-3 py-1 text-xs transition ${active ? 'apti-choice-active border-accent/30 bg-accent/10 text-accent' : 'apti-choice-idle'}`}
            >
              {option.label[locale] || option.label.en}
            </button>
          );
        })}
      </div>
    </div>
  ) : null}
</section>
```

Add `advancedOpen` state and import `religionRelatedMajorPreferences`.

- [ ] **Step 3: Ensure payload defaults religion preference**

Before submit payload is sent:

```js
const payload = {
  ...existingPayload,
  preferences: {
    ...preferences,
    religion_related_major_preference: preferences.religion_related_major_preference || 'Not relevant'
  }
};
```

Preserve current API shape for scores/interests.

- [ ] **Step 4: Render improved recommendation fields**

In `ResultCardAdvanced.jsx`, support both old and new fields:

```jsx
const score = recommendation.suitability_score ?? recommendation.score ?? 0;
const explanations = recommendation.explanation ?? [recommendation.reason].filter(Boolean);
const breakdown = recommendation.score_breakdown ?? recommendation.fit_summary ?? {};
```

Render:

```jsx
<p className="text-xs uppercase tracking-[0.18em] text-textSubtle">#{recommendation.rank}</p>
<h3 className="text-xl font-semibold text-textPrimary">{recommendation.major}</h3>
<p className="text-sm text-textSecondary">{recommendation.cluster}</p>
<div className="mt-4 h-2 rounded-full bg-borderSoft">
  <div className="h-2 rounded-full bg-accent" style={{ width: `${Math.min(100, Math.max(0, score))}%` }} />
</div>
<p className="mt-2 text-sm font-medium text-textPrimary">{score}/100 · {recommendation.match_level}</p>
<ul className="mt-4 space-y-2 text-sm text-textSecondary">
  {explanations.map((item) => <li key={item}>• {item}</li>)}
</ul>
```

For expandable breakdown, use existing expansion pattern if present. Otherwise add a native `<details>` block with subtle styling.

- [ ] **Step 5: Render response notes and fallback state**

In `ResultSectionAdvanced.jsx`, display:

```jsx
{result.fallback_used ? (
  <p className="rounded-2xl border border-amber-300/40 bg-amber-100/50 px-4 py-3 text-sm text-amber-900">
    {locale === 'id'
      ? 'Model ML sedang tidak tersedia, jadi Apti memakai rekomendasi fallback berbasis aturan.'
      : 'The ML model was unavailable, so Apti used a rule-based fallback recommendation.'}
  </p>
) : null}

{result.notes?.length ? (
  <div className="space-y-2 text-sm text-textSecondary">
    {result.notes.map((note) => <p key={note}>{note}</p>)}
  </div>
) : null}
```

- [ ] **Step 6: Run frontend tests/build**

Run:

```bash
cd frontend && npm test -- --run && npm run build
```

Expected: tests/build pass.

---

## Task 9: README update after verified implementation

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Verify implementation before docs**

Run:

```bash
cd frontend && npm test -- --run && npm run build
python -m compileall backend/app
PYTHONPATH=backend pytest backend/tests/test_predict_contract.py backend/tests/test_religion_sanity.py -q
```

Expected: all feasible checks pass. If backend pytest is unavailable, document exact command failure and still run compile.

- [ ] **Step 2: Update README sections**

Add concise sections:

```markdown
## Apti

Apti is a college major recommendation web app for Indonesian high school students. It combines academic signals, interest profiling, preferences, explainable recommendations, and optional feedback to support exploration.

## Recommendation approach

Apti returns top-N recommendations rather than one final answer. The suitability score combines model signal, academic fit, interest fit, preference fit, and optional-subject boost. Raw model probability is not shown as truth.

## Optional subject handling

Optional subjects may be missing. Missing optional subjects are treated neutrally and tracked with availability flags, not converted to zero.

## Religion-related study preference

Apti does not ask for religion identity. It asks whether the student is interested in religion-related study programs. Religion-related majors are only boosted when the student explicitly selects a related academic preference.

## Model card

- Model: Random Forest MVP
- Version: `apti_rf_v1.0`
- Feature version: `apti_features_v1.0`
- Dataset version: `apti_dataset_v1.0`
- Intended use: exploration aid for major discovery
- Not intended use: final admissions, guaranteed career prediction, or sensitive identity inference
- Limitation: synthetic data supports MVP simulation and does not prove real-world accuracy

## Dataset card

The current dataset is synthetic bootstrap data for simulation. Real questionnaire and feedback data should be evaluated separately before making real-world performance claims.
```

Keep existing setup/deployment instructions if present.

- [ ] **Step 3: Final verification commands**

Run:

```bash
git diff --stat
cd frontend && npm test -- --run && npm run build
python -m compileall backend/app
```

Expected: frontend tests/build pass; backend compile passes; diff only includes planned files.

---

## Self-review checklist

- [x] Spec coverage: stabilization, backend/ML P0, frontend integration, docs, testing all mapped to tasks.
- [x] No placeholders: plan uses concrete file paths, code blocks, commands, expected outcomes.
- [x] Type consistency: `PredictRequest`, `RecommendationItem`, `PredictResponse`, and `PredictionOutput` fields match across tasks.
- [x] User constraint honored: no git commit/push steps included.
