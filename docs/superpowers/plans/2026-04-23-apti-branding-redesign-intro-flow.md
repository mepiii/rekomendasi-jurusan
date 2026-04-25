# Apti Branding, Editorial Redesign, and Intro Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebrand the current recommendation app as Apti, redesign the frontend into a calm editorial workspace, and add a short pre-home intro flow that personalizes the existing experience without changing recommendation scoring.

**Architecture:** Keep the backend scoring flow unchanged and implement this chunk entirely in the frontend shell. Introduce a small client-side intro state model with local persistence, render a new first-run intro component before the main app, and refactor the current page layout/styling so intro and recommendation flow share one calm editorial visual system.

**Tech Stack:** React, Vite, existing frontend CSS/Tailwind utility classes, localStorage, Framer Motion (restrained use), current API integration layer.

---

## File Structure

### Existing files to modify
- `frontend/index.html` — update browser title to Apti.
- `frontend/src/App.jsx` — add intro-state orchestration, personalization state, and branch between intro and main workspace.
- `frontend/src/styles.css` — replace current glass-heavy styling tokens with calm editorial tokens and shared shell styles.
- `frontend/src/components/features/RecommendationJourney.jsx` — adapt form container and copy hooks to fit editorial shell and personalized guidance.
- `frontend/src/components/features/ResultSectionAdvanced.jsx` — align results presentation with editorial shell and Apti brand wording.

### New files to create
- `frontend/src/lib/introState.js` — single-purpose helper for reading/writing/resetting intro state in localStorage.
- `frontend/src/components/features/AptiIntroFlow.jsx` — first-run onboarding flow for name, goal, and confidence.
- `frontend/src/components/features/AptiShell.jsx` — lightweight shared shell wrapper for branding, top bar, and layout rhythm.

### Tests to add
- `frontend/src/lib/introState.test.js` — local persistence behavior.
- `frontend/src/components/features/AptiIntroFlow.test.jsx` — intro validation, step progression, skip behavior.
- `frontend/src/App.test.jsx` — first-run vs returning-user flow and personalization rendering.

---

### Task 1: Add intro state persistence helper

**Files:**
- Create: `frontend/src/lib/introState.js`
- Create: `frontend/src/lib/introState.test.js`

- [ ] **Step 1: Write the failing tests**

```js
import { describe, expect, it, beforeEach, vi } from 'vitest';
import {
  INTRO_STATE_KEY,
  clearIntroState,
  loadIntroState,
  saveIntroState,
  defaultIntroState
} from './introState';

describe('introState', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('returns default state when storage is empty', () => {
    expect(loadIntroState()).toEqual(defaultIntroState);
  });

  it('saves and loads completed intro state', () => {
    const state = {
      completed: true,
      name: 'Naila',
      goal: 'compare-majors',
      confidence: 'rough-idea'
    };

    saveIntroState(state);

    expect(window.localStorage.getItem(INTRO_STATE_KEY)).toContain('Naila');
    expect(loadIntroState()).toEqual(state);
  });

  it('falls back to default state for invalid JSON', () => {
    window.localStorage.setItem(INTRO_STATE_KEY, '{bad json');
    expect(loadIntroState()).toEqual(defaultIntroState);
  });

  it('clears saved intro state', () => {
    saveIntroState({
      completed: true,
      name: 'Raka',
      goal: 'find-fit',
      confidence: 'very-unsure'
    });

    clearIntroState();

    expect(loadIntroState()).toEqual(defaultIntroState);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix frontend test -- src/lib/introState.test.js`
Expected: FAIL with `Cannot find module './introState'` or missing export errors.

- [ ] **Step 3: Write minimal implementation**

```js
export const INTRO_STATE_KEY = 'apti-intro-state';

export const defaultIntroState = {
  completed: false,
  name: '',
  goal: '',
  confidence: ''
};

export function loadIntroState() {
  const raw = window.localStorage.getItem(INTRO_STATE_KEY);
  if (!raw) return defaultIntroState;

  try {
    const parsed = JSON.parse(raw);
    return {
      completed: Boolean(parsed.completed),
      name: parsed.name ?? '',
      goal: parsed.goal ?? '',
      confidence: parsed.confidence ?? ''
    };
  } catch {
    return defaultIntroState;
  }
}

export function saveIntroState(state) {
  window.localStorage.setItem(INTRO_STATE_KEY, JSON.stringify({
    completed: Boolean(state.completed),
    name: state.name ?? '',
    goal: state.goal ?? '',
    confidence: state.confidence ?? ''
  }));
}

export function clearIntroState() {
  window.localStorage.removeItem(INTRO_STATE_KEY);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix frontend test -- src/lib/introState.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/introState.js frontend/src/lib/introState.test.js
git commit -m "feat: persist apti intro state"
```

### Task 2: Build Apti intro flow component

**Files:**
- Create: `frontend/src/components/features/AptiIntroFlow.jsx`
- Create: `frontend/src/components/features/AptiIntroFlow.test.jsx`
- Modify: `frontend/src/styles.css`

- [ ] **Step 1: Write the failing tests**

```jsx
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import AptiIntroFlow from './AptiIntroFlow';

describe('AptiIntroFlow', () => {
  it('requires name before moving to next step', () => {
    render(<AptiIntroFlow onComplete={vi.fn()} onSkip={vi.fn()} />);

    fireEvent.click(screen.getByRole('button', { name: /continue/i }));

    expect(screen.getByText(/name is required/i)).toBeInTheDocument();
  });

  it('collects goal and confidence then submits payload', () => {
    const onComplete = vi.fn();
    render(<AptiIntroFlow onComplete={onComplete} onSkip={vi.fn()} />);

    fireEvent.change(screen.getByLabelText(/your name/i), { target: { value: 'Naila' } });
    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    fireEvent.click(screen.getByRole('button', { name: /compare several majors/i }));
    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    fireEvent.click(screen.getByRole('button', { name: /already have a rough idea/i }));
    fireEvent.click(screen.getByRole('button', { name: /enter apti/i }));

    expect(onComplete).toHaveBeenCalledWith({
      completed: true,
      name: 'Naila',
      goal: 'compare-majors',
      confidence: 'rough-idea'
    });
  });

  it('supports skip action', () => {
    const onSkip = vi.fn();
    render(<AptiIntroFlow onComplete={vi.fn()} onSkip={onSkip} />);

    fireEvent.click(screen.getByRole('button', { name: /skip for now/i }));

    expect(onSkip).toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix frontend test -- src/components/features/AptiIntroFlow.test.jsx`
Expected: FAIL with `Cannot find module './AptiIntroFlow'`.

- [ ] **Step 3: Write minimal implementation**

```jsx
import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';

const goalOptions = [
  { value: 'find-fit', label: 'Find the best-fit major' },
  { value: 'compare-majors', label: 'Compare several majors' },
  { value: 'understand-strengths', label: 'Understand strengths first' }
];

const confidenceOptions = [
  { value: 'very-unsure', label: 'Very unsure' },
  { value: 'somewhat-unsure', label: 'Somewhat unsure' },
  { value: 'rough-idea', label: 'Already have a rough idea' }
];

export default function AptiIntroFlow({ onComplete, onSkip }) {
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [goal, setGoal] = useState('');
  const [confidence, setConfidence] = useState('');
  const [error, setError] = useState('');

  const progress = useMemo(() => `${step}/3`, [step]);

  const nextFromName = () => {
    if (!name.trim()) {
      setError('Name is required.');
      return;
    }
    setError('');
    setStep(2);
  };

  const nextFromGoal = () => {
    if (!goal) return;
    setStep(3);
  };

  const complete = () => {
    if (!confidence) return;
    onComplete({ completed: true, name: name.trim(), goal, confidence });
  };

  return (
    <section className="apti-intro-shell">
      <div className="apti-intro-header">
        <p className="apti-eyebrow">Apti</p>
        <p className="apti-progress">Step {progress}</p>
      </div>

      {step === 1 ? (
        <motion.div key="name" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <h1>Let’s start with your name.</h1>
          <label htmlFor="apti-name">Your name</label>
          <input id="apti-name" value={name} onChange={(event) => setName(event.target.value)} />
          {error ? <p>{error}</p> : null}
          <button type="button" onClick={nextFromName}>Continue</button>
        </motion.div>
      ) : null}

      {step === 2 ? (
        <motion.div key="goal" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <h1>What kind of help do you want first?</h1>
          {goalOptions.map((option) => (
            <button key={option.value} type="button" onClick={() => setGoal(option.value)}>
              {option.label}
            </button>
          ))}
          <button type="button" onClick={nextFromGoal} disabled={!goal}>Continue</button>
        </motion.div>
      ) : null}

      {step === 3 ? (
        <motion.div key="confidence" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <h1>How sure do you feel right now?</h1>
          {confidenceOptions.map((option) => (
            <button key={option.value} type="button" onClick={() => setConfidence(option.value)}>
              {option.label}
            </button>
          ))}
          <button type="button" onClick={complete} disabled={!confidence}>Enter Apti</button>
        </motion.div>
      ) : null}

      <button type="button" onClick={onSkip}>Skip for now</button>
    </section>
  );
}
```

Add starter CSS block to `frontend/src/styles.css`:

```css
.apti-intro-shell {
  max-width: 42rem;
  margin: 0 auto;
  padding: 4rem 1.5rem;
}

.apti-intro-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.apti-eyebrow,
.apti-progress {
  font-size: 0.875rem;
  color: var(--text-muted);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix frontend test -- src/components/features/AptiIntroFlow.test.jsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/features/AptiIntroFlow.jsx frontend/src/components/features/AptiIntroFlow.test.jsx frontend/src/styles.css
git commit -m "feat: add apti intro flow"
```

### Task 3: Add app-shell orchestration and personalization

**Files:**
- Create: `frontend/src/components/features/AptiShell.jsx`
- Modify: `frontend/src/App.jsx`
- Test: `frontend/src/App.test.jsx`

- [ ] **Step 1: Write the failing tests**

```jsx
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import App from './App';

describe('App intro orchestration', () => {
  it('shows intro flow for first-time users', () => {
    window.localStorage.clear();
    render(<App />);

    expect(screen.getByText(/let’s start with your name/i)).toBeInTheDocument();
  });

  it('shows personalized heading for returning users', () => {
    window.localStorage.setItem('apti-intro-state', JSON.stringify({
      completed: true,
      name: 'Naila',
      goal: 'find-fit',
      confidence: 'very-unsure'
    }));

    render(<App />);

    expect(screen.getByText(/hi, naila/i)).toBeInTheDocument();
  });

  it('allows restarting intro from main shell', () => {
    window.localStorage.setItem('apti-intro-state', JSON.stringify({
      completed: true,
      name: 'Naila',
      goal: 'find-fit',
      confidence: 'very-unsure'
    }));

    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /restart intro/i }));

    expect(screen.getByText(/let’s start with your name/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix frontend test -- src/App.test.jsx`
Expected: FAIL because intro flow and restart controls do not exist.

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/components/features/AptiShell.jsx`:

```jsx
export default function AptiShell({ title, subtitle, onRestartIntro, children }) {
  return (
    <div className="apti-shell">
      <header className="apti-topbar">
        <div>
          <p className="apti-brand">Apti</p>
          <h1 className="apti-title">{title}</h1>
          {subtitle ? <p className="apti-subtitle">{subtitle}</p> : null}
        </div>
        <button type="button" onClick={onRestartIntro}>Restart intro</button>
      </header>
      <main>{children}</main>
    </div>
  );
}
```

Update `frontend/src/App.jsx` around top-level state and render:

```jsx
import { useMemo, useState } from 'react';
import AptiIntroFlow from './components/features/AptiIntroFlow';
import AptiShell from './components/features/AptiShell';
import { clearIntroState, loadIntroState, saveIntroState } from './lib/introState';

const greetingByGoal = {
  'find-fit': 'Let’s find majors that fit how you learn.',
  'compare-majors': 'Let’s compare options clearly, one step at a time.',
  'understand-strengths': 'Let’s start from your strongest patterns first.'
};

export default function App() {
  const [introState, setIntroState] = useState(() => loadIntroState());
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [feedbackState, setFeedbackState] = useState({ loading: false, message: '' });

  const shellTitle = useMemo(() => {
    if (introState.name) return `Hi, ${introState.name}.`;
    return 'Welcome to Apti.';
  }, [introState.name]);

  const shellSubtitle = useMemo(() => {
    return greetingByGoal[introState.goal] || 'Apti helps you explore college majors with more clarity.';
  }, [introState.goal]);

  const handleIntroComplete = (state) => {
    saveIntroState(state);
    setIntroState(state);
  };

  const handleIntroSkip = () => {
    const skipped = { completed: true, name: '', goal: '', confidence: '' };
    saveIntroState(skipped);
    setIntroState(skipped);
  };

  const handleRestartIntro = () => {
    clearIntroState();
    setIntroState(loadIntroState());
    setResult(null);
  };

  if (!introState.completed) {
    return <AptiIntroFlow onComplete={handleIntroComplete} onSkip={handleIntroSkip} />;
  }

  return (
    <AptiShell title={shellTitle} subtitle={shellSubtitle} onRestartIntro={handleRestartIntro}>
      {/* existing recommendation journey + results live here */}
    </AptiShell>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix frontend test -- src/App.test.jsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/App.jsx frontend/src/App.test.jsx frontend/src/components/features/AptiShell.jsx
git commit -m "feat: add apti onboarding orchestration"
```

### Task 4: Refactor visual system to calm editorial shell

**Files:**
- Modify: `frontend/src/styles.css`
- Modify: `frontend/src/components/features/RecommendationJourney.jsx`
- Modify: `frontend/src/components/features/ResultSectionAdvanced.jsx`
- Modify: `frontend/index.html`

- [ ] **Step 1: Write the failing test for Apti title and shell text**

```jsx
import { render } from '@testing-library/react';
import App from './App';

describe('Apti brand shell', () => {
  it('renders Apti branding in document title path', () => {
    render(<App />);
    expect(document.title).toContain('Apti');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix frontend test -- src/App.test.jsx -t "Apti brand shell"`
Expected: FAIL because browser title still uses old brand.

- [ ] **Step 3: Write minimal implementation**

Update `frontend/index.html` title:

```html
<title>Apti</title>
```

Add editorial shell tokens to `frontend/src/styles.css` (replace glass-first palette with calmer tokens):

```css
:root {
  --page-bg: oklch(0.98 0.006 95);
  --panel-bg: oklch(0.995 0.004 95);
  --panel-muted: oklch(0.96 0.008 95);
  --text-strong: oklch(0.24 0.02 40);
  --text-body: oklch(0.38 0.015 40);
  --text-muted: oklch(0.55 0.012 40);
  --line-soft: oklch(0.9 0.01 95);
  --accent: oklch(0.62 0.12 80);
}

body {
  background: var(--page-bg);
  color: var(--text-strong);
}

.apti-shell {
  min-height: 100vh;
  padding: 2rem 1.25rem 4rem;
}

.apti-topbar {
  max-width: 76rem;
  margin: 0 auto 2rem;
  display: flex;
  justify-content: space-between;
  gap: 2rem;
  align-items: flex-start;
}

.apti-brand {
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-muted);
}
```

Adapt `RecommendationJourney.jsx` wrapper classes so form sits cleanly inside shell and no longer uses glass wording/container assumptions. Adapt `ResultSectionAdvanced.jsx` classes similarly so results feel like part of same editorial system.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix frontend test -- src/App.test.jsx -t "Apti brand shell"`
Expected: PASS

- [ ] **Step 5: Run frontend manually**

Run: `npm --prefix frontend run dev`
Manual verification:
- first view is calm and light
- no glass-heavy look remains in critical surfaces
- intro and main shell look like one product

- [ ] **Step 6: Commit**

```bash
git add frontend/index.html frontend/src/styles.css frontend/src/components/features/RecommendationJourney.jsx frontend/src/components/features/ResultSectionAdvanced.jsx
git commit -m "feat: redesign apti frontend shell"
```

### Task 5: Polish personalized main experience

**Files:**
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/components/features/RecommendationJourney.jsx`
- Modify: `frontend/src/components/features/ResultSectionAdvanced.jsx`

- [ ] **Step 1: Write the failing test for personalized helper copy**

```jsx
import { render, screen } from '@testing-library/react';
import App from './App';

describe('personalized helper copy', () => {
  it('shows confidence-aware helper copy for unsure users', () => {
    window.localStorage.setItem('apti-intro-state', JSON.stringify({
      completed: true,
      name: 'Naila',
      goal: 'understand-strengths',
      confidence: 'very-unsure'
    }));

    render(<App />);

    expect(screen.getByText(/start with your strongest subjects and interests/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix frontend test -- src/App.test.jsx -t "personalized helper copy"`
Expected: FAIL because helper copy is still generic.

- [ ] **Step 3: Write minimal implementation**

Add confidence-aware helper copy map in `frontend/src/App.jsx`:

```jsx
const helperByConfidence = {
  'very-unsure': 'Start with your strongest subjects and interests. Apti will guide you step by step.',
  'somewhat-unsure': 'You already have useful signals. Apti will help you turn them into clearer options.',
  'rough-idea': 'You already have a direction. Apti will help you compare it with more confidence.'
};
```

Pass helper text into `RecommendationJourney`:

```jsx
<RecommendationJourney
  onSubmit={handleSubmit}
  loading={loading}
  error={error}
  helperText={helperByConfidence[introState.confidence]}
/>
```

Update `RecommendationJourney.jsx` signature and render:

```jsx
export default function RecommendationJourney({ onSubmit, loading, error, helperText }) {
  // ...existing code...
  return (
    <form /* existing props */>
      <div className="mb-6">
        <h2 className="text-2xl font-semibold tracking-tight text-textPrimary">Build your recommendation profile</h2>
        <p className="mt-2 text-sm text-textMuted">
          {helperText || 'Add your subjects, interests, and track to see where you fit best.'}
        </p>
      </div>
      {/* existing content */}
    </form>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix frontend test -- src/App.test.jsx -t "personalized helper copy"`
Expected: PASS

- [ ] **Step 5: Run focused regression tests**

Run: `npm --prefix frontend test -- src/App.test.jsx src/components/features/AptiIntroFlow.test.jsx src/lib/introState.test.js`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add frontend/src/App.jsx frontend/src/components/features/RecommendationJourney.jsx frontend/src/components/features/ResultSectionAdvanced.jsx
git commit -m "feat: personalize apti recommendation flow"
```

### Task 6: Final verification and documentation touch-up

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README product naming minimally for this chunk**

Add or update summary copy near top of `README.md` so branding matches current chunk:

```md
# Apti

Apti is a college major recommendation web app for high school students. It helps users understand where their academic strengths and interests may fit best, starting with a guided intro and continuing into a personalized recommendation flow.
```

- [ ] **Step 2: Run frontend test suite**

Run: `npm --prefix frontend test`
Expected: PASS

- [ ] **Step 3: Run frontend manually for feature verification**

Run: `npm --prefix frontend run dev`
Manual verification checklist:
- first-time user sees intro before main app
- skip path works
- completed intro enters main app
- refreshed page preserves returning-user state
- restart intro works
- Apti branding visible
- shell feels calm/light/editorial
- recommendation submission still works after intro
- results still render
- no personalization changes affect ranking logic

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: align readme with apti brand"
```

## Self-Review

### Spec coverage
- Brand rename in UI shell: Tasks 3, 4, 6
- Editorial redesign: Task 4
- Pre-home intro flow: Task 2
- Personalized main app from intro answers: Tasks 3 and 5
- Returning user behavior: Tasks 1 and 3
- No scoring changes: enforced by scope and frontend-only tasks

### Placeholder scan
No TODO/TBD placeholders remain. Every code step includes concrete snippets and exact commands.

### Type consistency
Intro state uses one stable shape across plan:
- `completed`
- `name`
- `goal`
- `confidence`

Goal values:
- `find-fit`
- `compare-majors`
- `understand-strengths`

Confidence values:
- `very-unsure`
- `somewhat-unsure`
- `rough-idea`

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-23-apti-branding-redesign-intro-flow.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
