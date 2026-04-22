# Purpose: Backward-compatible ML service export module.
# Callers: Legacy imports from app.ml_service.
# Deps: app.services.ml_service.
# API: Re-export ml_service and related types.
# Side effects: None.

from app.services.ml_service import *  # noqa: F403
