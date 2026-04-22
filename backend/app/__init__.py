# Purpose: Mark app directory as Python package for backend module imports.
# Callers: Python import loader and uvicorn app import path.
# Deps: Python package resolution.
# API: Package initializer.
# Side effects: Enables absolute imports under app.* namespace.
