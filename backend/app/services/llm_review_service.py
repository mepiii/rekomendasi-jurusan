# Purpose: Optionally review Apti recommendations with a bounded LLM JSON advisor.
# Callers: Prediction route after deterministic recommendation generation.
# Deps: json, urllib, app.config, app.schemas.
# API: llm_review_service.review(req, recommendations).
# Side effects: Calls configured external LLM API only when provider and key are set.

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.config import settings
from app.schemas import PredictRequest, RecommendationItem

MAX_ADJUSTMENT = 5
SYSTEM_PROMPT = """
Anda adalah reviewer rekomendasi akademik Apti. Tugas Anda hanya meninjau rekomendasi prodi dari katalog yang sudah diberikan.
Jangan menambah prodi baru, jangan mengubah aturan etika, jangan menebak agama/identitas/status ekonomi/kesehatan, dan jangan menyatakan kepastian.
Kembalikan JSON valid: {"items":[{"prodi_id":"...","score_adjustment":0,"review_note":"..."}],"summary":"..."}.
score_adjustment wajib bilangan bulat antara -5 dan 5. review_note maksimal 160 karakter, berbasis data input.
""".strip()


@dataclass(frozen=True)
class LLMReviewResult:
    provider: str
    used: bool
    items: dict[str, dict[str, Any]]
    summary: str | None = None


class LLMReviewService:
    def provider(self) -> str:
        return settings.llm_provider if settings.llm_provider in {"gemini", "openai"} else "none"

    def enabled(self) -> bool:
        provider = self.provider()
        if provider == "gemini":
            return bool(settings.gemini_api_key)
        if provider == "openai":
            return bool(settings.openai_api_key)
        return False

    def review(self, req: PredictRequest, recommendations: list[RecommendationItem]) -> LLMReviewResult:
        provider = self.provider()
        if not self.enabled() or not recommendations:
            return LLMReviewResult(provider=provider, used=False, items={})
        payload = self._payload(req, recommendations)
        try:
            raw = self._call_gemini(payload) if provider == "gemini" else self._call_openai(payload)
            parsed = self._parse(raw, {item.prodi_id for item in recommendations if item.prodi_id})
        except Exception:
            return LLMReviewResult(provider=provider, used=False, items={})
        return LLMReviewResult(provider=provider, used=bool(parsed["items"]), items=parsed["items"], summary=parsed.get("summary"))

    def apply(self, recommendations: list[RecommendationItem], result: LLMReviewResult) -> list[RecommendationItem]:
        if not result.used:
            return recommendations
        adjusted: list[RecommendationItem] = []
        for item in recommendations:
            review = result.items.get(item.prodi_id or "")
            if not review:
                adjusted.append(item)
                continue
            score = max(0, min(100, item.suitability_score + int(review["score_adjustment"])))
            adjusted.append(item.model_copy(update={"suitability_score": score, "llm_review": review}))
        ranked = sorted(adjusted, key=lambda item: item.suitability_score, reverse=True)
        return [item.model_copy(update={"rank": rank}) for rank, item in enumerate(ranked, start=1)]

    def _payload(self, req: PredictRequest, recommendations: list[RecommendationItem]) -> dict[str, Any]:
        return {
            "instruction": SYSTEM_PROMPT,
            "language": req.language,
            "scores": req.scores,
            "interests": req.interests,
            "preferences": req.preferences,
            "career_direction": req.career_direction,
            "constraints": req.constraints,
            "recommendations": [
                {
                    "prodi_id": item.prodi_id,
                    "nama_prodi": item.nama_prodi,
                    "kelompok_prodi": item.kelompok_prodi,
                    "score": item.suitability_score,
                    "breakdown": item.score_breakdown,
                    "skill_gaps": item.skill_gaps,
                    "tradeoffs": item.tradeoffs,
                }
                for item in recommendations
                if item.prodi_id
            ],
        }

    def _call_gemini(self, payload: dict[str, Any]) -> str:
        body = json.dumps({"contents": [{"parts": [{"text": json.dumps(payload, ensure_ascii=False)}]}], "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}}).encode("utf-8")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
        request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=settings.llm_timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def _call_openai(self, payload: dict[str, Any]) -> str:
        body = json.dumps({"model": settings.openai_model, "temperature": 0.2, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}], "response_format": {"type": "json_object"}}).encode("utf-8")
        request = Request("https://api.openai.com/v1/chat/completions", data=body, headers={"Content-Type": "application/json", "Authorization": f"Bearer {settings.openai_api_key}"}, method="POST")
        try:
            with urlopen(request, timeout=settings.llm_timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except URLError:
            raise
        return data["choices"][0]["message"]["content"]

    def _parse(self, raw: str, allowed_ids: set[str]) -> dict[str, Any]:
        data = json.loads(raw)
        items: dict[str, dict[str, Any]] = {}
        for item in data.get("items", []):
            prodi_id = str(item.get("prodi_id", ""))
            if prodi_id not in allowed_ids:
                continue
            adjustment = max(-MAX_ADJUSTMENT, min(MAX_ADJUSTMENT, int(item.get("score_adjustment", 0))))
            note = str(item.get("review_note", ""))[:160]
            items[prodi_id] = {"score_adjustment": adjustment, "review_note": note}
        return {"items": items, "summary": data.get("summary")}


llm_review_service = LLMReviewService()
