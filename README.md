# College Major Recommendation System

A production-oriented web platform that recommends university majors for Indonesian high school students.

The system combines academic scores, declared interests, and high-school track (`IPA`, `IPS`, or `Bahasa`) to produce ranked major recommendations, profile summaries, asynchronous explainability data, telemetry snapshots, user feedback signals, and retraining inputs.

---

## Current Phase

This project is no longer a simple prototype. It is now in an application-hardening phase with these capabilities already implemented:

- Interactive multi-step frontend journey
- Ranked recommendation output with richer visual explanation
- Asynchronous SHAP-based explainability flow
- Prediction logging and metrics logging
- User feedback capture for future retraining
- Champion-vs-challenger retraining endpoint
- Fairness gate with weighted fallback retraining
- Telemetry snapshot endpoint for drift and bias monitoring
- Vercel + Railway + Supabase deployment path

Current operational focus:

- stabilize production deployment
- ensure model artifacts and dataset files are present in deployed backend
- verify `/predict` works end-to-end in Railway
- keep README and deployment steps aligned with current architecture

---

## What Problem This Program Solves

Students often know their grades and broad interests, but not how those signals translate into specific university majors. This system turns those inputs into:

1. **Top major recommendations**
2. **A profile summary** describing the student’s strength pattern
3. **Explainability output** showing why each major was suggested
4. **Feedback records** for continuous improvement
5. **Telemetry data** for model-health tracking

This makes the application useful for both:

- **end users**, who want understandable recommendations
- **system operators**, who need observability, retraining hooks, and deployment readiness

---

## System Overview

### High-level architecture

```text
Frontend (React/Vite)
    ↓ HTTP
FastAPI Backend
    ├── Prediction service
    ├── Explainability generation
    ├── Feedback logging
    ├── Retrain orchestration
    └── Telemetry snapshot
    ↓
Supabase PostgreSQL

Local ML Assets
    ├── trained model (.pkl)
    ├── label encoder (.pkl)
    └── training dataset (.csv)
```

### Runtime split

- **Frontend**: user interaction, request orchestration, explanation polling, feedback submission
- **Backend**: validation, inference, explainability generation, database writes, retrain triggering, telemetry
- **Supabase**: majors catalog, interests catalog, prediction logs, feedback, metrics, explanations
- **ML assets**: trained random forest model, label encoder, generated dataset used by training pipeline

---

## Deep Program Analysis

## 1. Frontend Analysis

Frontend lives in `frontend/` and is built with React + Vite.

### Main responsibility

Frontend is not only a form. It acts as a lightweight workflow controller:

- collects user input
- sends prediction payload to backend
- stores prediction result in local state
- polls async explainability endpoint until ready
- captures user feedback after recommendation is shown

### Main entry flow

Primary app orchestration happens in `frontend/src/App.jsx`.

Observed responsibilities there:

- triggers backend health ping on startup
- sends `/predict` request when user completes journey
- resets and starts explainability polling for new session
- submits feedback through `/feedback`
- passes merged result + explanation state to result components

### Frontend structure

```text
frontend/
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── styles.css
│   ├── lib/
│   │   └── api.js
│   ├── hooks/
│   │   └── useExplainabilityPoll.js
│   └── components/
│       ├── features/
│       │   ├── RecommendationJourney.jsx
│       │   ├── ResultCardAdvanced.jsx
│       │   └── ResultSectionAdvanced.jsx
│       ├── RecommendationForm.jsx
│       ├── ResultCard.jsx
│       └── ResultSection.jsx
├── package.json
├── tailwind.config.js
├── vite.config.js
└── vercel.json
```

### Important frontend modules

#### `frontend/src/lib/api.js`
HTTP client layer for:

- `pingHealth()`
- `predict(payload)`
- `submitFeedback(payload)`
- `fetchExplanations(sessionId)`

Important behavior:

- reads backend base URL from `VITE_API_URL`
- times out prediction requests with `AbortController`
- throws structured errors when backend returns non-2xx response

#### `frontend/src/hooks/useExplainabilityPoll.js`
Implements async explanation polling.

Why this matters:

- prediction response is returned first
- SHAP explanation rows are generated in backend background task
- frontend repeatedly calls `/explanations/{session_id}` until rows are ready

This keeps first response fast while still exposing richer explanation data later.

#### `frontend/src/components/features/RecommendationJourney.jsx`
Multi-step UI for collecting:

- high-school track
- academic scores
- interests

This component improves completion flow compared with a single dense form.

#### `frontend/src/components/features/ResultSectionAdvanced.jsx`
Result presentation layer.

It merges:

- recommendation list from `/predict`
- explanation payload from `/explanations/{session_id}`
- feedback submission state

#### `frontend/src/components/features/ResultCardAdvanced.jsx`
Visual explanation layer.

It renders richer UI such as:

- animated score gauge
- radar chart
- expandable explanation details

### Frontend design direction

Frontend has moved toward a more product-like interface rather than a plain admin or demo screen.

Implemented direction includes:

- glassmorphism styling
- animated transitions with Framer Motion
- data visualization with Recharts
- session-based result experience

---

## 2. Backend Analysis

Backend lives in `backend/` and is built with FastAPI.

### Main responsibility

Backend is application core. It handles:

- request validation
- model loading
- feature conversion
- prediction generation
- explainability generation
- database persistence
- retraining orchestration
- telemetry snapshots

### Backend structure

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── db.py
│   └── services/
│       ├── ml_service.py
│       ├── retrain_service.py
│       └── telemetry_service.py
├── ml/
│   ├── dataset_generator.py
│   ├── train_pipeline.py
│   ├── data/
│   │   └── training_dataset.csv
│   └── models/
│       ├── rf_v1.0.pkl
│       └── label_encoder.pkl
├── sql/
│   └── schema.sql
├── requirements.txt
└── railway.toml
```

### `backend/app/main.py`
Application bootstrap.

Main roles:

- create FastAPI app
- register CORS middleware
- include API router
- load ML service at startup
- expose validation error formatting

This file controls whether deployment boots cleanly. If model paths or env vars are wrong, startup or first prediction path will fail here or in loaded services.

### `backend/app/api/routes.py`
Main API surface.

Documented route set:

- `GET /`
- `GET /health`
- `GET /majors`
- `GET /interests`
- `POST /predict`
- `GET /explanations/{session_id}`
- `POST /feedback`
- `GET /metrics`
- `POST /api/retrain`

This file is orchestration-heavy, not model-heavy.

#### Route behavior analysis

##### `GET /health`
Simple liveness endpoint. Useful for Railway health checks.

##### `GET /majors` and `GET /interests`
Reads selectable catalog data. These endpoints support form configuration and can fall back when database state is incomplete.

##### `POST /predict`
Most important runtime path.

This route:

1. accepts validated recommendation input
2. calls `ml_service.predict(...)`
3. logs prediction data
4. logs telemetry metrics
5. clears any prior explanation rows for same session
6. starts background explanation generation
7. returns ranked recommendations immediately

This endpoint is where most production failures matter, because successful boot does not guarantee successful inference.

##### `GET /explanations/{session_id}`
Reads explanation rows after background generation completes.

##### `POST /feedback`
Stores user feedback about recommendation quality.

##### `GET /metrics`
Returns telemetry snapshot, including drift and bias style monitoring values.

##### `POST /api/retrain`
Starts retraining workflow in background.

This endpoint does not simply retrain blindly. It applies evaluation logic and deployment gate logic before replacing production model.

---

## 3. ML Service Analysis

Core inference logic lives in `backend/app/services/ml_service.py`.

### Main responsibility

This service converts raw request data into model-ready features, loads model artifacts, runs inference, builds recommendation objects, and prepares explanation payloads.

### Key functions observed

- model load lifecycle
- request-to-feature-row conversion
- profile summary creation
- explanation building
- prediction generation

### Inference flow

Conceptually, prediction path works like this:

```text
PredictRequest
    ↓
Normalize scores + interests + SMA track
    ↓
Build feature row
    ↓
Load model + encoder
    ↓
Predict class probabilities / ranking
    ↓
Map encoded classes to major names
    ↓
Build profile summary
    ↓
Return top-N recommendations
```

### Explainability flow

Explainability is intentionally asynchronous.

Why:

- SHAP work is more expensive than main prediction path
- response latency stays lower if explanation generation is deferred
- frontend can poll later without blocking recommendation screen

Conceptual flow:

```text
/predict
    ↓
Immediate prediction response
    ↓
Background task starts
    ↓
SHAP or explanation values built per top major
    ↓
Rows saved in prediction_explanations
    ↓
Frontend polls /explanations/{session_id}
```

### Critical runtime dependency

`ml_service.py` depends on deployed file presence for:

- `backend/ml/models/rf_v1.0.pkl`
- `backend/ml/models/label_encoder.pkl`

If these files are missing in Railway build output, `/predict` will fail even when:

- backend boots
- CORS works
- `/health` returns 200

This is one of the most important deployment constraints in current phase.

---

## 4. Retraining Analysis

Retraining logic lives in `backend/app/services/retrain_service.py`.

### Main responsibility

This service converts accumulated feedback into candidate training signal, trains challenger models, compares them against champion model, evaluates fairness, and only promotes challenger if gate conditions pass.

### Why this matters

Many demo ML apps stop at prediction. This project goes further:

- it captures user feedback
- it makes that feedback operationally useful
- it adds evaluation and fairness protection before model replacement

### Retrain strategy

Observed strategy includes:

- feedback fetch from database
- feedback augmentation into training set
- champion-vs-challenger comparison
- macro-F1 evaluation
- fairness check using disparate impact ratio on `sma_track`
- weighted fallback retraining path

### Fairness gate

Fairness is not cosmetic here. Retraining path includes fairness-aware logic so new model is not deployed only because raw score improves.

This is important because input population varies by school track, and naive optimization could amplify bias.

---

## 5. Telemetry Analysis

Telemetry logic lives in `backend/app/services/telemetry_service.py`.

### Main responsibility

Produces monitoring-style metrics for current model version.

Observed telemetry concerns:

- drift score
- bias score
- snapshot generation

### Why telemetry exists

ML system needs more than uptime monitoring.

Standard web checks answer:

- is service alive?
- is endpoint responding?

Telemetry layer answers deeper questions:

- is incoming behavior drifting?
- is fairness degrading?
- how much prediction activity exists?
- should retrain be considered?

This moves project from static ML demo toward maintainable ML-backed service.

---

## 6. Database Analysis

Database access layer lives in `backend/app/core/db.py`.

### Main responsibility

This module isolates Supabase read/write logic for:

- major catalog
- interest catalog
- prediction logs
- metrics logs
- feedback logs
- explanation rows
- retrain input reads
- metrics snapshots

### Schema role

`backend/sql/schema.sql` creates core relational model.

Important tables:

- `sma_tracks`
- `majors`
- `interests`
- `prediction_log`
- `prediction_metrics`
- `user_feedback`
- `prediction_explanations`

### Table purpose analysis

#### `majors`
Canonical major list. Used in frontend options and prediction mapping.

#### `interests`
Interest taxonomy used by frontend and model input encoding.

#### `sma_tracks`
Represents student stream categories. Also relevant for fairness evaluation.

#### `prediction_log`
Stores recommendation request history. Useful for analytics and audit.

#### `prediction_metrics`
Stores model-health style measurements and runtime telemetry.

#### `user_feedback`
Stores explicit user assessment of recommendation quality.

#### `prediction_explanations`
Stores delayed explanation payload so frontend can fetch it later.

### Architectural note

DB layer is intentionally separated from route layer. This reduces endpoint complexity and keeps Supabase integration details in one place.

---

## 7. Training Pipeline Analysis

Training utilities live in `backend/ml/`.

### `dataset_generator.py`
Builds synthetic or rule-based training dataset.

Role:

- create training rows at controlled scale
- encode domain assumptions into sample generation
- bootstrap project when real historical data is limited

### `train_pipeline.py`
Builds training pipeline and saves artifacts.

Observed functions include:

- derived feature creation
- preprocessing builder
- model training
- model evaluation
- encoder persistence
- top-k accuracy support

### Pipeline role in overall system

```text
dataset_generator.py
    ↓
training_dataset.csv
    ↓
train_pipeline.py
    ↓
rf_v1.0.pkl + label_encoder.pkl
    ↓
ml_service.py inference runtime
```

This means production inference is tightly coupled to artifact versioning. If training output and config paths drift apart, deployment will break.

---

## 8. API Flow Analysis

## Prediction flow

```text
User fills recommendation journey
    ↓
Frontend sends POST /predict
    ↓
FastAPI validates payload
    ↓
ML service predicts top majors
    ↓
Backend logs prediction + metrics
    ↓
Backend starts explanation background task
    ↓
Frontend shows initial results
    ↓
Frontend polls GET /explanations/{session_id}
    ↓
Explanation data becomes visible later
```

## Feedback flow

```text
User reviews recommendation
    ↓
Frontend sends POST /feedback
    ↓
Backend stores user feedback
    ↓
Feedback becomes future retrain input
```

## Retrain flow

```text
Operator calls POST /api/retrain
    ↓
Backend fetches enough feedback rows
    ↓
Build challenger training set
    ↓
Train and evaluate challenger
    ↓
Check quality + fairness gate
    ↓
Promote challenger only if thresholds pass
```

## Metrics flow

```text
Prediction activity + stored metrics
    ↓
Telemetry service computes snapshot
    ↓
GET /metrics returns current view
```

---

## 9. Deployment Analysis

## Frontend deployment

Target platform: **Vercel**

Important production requirement:

- `VITE_API_URL` must point to live Railway backend URL

Root-level `vercel.json` is used for monorepo-aware build behavior.

## Backend deployment

Target platform: **Railway**

Important production requirement:

- backend root directory should be `backend`
- startup command should run Uvicorn from backend context
- model files and dataset files must exist in deployed repo or build output

`backend/railway.toml` exists to support this deployment path.

## Database deployment

Target platform: **Supabase**

Important production requirement:

- schema from `backend/sql/schema.sql` must be applied
- `SUPABASE_SERVICE_KEY` must be service-role key for server-side writes
- CORS origin list must include actual frontend deployment URL

---

## 10. Current Production Risks

These are most important risks in current phase.

### 1. Missing model artifacts in deployed backend

If `.gitignore` excludes model files, Railway will deploy app code without inference assets.

Most critical files:

- `backend/ml/models/rf_v1.0.pkl`
- `backend/ml/models/label_encoder.pkl`
- `backend/ml/data/training_dataset.csv` if deployment or retrain path depends on it

### 2. Healthy service but broken `/predict`

`/health` returning `200 OK` only proves server is alive. It does not prove model path, encoder path, or prediction pipeline works.

### 3. Env mismatch between local and production

Common breakpoints:

- wrong `VITE_API_URL`
- wrong `ALLOWED_ORIGINS`
- wrong `SUPABASE_SERVICE_KEY`
- wrong model path values

### 4. Monorepo deployment misconfiguration

Frontend and backend deploy from different subdirectories. Wrong root or wrong build command causes partial success where one side works and other side fails.

---

## Technology Stack

### Frontend

- React 18
- Vite 5
- Tailwind CSS 3
- Framer Motion
- Recharts
- lucide-react

### Backend

- FastAPI
- Pydantic v2
- Uvicorn
- Supabase Python client

### ML and data

- scikit-learn
- pandas
- numpy
- SHAP
- joblib

### Infrastructure

- Vercel
- Railway
- Supabase PostgreSQL

---

## Local Development Setup

## 1. Clone repository

```bash
git clone <repo-url>
cd rekomen-jurusan
```

## 2. Backend setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
```

Set `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
MODEL_PATH=ml/models/rf_v1.0.pkl
LABEL_ENCODER_PATH=ml/models/label_encoder.pkl
MODEL_VERSION=rf_v1.0
DRIFT_ALERT_THRESHOLD=12.0
```

## 3. Generate dataset and train model

```bash
source .venv/bin/activate
python backend/ml/dataset_generator.py --rows 1800 --output backend/ml/data/training_dataset.csv
python backend/ml/train_pipeline.py \
  --dataset backend/ml/data/training_dataset.csv \
  --model-out backend/ml/models/rf_v1.0.pkl \
  --encoder-out backend/ml/models/label_encoder.pkl
```

## 4. Apply database schema

Run this file in Supabase SQL Editor:

- `backend/sql/schema.sql`

## 5. Run backend

```bash
source .venv/bin/activate
uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

Backend URL:

- `http://localhost:8000`

## 6. Frontend setup

```bash
npm --prefix frontend install
cp frontend/.env.example frontend/.env
```

Set `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=RekomendasiJurusan
```

## 7. Run frontend

```bash
npm --prefix frontend run dev
```

Frontend URL:

- `http://localhost:5173`

---

## API Reference

Base local URL: `http://localhost:8000`

### `GET /`
Basic service root.

### `GET /health`
Health check for platform and deployment probes.

### `GET /majors`
Returns available major options.

### `GET /interests`
Returns available interest options.

### `POST /predict`
Runs inference and starts async explanation generation.

Example:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "sma_track": "IPA",
    "scores": {
      "math": 90,
      "physics": 85,
      "chemistry": 78,
      "biology": 65,
      "economics": 60,
      "indonesian": 75,
      "english": 80
    },
    "interests": ["Teknologi", "Data & AI", "Rekayasa"],
    "top_n": 5
  }'
```

### `GET /explanations/{session_id}`
Fetches async explanation rows for prior prediction session.

### `POST /feedback`
Stores user feedback for recommendation quality.

Example:

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "selected_major": "Teknik Informatika",
    "aligns_with_goals": true,
    "rating": 5,
    "notes": "Strong fit"
  }'
```

### `GET /metrics`
Returns telemetry snapshot for model version.

### `POST /api/retrain`
Triggers retraining workflow.

Example:

```bash
curl -X POST http://localhost:8000/api/retrain \
  -H "Content-Type: application/json" \
  -d '{"min_feedback_rows": 100}'
```

---

## Build and Verification

### Frontend production build

```bash
npm --prefix frontend run build
```

### Backend compile check

```bash
python -m compileall backend/app
```

### Minimum manual verification

1. open frontend
2. submit prediction request
3. confirm recommendation list renders
4. confirm `/explanations/{session_id}` eventually returns rows
5. submit feedback
6. confirm `/metrics` responds
7. confirm Railway logs show no `/predict` exception

---

## Production Checklist

## Vercel

- import repository
- verify frontend build settings
- set `VITE_API_URL`
- redeploy after backend URL changes

## Railway

- service root directory: `backend`
- install dependencies from `requirements.txt`
- start with Uvicorn
- verify model files exist in deployed source
- confirm `/health` and `/predict`

## Supabase

- apply `backend/sql/schema.sql`
- use correct `SUPABASE_URL`
- use correct service-role key
- confirm insert permissions work from backend

---

## Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   └── db.py
│   │   ├── services/
│   │   │   ├── ml_service.py
│   │   │   ├── retrain_service.py
│   │   │   └── telemetry_service.py
│   │   ├── config.py
│   │   ├── main.py
│   │   └── schemas.py
│   ├── ml/
│   │   ├── dataset_generator.py
│   │   ├── train_pipeline.py
│   │   ├── data/
│   │   │   └── training_dataset.csv
│   │   └── models/
│   │       ├── rf_v1.0.pkl
│   │       └── label_encoder.pkl
│   ├── sql/
│   │   └── schema.sql
│   ├── railway.toml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── App.jsx
│   │   └── styles.css
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── vercel.json
├── vercel.json
└── README.md
```

---

## Final Notes

- Main business-critical endpoint is `/predict`.
- Main product differentiator is async explainability plus retrain-aware architecture.
- Main deployment hazard is missing ML artifact files in production.
- Main maturity signal is separation of inference, telemetry, feedback, and retrain flows.

If you are debugging production and `GET /health` works but `POST /predict` returns 500, inspect deployed model file presence first, then inspect Railway traceback for exact failing line.
