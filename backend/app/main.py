# Purpose: Initialize FastAPI app, middleware, validation handler, and route mounting.
# Callers: Uvicorn/ASGI entrypoint.
# Deps: FastAPI, CORS middleware, app.api router, app.services.
# API: App instance exposing REST endpoints via router.
# Side effects: Loads ML model artifacts on startup.

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import settings
from app.services.ml_service import ml_service

app = FastAPI(title="College Major Recommendation API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.on_event("startup")
def startup_event() -> None:
    try:
        ml_service.load()
    except Exception:
        return


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for item in exc.errors():
        path = [str(part) for part in item.get("loc", []) if part != "body"]
        details.append({"field": ".".join(path), "issue": item.get("msg", "invalid")})

    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Invalid input.",
            "details": details,
        },
    )


app.include_router(router)
