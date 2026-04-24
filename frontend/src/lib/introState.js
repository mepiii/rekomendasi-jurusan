// Purpose: Persist Apti intro flow state in browser storage.
// Callers: Intro flow orchestration in frontend app shell.
// Deps: Browser window.localStorage and JSON serialization.
// API: Exports key, default state, load/save/clear helper functions.
// Side effects: Reads, writes, and removes localStorage entries.
export const INTRO_STATE_KEY = 'apti-intro-state';

export const defaultIntroState = {
  completed: false,
  name: '',
  goal: '',
  confidence: ''
};

const helperCopyByConfidence = {
  'very-unsure': 'Start with your strongest subjects and interests, then narrow from there.',
  'somewhat-unsure': 'Use the mix of scores and interests to compare a few directions with more confidence.',
  'rough-idea': 'Pressure-test your current direction with updated scores and interests before deciding.'
};

const defaultHelperCopy = 'Share your latest scores and interests to get a grounded shortlist of majors.';

const normalizeIntroState = (state = {}) => ({
  completed: Boolean(state.completed),
  name: state.name ?? '',
  goal: state.goal ?? '',
  confidence: state.confidence ?? ''
});

export function getHelperCopy() {
  return helperCopyByConfidence[loadIntroState().confidence] || defaultHelperCopy;
}

export function loadIntroState() {
  const raw = window.localStorage.getItem(INTRO_STATE_KEY);
  if (!raw) return defaultIntroState;

  try {
    return normalizeIntroState(JSON.parse(raw));
  } catch {
    return defaultIntroState;
  }
}

export function saveIntroState(state) {
  window.localStorage.setItem(INTRO_STATE_KEY, JSON.stringify(normalizeIntroState(state)));
}

export function clearIntroState() {
  window.localStorage.removeItem(INTRO_STATE_KEY);
}
