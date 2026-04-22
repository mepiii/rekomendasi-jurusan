# Purpose: Centralized environment-backed backend configuration.
# Callers: API startup, db client setup, model service loader.
# Deps: os, pathlib, dotenv.
# API: settings object exposing runtime config fields.
# Side effects: Loads .env from backend root if present.

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    allowed_origins_raw: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
    model_path: str = os.getenv("MODEL_PATH", "ml/models/rf_v1.0.pkl")
    label_encoder_path: str = os.getenv("LABEL_ENCODER_PATH", "ml/models/label_encoder.pkl")
    model_version: str = os.getenv("MODEL_VERSION", "rf_v1.0")
    drift_alert_threshold: float = float(os.getenv("DRIFT_ALERT_THRESHOLD", "12.0"))

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]

    @property
    def model_abs_path(self) -> Path:
        return (ROOT_DIR / self.model_path).resolve()

    @property
    def label_encoder_abs_path(self) -> Path:
        return (ROOT_DIR / self.label_encoder_path).resolve()


settings = Settings()
