# Apti phased P0 design

## Status

Approved direction: stabilize current frontend diff first, then backend/ML P0 contract, then frontend integration. No git commit or push during this session unless user explicitly asks later.

## Assumptions

- Apti is an existing project; no rewrite from scratch.
- Supabase table names stay unchanged.
- Existing endpoints stay compatible unless additive API versioning is harmless.
- Current uncommitted frontend work must be preserved and verified before broader changes.
- Synthetic data supports MVP simulation only; documentation must not present it as real-world validation.

## Phase 1: stabilize current frontend diff

### Scope

Verify and fix only the current frontend changes:

- `frontend/src/App.jsx`
- `frontend/src/components/features/AptiIntroFlow.jsx`
- `frontend/src/components/features/RecommendationJourney.jsx`
- `frontend/src/lib/recommendationConfig.js`
- `frontend/src/styles.css`

### Behavior to verify

- Intro flow receives `locale` and renders English/Bahasa copy correctly.
- Interest chips store stable English values but render localized labels.
- Preference chips store stable English values but render localized labels.
- Prakarya appears as an optional subject where configured.
- Light-mode hover text remains readable.

### Validation

Run from `frontend/`:

```bash
npm test -- --run
npm run build
```

Fix only failures caused by current diff. If failures are unrelated or environment-based, document exact failure and stop before broad changes.

## Phase 2: backend and ML P0 contract

### Goals

Make `/predict` robust, explainable, fairer, and stable before frontend depends on richer response data.

### API schema

Update prediction input to support:

- SMA tracks: `IPA`, `IPS`, `Bahasa`, `Kurikulum Merdeka`.
- Scores from 0–100 when present.
- Nullable optional subjects.
- Multi-label interests.
- Partial preferences.
- `religion_related_major_preference` as academic interest preference, not identity.
- `top_n` default 5, clamped to 3–5.
- `language` for explanation copy if already supported.

Unknown interests should not crash prediction. Unsupported SMA track should return a clear validation error.

### Feature engineering

Add sklearn-compatible transformations that preserve training/prediction consistency:

- Academic averages: core, science, social, language, creative, optional available.
- Derived strengths: technical, verbal, people-oriented, creative, business, health, research.
- Optional availability flags: regional language, art, PKWU/Prakarya, PE, religion/ethics, informatics.
- Interest multi-hot and cluster counts.
- Preference encodings.
- Input quality indicators: completeness, optional completeness, ambiguity, cross-track interest, low completeness.

Missing optional subjects use neutral handling and availability flags. Missing optional subjects must not become zero.

### Model and artifacts

Use current Random Forest MVP path unless evidence shows artifact mismatch. Add explicit versions:

- `MODEL_VERSION=apti_rf_v1.0`
- `FEATURE_VERSION=apti_features_v1.0`
- `DATASET_VERSION=apti_dataset_v1.0`

Backend should load model artifacts once at startup/service initialization when possible. If artifacts are missing or incompatible, use fallback mode instead of crashing.

### Scoring

Return `suitability_score` from 0–100, not raw model probability.

Formula:

```text
suitability_score =
  0.45 * model_score +
  0.25 * academic_fit_score +
  0.15 * interest_fit_score +
  0.10 * preference_fit_score +
  0.05 * optional_subject_boost
```

All components normalize to 0–100. Optional boost is neutral when optional data is absent.

Match levels:

- 85–100: Strong match
- 70–84: Good match
- 55–69: Moderate match
- below 55: Exploratory match

### Sanity layer

Apply soft reranking after model output:

- Religion-related majors are not boosted unless explicit religion-related preference supports them.
- If preference is `Not relevant`, religion-related majors should not rank highly by default.
- Medicine should not dominate without health/science support.
- Bahasa profiles should not be limited to teaching majors.
- Mixed profiles should get diverse related clusters.
- Popular-major dominance should be downweighted when fit is weak.
- Strong cross-track interests should be allowed.

### Explanation engine

Each recommendation should include:

- Academic reason.
- Interest reason.
- Preference reason.
- Optional subject reason when relevant.
- Tradeoff/challenge.
- Caution when score gaps are close or input is incomplete.

Explanations must avoid destiny/certainty language and sensitive identity inference. Religion-related explanations must reference selected academic preference, not assumed religion identity.

### Response contract

`/predict` should return:

- `app: "apti"`
- `model_version`
- `feature_version`
- `session_id`
- `recommendations[]` with rank, major, cluster, suitability score, match level, score breakdown, explanations, tradeoffs, career paths, alternatives, caution.
- `profile_summary`
- `notes`
- `fallback_used`
- `latency_ms`

### Supabase logging

Keep table names unchanged. Logging should include summary data, versions, recommended majors, score breakdown, latency, fallback status, and explanation status. Logging failures must not fail prediction. Do not expose secrets. Do not store religion identity.

### Health endpoint

Improve `/health` to include app name, status, model-loaded flag, model version, feature version, Supabase configured flag, and timestamp. Do not expose secrets.

## Phase 3: frontend integration

### Goals

Adapt UI after backend response contract is stable.

### Form changes

- Keep step-based intake.
- Keep chips/cards over cluttered dropdowns.
- Add richer multi-label interests when backend supports them.
- Add advanced preferences section.
- Place religion-related major preference only in advanced preferences.
- Copy: “Are you interested in religion-related study programs?”
- Never ask “What is your religion?”

### Result changes

Recommendation cards should show:

- Rank.
- Major.
- Suitability score.
- Match level.
- Explanation bullets.
- Tradeoffs.
- Career paths.
- Alternative majors.
- Expandable score breakdown.
- Uncertainty/completeness note when returned.

Visual direction remains calm, premium, neutral, and subtle. Top recommendation gets slight emphasis only.

### Validation

Run frontend tests/build after integration. Manually inspect light/dark and mobile if dev server/browser validation is available.

## Phase 4: docs after implementation

Update README only after implemented behavior exists. Include:

- Apti overview.
- Architecture.
- ML approach.
- Dataset strategy.
- Optional subject handling.
- Religion-related preference handling.
- Scoring system.
- Explanation engine.
- API overview.
- Model card.
- Dataset card.
- Limitations.
- Roadmap.

Documentation must state that synthetic data is MVP simulation, not real-world proof.

## Testing plan

Backend:

```bash
python -m compileall backend/app
```

If backend tests exist, run them. Start FastAPI locally if feasible and test `/health` plus `/predict` profiles:

1. Full IPA profile.
2. IPS profile.
3. Bahasa profile.
4. Kurikulum Merdeka profile.
5. Missing optional subjects.
6. Religion preference Not relevant.
7. Religion-related preference selected.
8. Ambiguous profile.
9. Strong creative profile.
10. Strong language profile.
11. Weak academic but strong interest profile.
12. High scores but mixed interests.

Frontend:

```bash
cd frontend && npm test -- --run && npm run build
```

## Non-goals for P0

- No deep learning.
- No Supabase table renames.
- No login/account system.
- No university recommendation as core product.
- No heavy experiment-tracking platform.
- No deployment claim unless verified separately.
- No git commit or push unless user explicitly asks later.
