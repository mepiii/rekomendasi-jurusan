# Purpose: Centralized environment-backed backend configuration.
# Callers: API startup, db client setup, model service loader.
# Deps: os, pathlib, dotenv.
# API: settings object exposing runtime config fields.
# Side effects: Loads .env from backend root if present.

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from app.recommendation_config import MODEL_VERSION as CANONICAL_MODEL_VERSION

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_: object, **__: object) -> bool:
        return False

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    allowed_origins_raw: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
    model_path: str = os.getenv("MODEL_PATH", "ml/models/apti_group_model_v2.pkl")
    label_encoder_path: str = os.getenv("LABEL_ENCODER_PATH", "ml/models/apti_label_encoder_group_v2.pkl")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    llm_provider: str = os.getenv("LLM_PROVIDER", "none").lower()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "4.0"))
    model_version: str = CANONICAL_MODEL_VERSION
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
