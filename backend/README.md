# Purpose: Document Apti backend API, prodi catalog, ML pipeline, and local verification.
# Callers: Developers maintaining FastAPI, ML artifacts, and dataset jobs.
# Deps: FastAPI, scikit-learn, pandas, joblib, optional Supabase/LLM APIs.
# API: Local commands for ingestion, training, evaluation, testing, and serving.
# Side effects: None.

# Apti Backend

FastAPI backend for Apti recommendation flow. It validates student input, loads the cleaned Indonesian prodi catalog, scores specific prodi, optionally reviews results with an LLM, logs feedback/telemetry, and exposes retraining hooks.

## Data pipeline

Source files live at repository root:

- `kelompok_resmi_59_mapel_pendukung.csv`
- `prodi_spesifik_mapping_mapel_pendukung.csv`
- `dataset_prodi_mapel_pendukung.json`

Clean outputs:

- `ml/data/catalog/kelompok_resmi_59_clean.json`
- `ml/data/catalog/prodi_spesifik_clean.json`
- `ml/data/catalog/prodi_aliases.json`
- `ml/data/catalog/subject_normalization_map.json`
- `ml/config/prodi_profiles.json`

Commands:

```bash
python ml/data_ingestion/load_prodi_data.py
python ml/data_ingestion/validate_prodi_data.py
python ml/data_ingestion/build_catalog.py
python ml/data_ingestion/build_profiles.py
```

## ML pipeline v2

Synthetic generator creates form-like rows from the catalog/profile matrix, then training compares baseline and scikit-learn classifiers.

```bash
python ml/data_generation/generate_synthetic_dataset.py --n 5000 --version apti_dataset_v2
python ml/training/train_model.py --dataset ml/data/processed/apti_training_v2.csv --model-version apti_v2
python ml/training/evaluate_model.py --dataset ml/data/processed/apti_training_v2.csv --model-version apti_v2
python ml/training/promote_model.py
```

Generated artifacts:

- `ml/models/apti_group_model_v2.pkl`
- `ml/models/apti_preprocessor_v2.pkl`
- `ml/models/apti_label_encoder_group_v2.pkl`
- `ml/models/apti_model_metadata_v2.json`
- `ml/experiments/apti_eval_report_v2.json`
- `ml/experiments/apti_fairness_report_v2.json`

Promotion requires top-3 kelompok accuracy, macro-F1, and fairness checks to pass configured thresholds.

## Recommendation flow

`POST /predict` supports legacy fields plus v2 prodi context:

- `academic_context`
- `subject_preferences`
- `interest_deep_dive`
- `career_direction`
- `constraints`
- `expected_prodi`
- `prodi_to_avoid`
- `free_text_goal`
- `language`

Output includes prodi metadata when available: `prodi_id`, `nama_prodi`, `kelompok_prodi`, `rumpun_ilmu`, supporting subjects, specific reasons, skill gaps, and optional `llm_review`.

## Optional LLM review

Default is local-only.

```env
LLM_PROVIDER=none
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
LLM_TIMEOUT_SECONDS=4.0
```

LLM review is bounded: no new prodi outside returned catalog items, no protected-identity inference, and score adjustments are clamped to ±5.

## Serve

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Verify

```bash
python -m compileall app ml/data_ingestion ml/data_generation ml/training
pytest tests
```

Current verified backend suite: `26 passed, 2 warnings`.
