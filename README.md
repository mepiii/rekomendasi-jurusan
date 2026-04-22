# Sistem Rekomendasi Jurusan Kuliah

Platform rekomendasi jurusan kuliah untuk siswa SMA Indonesia.
Input nilai + minat + jurusan SMA. Output top rekomendasi, profile summary, telemetry, feedback, dan explainability SHAP async.

## Fitur sekarang

- Multi-step journey UI (React + Framer Motion)
- Visual hasil: animated gauge + radar chart (Recharts)
- Explainability async per jurusan (`/explanations/{session_id}`)
- Feedback loop user (`/feedback`)
- Retrain trigger endpoint (`/api/retrain`) dengan champion-vs-challenger
- Fairness gate (disparate impact) + weighted fallback retrain
- Telemetry endpoint (`/metrics`) dan logging prediction non-blocking

## Tech stack

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

### ML
- scikit-learn pipeline
- pandas, numpy, joblib
- SHAP

### Data store
- Supabase PostgreSQL

---

## Cara start project (local)

### 1) Clone repo

```bash
git clone <repo-url>
cd rekomen-jurusan
```

### 2) Setup backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
```

Isi `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
ALLOWED_ORIGINS=http://localhost:5173,https://your-app.vercel.app
MODEL_PATH=ml/models/rf_v1.0.pkl
LABEL_ENCODER_PATH=ml/models/label_encoder.pkl
MODEL_VERSION=rf_v1.0
DRIFT_ALERT_THRESHOLD=12.0
```

### 3) Generate dataset + train model

```bash
source .venv/bin/activate
python backend/ml/dataset_generator.py --rows 1800 --output backend/ml/data/training_dataset.csv
python backend/ml/train_pipeline.py \
  --dataset backend/ml/data/training_dataset.csv \
  --model-out backend/ml/models/rf_v1.0.pkl \
  --encoder-out backend/ml/models/label_encoder.pkl
```

### 4) Setup database Supabase

Jalankan SQL berikut di Supabase SQL Editor:

- `backend/sql/schema.sql`

File ini membuat tabel:
- `majors`, `interests`, `sma_tracks`
- `prediction_log`
- `prediction_metrics`
- `user_feedback`
- `prediction_explanations`

### 5) Run backend

```bash
source .venv/bin/activate
uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

Backend local URL:

- `http://localhost:8000`

### 6) Setup frontend

```bash
npm --prefix frontend install
cp frontend/.env.example frontend/.env
```

Isi `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=RekomendasiJurusan
```

### 7) Run frontend

```bash
npm --prefix frontend run dev
```

Frontend local URL:

- `http://localhost:5173`

---

## API ringkas

Base URL local: `http://localhost:8000`

- `GET /`
- `GET /health`
- `GET /majors`
- `GET /interests`
- `POST /predict`
- `GET /explanations/{session_id}`
- `POST /feedback`
- `GET /metrics`
- `POST /api/retrain`

### Contoh request `/predict`

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

### Contoh request `/feedback`

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "selected_major": "Teknik Informatika",
    "aligns_with_goals": true,
    "rating": 5,
    "notes": "Cukup sesuai"
  }'
```

### Contoh trigger retrain

```bash
curl -X POST http://localhost:8000/api/retrain \
  -H "Content-Type: application/json" \
  -d '{"min_feedback_rows": 100}'
```

---

## Build & check

### Frontend build

```bash
npm --prefix frontend run build
```

### Backend compile check

```bash
python -m compileall backend/app
```

---

## Struktur project (current)

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
│   │   └── models/
│   ├── sql/
│   │   └── schema.sql
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/features/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── App.jsx
│   │   └── styles.css
│   └── package.json
└── README.md
```

---

## Notes

- `/predict` simpan logging + metrics via `BackgroundTasks`.
- SHAP explanation tidak blocking response utama. Frontend poll endpoint explanations sampai ready.
- Retrain endpoint start proses background. Model deploy hanya jika gate metric + fairness lolos.
- Jika Supabase env kosong, endpoint tetap jalan dengan fallback data untuk majors/interests, tapi logging DB non-aktif.
