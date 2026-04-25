# Apti — College Major Recommendation Web App

Apti is a decision-support web app for Indonesian high school students exploring college majors. It combines curriculum-aware academic signals, interest profiling, learning preferences, explainable scoring, and optional user feedback.

Apti is not an admissions guarantee, aptitude diagnosis, or proof that a major is objectively best. Its recommendations should be treated as structured guidance for reflection, counseling, and further research.

## Features

- 10-step intake for `IPA`, `IPS`, `Bahasa`, and `Kurikulum Merdeka`
- Optional subject handling for curriculum-specific and user-selected subjects
- Prodi-specific recommendations from 59 official groups and 489 mapped Indonesian prodi
- Interest, academic context, career direction, constraints, and learning-preference profiling
- Religion-related preference handling through explicit user preference fields, not inferred identity
- Ranked recommendation cards with prodi ID, kelompok prodi, rumpun ilmu, match scores, tradeoffs, career paths, skill gaps, and alternatives
- Explanation engine with async polling for recommendation reasoning
- Optional bounded Gemini/OpenAI review that cannot add catalog items or override safety rules
- Bilingual English / Bahasa Indonesia UI with persisted preference
- Optional feedback capture for future evaluation and model improvement
- FastAPI backend with catalog services, metrics, telemetry, explanation, and retraining hooks

## Architecture

```text
frontend/
  React + Vite UI
  Intake flow, recommendation journey, charts, feedback, localization

backend/
  FastAPI API
  Prediction, explanation, metrics, feedback, and retraining services

backend/ml/
  Raw data ingestion, cleaned prodi catalog, profile matrix, synthetic dataset generation,
  model artifacts, training scripts, evaluation reports, fairness checks, promotion gate

backend/sql/
  Supabase schema support for majors, interests, logs, metrics, explanations, feedback
```

## ML Approach

Apti uses a two-stage recommendation approach. Stage 1 predicts an official `kelompok_prodi`; Stage 2 ranks specific prodi with a hybrid score over model/group signal, academic fit, supporting subject fit, interest depth, preferences, career direction, constraints, and optional subject evidence.

The model is designed for explainable decision support:

- Academic scores contribute curriculum-specific evidence
- Supporting subjects come from cleaned Indonesian prodi catalog data
- Interest selections and free-text context contribute preference evidence
- Learning style, constraints, and career direction add contextual signals
- Optional subjects are included only when supplied or relevant
- Recommendation scores are surfaced with explanations, caveats, and skill gaps

## Dataset Strategy

Catalog source data contains 59 official prodi groups and 489 specific prodi mappings. Cleaned catalog files are generated under `backend/ml/data/catalog/`; profile weights are generated under `backend/ml/config/prodi_profiles.json`.

Training and evaluation data are synthetic / curated project data generated from the catalog and profile matrix, not verified real-world longitudinal outcomes. This is useful for product development, integration testing, and demonstrating the recommendation pipeline, but it does not prove real-world predictive validity.

Current v2 commands:

```bash
python backend/ml/data_generation/generate_synthetic_dataset.py --n 5000 --version apti_dataset_v2
python backend/ml/training/train_model.py --dataset backend/ml/data/processed/apti_training_v2.csv --model-version apti_v2
python backend/ml/training/evaluate_model.py --dataset backend/ml/data/processed/apti_training_v2.csv --model-version apti_v2
python backend/ml/training/promote_model.py
```

Future dataset work should prioritize:

- Real anonymized counseling or enrollment data, with consent
- Balanced representation across curricula, regions, and school types
- Bias checks for gender, socioeconomic, regional, and religious preference effects
- Outcome tracking beyond initial recommendation acceptance
- Clear data governance and deletion policies

## Optional Subject Handling

Apti supports curriculum differences by making some subjects optional. Optional subject values are used when present and ignored or defaulted when not applicable. This avoids forcing students to provide irrelevant scores while still allowing richer recommendations for students with extra subject data.

## Religion-Related Preference Handling

Apti may include religion-related academic or preference fields when users explicitly provide them. These fields should only support stated educational preferences. Apti should not infer religious identity, restrict opportunities, or treat religion-related data as a protected-attribute proxy for eligibility.

## Scoring System

Recommendations are ranked by model output and supporting rule/config signals. Scores represent relative fit within Apti's current feature space, not certainty or admission probability.

Each recommendation may include:

- Match score
- Prodi ID, specific prodi name, kelompok prodi, and rumpun ilmu
- Academic, supporting-subject, interest, preference, career, and optional-subject alignment
- Tradeoffs or weaker-fit signals
- Career pathways and skill gaps
- Alternative majors/prodi
- Explanation status and optional LLM review notes

## Explanation and LLM Review

The backend records prediction sessions and exposes explanation retrieval. The frontend polls for explanations after recommendations are returned. Explanations are intended to make recommendation factors more transparent and help users compare options.

Optional LLM review supports `LLM_PROVIDER=gemini` or `LLM_PROVIDER=openai`; default is `none`. LLM output is JSON-only, time-bounded, catalog-bounded, and score adjustments are clamped to ±5. The LLM may add review notes, but cannot add prodi outside returned recommendations or override hard safety rules.

Explanations are approximate model-support narratives. They should not be interpreted as causal proof.

## API Overview

Main endpoints:

- `GET /health` — backend health check
- `GET /majors` — supported majors
- `GET /interests` — supported interests
- `POST /predict` — recommendation request
- `GET /explanations/{session_id}` — async explanation lookup
- `POST /feedback` — user feedback capture
- `GET /metrics` — prediction metrics
- `POST /api/retrain` — retraining hook

## Local Setup

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Default dev URL:

```text
http://localhost:5173
```

### Backend

```bash
cd backend
cp .env.example .env
```

Required variables:

```env
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
ALLOWED_ORIGINS=http://localhost:5173
MODEL_PATH=ml/models/rf_v1.0.pkl
LABEL_ENCODER_PATH=ml/models/label_encoder.pkl
MODEL_VERSION=rf_v1.0
LLM_PROVIDER=none
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
LLM_TIMEOUT_SECONDS=4.0
```

Run backend:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

Frontend build:

```bash
cd frontend
npm run build
```

Frontend tests:

```bash
cd frontend
npm test
```

Backend tests:

```bash
cd backend
pytest
```

Recent prior verification context:

- Backend tests: 26 passed
- Frontend build: passed
- Frontend tests: passed only when excluding `.claude/worktrees`; temporary agent test files pollute default discovery

No deployment success is claimed by this README.

## Model Card

- **Model purpose:** Recommend Indonesian college prodi for student exploration and counseling support
- **Model type:** scikit-learn supervised kelompok classifier plus hybrid prodi scorer
- **Inputs:** Curriculum, academic scores, optional subjects, interests, academic context, subject preferences, career direction, constraints, explicit user preferences
- **Outputs:** Ranked prodi recommendations, scores, metadata, skill gaps, and explanation references
- **Intended users:** Students, counselors, educators, product evaluators
- **Not intended for:** Admissions decisions, automated eligibility screening, high-stakes placement, or psychological diagnosis
- **Known risks:** Synthetic-data bias, limited external validation, over-trust in scores, under-representation of real student pathways
- **Human oversight:** Required for meaningful decisions

## Dataset Card

- **Catalog status:** 59 official groups and 489 specific prodi mappings from provided CSV/JSON files
- **Training status:** Synthetic / curated project data generated from catalog/profile matrix
- **Primary use:** Development, testing, demonstration, and model pipeline validation
- **Real-world validity:** Not proven
- **Sensitive considerations:** Religion-related preferences must be explicit, optional, and handled carefully
- **Recommended improvements:** Real consented data, demographic fairness checks, regional coverage, outcome tracking, and documentation of data provenance

## Limitations

- Synthetic data cannot establish real-world recommendation quality
- Scores are relative fit signals, not probabilities of success
- Explanations are approximations of model factors
- Recommendations may reflect gaps or bias in training data and feature design
- Optional subject defaults can affect comparability across curricula
- Religion-related fields require careful consent, minimization, and fairness review

## Roadmap

- Validate with real anonymized data and counselor review
- Add stronger fairness and robustness evaluation
- Improve test isolation so temporary worktrees do not affect frontend discovery
- Expand model monitoring and feedback analysis
- Add clearer user-facing consent and data-use messaging
- Consider frontend code-splitting if bundle size grows
