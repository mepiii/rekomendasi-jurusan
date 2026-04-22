// Purpose: HTTP client helpers for backend API calls.
// Callers: Form submit flow and app startup wake-up ping.
// Deps: Browser fetch API and Vite env vars.
// API: pingHealth(), predict(), submitFeedback(), fetchExplanations().
// Side effects: Executes network requests to backend service.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function parseJsonSafe(response) {
  try {
    return await response.json();
  } catch {
    return {};
  }
}

export async function pingHealth() {
  try {
    await fetch(`${API_URL}/health`, { method: 'GET' });
  } catch {
    return null;
  }
  return null;
}

export async function predict(payload, timeoutMs = 10000) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_URL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal
    });

    const json = await parseJsonSafe(response);

    if (!response.ok) {
      const error = new Error(json?.message || 'Request failed');
      error.status = response.status;
      error.payload = json;
      throw error;
    }

    return json;
  } finally {
    clearTimeout(timeout);
  }
}

export async function submitFeedback(payload) {
  const response = await fetch(`${API_URL}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const json = await parseJsonSafe(response);
  if (!response.ok) {
    const error = new Error(json?.message || 'Feedback failed');
    error.status = response.status;
    error.payload = json;
    throw error;
  }

  return json;
}

export async function fetchExplanations(sessionId) {
  const response = await fetch(`${API_URL}/explanations/${sessionId}`, {
    method: 'GET'
  });

  const json = await parseJsonSafe(response);
  if (!response.ok) {
    const error = new Error(json?.message || 'Fetch explanations failed');
    error.status = response.status;
    error.payload = json;
    throw error;
  }

  return json;
}
