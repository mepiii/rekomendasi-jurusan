# Purpose: Group business services (ML, telemetry, retraining) under one namespace.
# Callers: app.api routes and startup logic.
# Deps: Python package resolution.
# API: Services package marker.
# Side effects: Enables imports under app.services.* namespace.
