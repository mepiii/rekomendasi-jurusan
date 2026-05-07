# Apti

Apti is a bilingual decision-support app for Indonesian high school students exploring college majors. It combines curriculum-aware academic signals, structured interest profiling, prodi catalog metadata, explainable scoring, and optional recommendation review.

Apti does not predict admissions outcomes or diagnose aptitude. Recommendations are guidance for reflection, counseling, and further research.

## Quick Navigation

- [Highlights](#highlights)
- [How Apti Works](#how-apti-works)
- [Architecture](#architecture)
- [Dataset and ML](#dataset-and-ml)
- [API](#api)
- [Run Locally](#run-locally)
- [Testing](#testing)
- [Model Card](#model-card)
- [Dataset Card](#dataset-card)
- [Limitations](#limitations)
- [Roadmap](#roadmap)

## Highlights

- Option-based intake for `IPA`, `IPS`, `Bahasa`, and `Kurikulum Merdeka`
- Optional target-prodi flow for students with or without specific major goals
- Prodi-specific catalog backed by 59 official groups and 489 mapped Indonesian prodi
- Structured signals for grades, interests, academic preferences, activities, career goals, constraints, and avoided prodi
- Explainable recommendation cards with match scores, tradeoffs, skill gaps, alternatives, and metadata
- Bilingual English / Bahasa Indonesia UI with persisted locale preference
- FastAPI backend with prediction, explanation, metrics, feedback, and retraining hooks
- Optional bounded LLM review that cannot invent catalog items or override safety rules

## How Apti Works

```text
Student profile
  ↓
Curriculum + report scores
  ↓
Structured survey signals
  ↓
Kelompok prediction + hybrid prodi scorer
  ↓
Ranked recommendations + explanations
```

Apti uses academic evidence and preference signals together. Grades matter, but they do not dominate the ranking. Interest depth, subject fit, career direction, constraints, target-prodi intent, and avoided-prodi penalties all contribute to final recommendations.

## Architecture

```text
frontend/
  React + Vite
  Intake wizard, recommendation UI, charts, localization, tests

backend/
  FastAPI
  Prediction API, schemas, services, metrics, feedback, explanations

backend/ml/
  Catalog ingestion, profile matrix, synthetic dataset generation,
  training, evaluation, promotion checks, model artifacts

backend/sql/
  Supabase schema support for majors, interests, logs, metrics,
  explanations, and feedback
```

## Dataset and ML

Apti uses a two-stage recommendation approach:

1. Predict official `kelompok_prodi` from student profile signals.
2. Rank specific prodi with hybrid scoring across model output, academic fit, supporting subjects, interest tags, preferences, career goals, constraints, and optional subjects.

Catalog source data:

- 59 official prodi groups
- 489 specific prodi mappings
- Cleaned catalog output under `backend/ml/data/catalog/`
- Profile weights under `backend/ml/config/prodi_profiles.json`

Current v2 pipeline:

```bash
python backend/ml/data_generation/generate_synthetic_dataset.py --n 5000 --version apti_dataset_v2
python backend/ml/training/train_model.py --dataset backend/ml/data/processed/apti_training_v2.csv --model-version apti_v2
python backend/ml/training/evaluate_model.py --dataset backend/ml/data/processed/apti_training_v2.csv --model-version apti_v2
python backend/ml/training/promote_model.py
```

Training and evaluation data are synthetic / curated project data generated from catalog and profile rules. They support product development and integration testing, but do not prove real-world predictive validity.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Backend health check |
| `GET` | `/majors` | Supported majors |
| `GET` | `/interests` | Supported interests |
| `POST` | `/predict` | Recommendation request |
| `GET` | `/explanations/{session_id}` | Async explanation lookup |
| `POST` | `/feedback` | User feedback capture |
| `GET` | `/metrics` | Prediction metrics |
| `POST` | `/api/retrain` | Retraining hook |

## Run Locally

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Default URL:

```text
http://localhost:5173
```

### Backend

```bash
cd backend
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Required environment variables:

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

## Testing

```bash
cd frontend
npm test
npm run build
```

```bash
cd backend
pytest
```

Recent verification context:

- Backend tests: 26 passed
- Frontend build: passed
- Frontend tests: passed when temporary worktree test files are excluded from discovery

No deployment success is claimed here.

## Model Card

| Field | Description |
|---|---|
| Purpose | Recommend Indonesian college prodi for exploration and counseling support |
| Type | scikit-learn kelompok classifier plus hybrid prodi scorer |
| Inputs | Curriculum, scores, optional subjects, interests, academic context, preferences, career direction, constraints |
| Outputs | Ranked prodi, scores, metadata, skill gaps, explanation references |
| Intended users | Students, counselors, educators, product evaluators |
| Not intended for | Admissions decisions, eligibility screening, high-stakes placement, psychological diagnosis |
| Known risks | Synthetic-data bias, limited validation, score over-trust, under-represented pathways |
| Oversight | Human review required for meaningful decisions |

## Dataset Card

| Field | Description |
|---|---|
| Catalog | 59 official groups and 489 prodi mappings |
| Training data | Synthetic / curated project data |
| Primary use | Development, testing, demo, model-pipeline validation |
| Real-world validity | Not proven |
| Sensitive considerations | Religion-related preferences must be explicit, optional, minimized, and handled carefully |
| Recommended improvements | Consented real data, fairness checks, regional coverage, outcome tracking, provenance docs |

## Safety Notes

- Scores are relative fit signals, not admission probabilities.
- Explanations are approximations of model factors, not causal proof.
- Optional subjects are used only when supplied or relevant.
- Religion-related preferences must never be inferred from identity.
- LLM review is JSON-only, time-bounded, catalog-bounded, and score adjustments are clamped.

## Limitations

- Synthetic data cannot establish real-world recommendation quality.
- Recommendations may reflect gaps or bias in training data and feature design.
- Optional subject defaults can affect cross-curriculum comparability.
- Explanation quality depends on available profile and scoring signals.
- Human review remains necessary for important education decisions.

## Roadmap

- Validate with anonymized real data and counselor review
- Expand fairness and robustness evaluation
- Improve frontend test isolation around temporary worktrees
- Strengthen model monitoring and feedback analysis
- Add clearer user-facing consent and data-use messaging
- Expand interactive result comparison and chart explanations
