# Apti — College Major Recommendation Web App

Apti helps Indonesian high school students explore college majors using curriculum-aware academic signals, interest profiling, learning preferences, explainable recommendations, and optional feedback.

## Features

- Dynamic intake flow for `IPA`, `IPS`, `Bahasa`, and `Kurikulum Merdeka`
- Bilingual UI with English / Bahasa Indonesia toggle and local persistence
- Light and dark themes with shared premium UI system
- Global grid background and polished CTA styling
- Ranked recommendation cards with profile summary, tradeoffs, career paths, and alternative majors
- Async explainability polling for recommendation reasoning
- Optional feedback capture for future model improvement
- FastAPI backend with telemetry, metrics, and retraining hooks
- Supabase-backed logging for predictions, explanations, metrics, and feedback

## Tech Stack

### Frontend
- React
- Vite
- Tailwind CSS
- Framer Motion
- Recharts
- Vitest + Testing Library

### Backend
- FastAPI
- Pydantic v2
- Supabase Python client
- scikit-learn model artifacts
- SHAP explainability support

## Project Structure

```text
frontend/
  src/
    App.jsx
    styles.css
    components/features/
    hooks/
    lib/
backend/
  app/
    api/
    core/
    services/
  ml/
  sql/
```

## Local Setup

### 1. Frontend

```bash
cd frontend
npm install
npm run dev
```

Default dev URL:

```text
http://localhost:5173
```

### 2. Backend

Create backend env file if needed:

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

Backend import sanity:

```bash
python -m compileall backend/app
```

## API Overview

Main endpoints:

- `GET /health`
- `GET /majors`
- `GET /interests`
- `POST /predict`
- `GET /explanations/{session_id}`
- `POST /feedback`
- `GET /metrics`
- `POST /api/retrain`

## Deployment

### Vercel
- Project: `apti`
- Domain in use: `apti-mepi.vercel.app`
- Root directory: `frontend`

### Railway
- Project: `major-recommendation`
- Service: `rekomendasi-jurusan`
- Backend workspace path: `backend`

### Supabase
Expected core tables:

- `majors`
- `interests`
- `prediction_log`
- `prediction_metrics`
- `prediction_explanations`
- `user_feedback`

## Current Validation Status

Verified in current local state:

- Frontend build passes
- Focused frontend tests pass
- Backend Python modules compile
- Supabase core tables exist
- Vercel project and production deployment exist
- Railway CLI is installed and authenticated

## Known Follow-up

- Railway service variables still need service-level inspection after linking service context
- Vite shows deprecation warnings from React plugin config path, but build still succeeds
- Frontend production bundle is large and may benefit from code-splitting
