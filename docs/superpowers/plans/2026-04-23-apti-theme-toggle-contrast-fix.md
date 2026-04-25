# Apti Theme Toggle and Contrast Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix Apti light-mode contrast bug, add persistent light/dark theme toggle, and restyle core Apti screens closer to a Notion-like light and dark UI without changing recommendation behavior.

**Architecture:** Introduce a small `themeState` helper for persistence, let `App.jsx` own current theme, and have `AptiShell.jsx` apply `data-theme` plus header actions. Move visual decisions into semantic CSS tokens in `styles.css`, then replace conflicting hardcoded utility colors in Apti intro, journey, and result components so both modes share one consistent theme system.

**Tech Stack:** React, Vite, Vitest, browser `localStorage`, CSS custom properties, current Apti component structure.

---

## File Structure

### Existing files to modify
- `frontend/src/App.jsx` — own theme state, pass theme/toggle into shell, keep intro/prediction flow unchanged.
- `frontend/src/components/features/AptiShell.jsx` — apply `data-theme`, render theme toggle beside restart button, keep shell layout focused.
- `frontend/src/components/features/AptiIntroFlow.jsx` — remove hardcoded visual classes that break cross-theme contrast.
- `frontend/src/components/features/RecommendationJourney.jsx` — replace conflicting borders/backgrounds/error colors with semantic theme classes.
- `frontend/src/components/features/ResultSectionAdvanced.jsx` — align surfaces, chips, feedback controls, and helper text with theme tokens.
- `frontend/src/styles.css` — define semantic variables for light and dark themes, remove glass-heavy styling, add Notion-like neutral surfaces.
- `frontend/src/App.test.jsx` — verify theme toggle rendering and stored theme application.

### New files to create
- `frontend/src/lib/themeState.js` — load/save/toggle helper for `'light' | 'dark'`.
- `frontend/src/lib/themeState.test.js` — persistence and default behavior tests.

### Tests to add
- `frontend/src/lib/themeState.test.js` — persistence helper tests.
- `frontend/src/App.test.jsx` — theme toggle + stored theme path.

---

### Task 1: Add theme persistence helper

**Files:**
- Create: `frontend/src/lib/themeState.js`
- Create: `frontend/src/lib/themeState.test.js`

- [ ] **Step 1: Write the failing test**

```js
import { beforeEach, describe, expect, it } from 'vitest';
import {
  THEME_KEY,
  defaultTheme,
  loadTheme,
  saveTheme,
  toggleTheme
} from './themeState';

describe('themeState', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('defaults to light when storage is empty', () => {
    expect(loadTheme()).toBe(defaultTheme);
  });

  it('saves and loads dark theme', () => {
    saveTheme('dark');

    expect(window.localStorage.getItem(THEME_KEY)).toBe('dark');
    expect(loadTheme()).toBe('dark');
  });

  it('falls back to light for invalid stored value', () => {
    window.localStorage.setItem(THEME_KEY, 'sepia');
    expect(loadTheme()).toBe(defaultTheme);
  });

  it('toggles between light and dark', () => {
    expect(toggleTheme('light')).toBe('dark');
    expect(toggleTheme('dark')).toBe('light');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix frontend test -- src/lib/themeState.test.js`
Expected: FAIL with `Cannot find module './themeState'`.

- [ ] **Step 3: Write minimal implementation**

```js
export const THEME_KEY = 'apti-theme';
export const defaultTheme = 'light';

const validThemes = new Set(['light', 'dark']);

export function loadTheme() {
  const stored = window.localStorage.getItem(THEME_KEY);
  return validThemes.has(stored) ? stored : defaultTheme;
}

export function saveTheme(theme) {
  const nextTheme = validThemes.has(theme) ? theme : defaultTheme;
  window.localStorage.setItem(THEME_KEY, nextTheme);
  return nextTheme;
}

export function toggleTheme(theme) {
  return theme === 'dark' ? 'light' : 'dark';
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix frontend test -- src/lib/themeState.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/themeState.js frontend/src/lib/themeState.test.js
git commit -m "feat: persist apti theme state"
```

### Task 2: Wire theme state through App and shell

**Files:**
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/components/features/AptiShell.jsx`
- Modify: `frontend/src/App.test.jsx`
- Use: `frontend/src/lib/themeState.js`

- [ ] **Step 1: Write the failing test**

Add tests to `frontend/src/App.test.jsx`:

```jsx
it('shows dark mode toggle for returning users in light theme', () => {
  window.localStorage.setItem(
    'apti-intro-state',
    JSON.stringify({
      completed: true,
      name: 'Raka',
      goal: 'find-fit',
      confidence: ''
    })
  );

  render(<App />);

  expect(screen.getByRole('button', { name: /dark mode/i })).toBeInTheDocument();
});

it('applies stored dark theme on shell root', () => {
  window.localStorage.setItem(
    'apti-intro-state',
    JSON.stringify({
      completed: true,
      name: 'Raka',
      goal: 'find-fit',
      confidence: ''
    })
  );
  window.localStorage.setItem('apti-theme', 'dark');

  render(<App />);

  expect(screen.getByTestId('apti-shell')).toHaveAttribute('data-theme', 'dark');
  expect(screen.getByRole('button', { name: /light mode/i })).toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix frontend test -- src/App.test.jsx`
Expected: FAIL because shell has no theme toggle and no `data-theme` attribute.

- [ ] **Step 3: Write minimal implementation**

Update `frontend/src/App.jsx` imports and state:

```jsx
import { loadTheme, saveTheme, toggleTheme } from './lib/themeState';

const [theme, setTheme] = useState(() => loadTheme());

const handleThemeToggle = () => {
  const nextTheme = toggleTheme(theme);
  saveTheme(nextTheme);
  setTheme(nextTheme);
};
```

Pass theme into shell:

```jsx
<AptiShell
  theme={theme}
  onToggleTheme={handleThemeToggle}
  title={shellContent.title}
  subtitle={shellContent.subtitle}
  actions={shellContent.actions}
>
```

Update `frontend/src/components/features/AptiShell.jsx`:

```jsx
export default function AptiShell({ theme, onToggleTheme, title, subtitle, actions = null, children }) {
  const themeLabel = theme === 'dark' ? 'Light mode' : 'Dark mode';

  return (
    <main data-testid="apti-shell" data-theme={theme} className="apti-shell min-h-screen w-full px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
        {title || subtitle || actions ? (
          <header className="apti-shell-header flex flex-col gap-4 rounded-3xl p-6 sm:flex-row sm:items-start sm:justify-between">
            <div className="space-y-2">
              <p className="apti-shell-brand text-xs uppercase tracking-[0.2em]">Apti</p>
              {title ? <h1 className="text-3xl font-semibold tracking-tight">{title}</h1> : null}
              {subtitle ? <p className="max-w-2xl text-sm">{subtitle}</p> : null}
            </div>
            <div className="flex items-center gap-3">
              <button type="button" onClick={onToggleTheme} className="apti-secondary-button rounded-xl px-4 py-2 text-sm font-medium">
                {themeLabel}
              </button>
              {actions}
            </div>
          </header>
        ) : null}
        <div className="flex w-full flex-col items-center gap-6">{children}</div>
      </div>
    </main>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix frontend test -- src/App.test.jsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/App.jsx frontend/src/App.test.jsx frontend/src/components/features/AptiShell.jsx
git commit -m "feat: add apti theme toggle shell"
```

### Task 3: Replace global visual tokens with Notion-like light and dark themes

**Files:**
- Modify: `frontend/src/styles.css`

- [ ] **Step 1: Write the failing test**

Add a test block to `frontend/src/App.test.jsx`:

```jsx
it('renders shell with theme-aware root attribute for CSS token styling', () => {
  window.localStorage.setItem(
    'apti-intro-state',
    JSON.stringify({ completed: true, name: 'Raka', goal: 'find-fit', confidence: '' })
  );

  render(<App />);

  expect(screen.getByTestId('apti-shell')).toHaveAttribute('data-theme', 'light');
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix frontend test -- src/App.test.jsx -t "theme-aware root attribute"`
Expected: FAIL until Task 2 shell changes exist.

- [ ] **Step 3: Write minimal implementation**

Replace top of `frontend/src/styles.css` with semantic tokens:

```css
:root {
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  font-feature-settings: 'cv01', 'ss03';
}

html,
body,
#root {
  min-height: 100%;
}

body {
  margin: 0;
}

.apti-shell[data-theme='light'] {
  --shell-bg: #ffffff;
  --shell-surface: #ffffff;
  --shell-surface-strong: #ffffff;
  --shell-border: rgba(55, 53, 47, 0.16);
  --shell-border-strong: rgba(55, 53, 47, 0.28);
  --shell-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
  --shell-shadow-soft: 0 1px 1px rgba(15, 23, 42, 0.04);
  --shell-ink: #37352f;
  --shell-muted: #6b6f76;
  --shell-subtle: #8a8f98;
  --shell-accent: #4f46e5;
  --shell-success: #2f7d4f;
  --shell-danger: #c2410c;
  --input-bg: #ffffff;
  --input-placeholder: #9ca3af;
  --button-secondary-bg: #ffffff;
  --button-secondary-border: rgba(55, 53, 47, 0.16);
  background: #f7f6f3;
  color: var(--shell-ink);
}

.apti-shell[data-theme='dark'] {
  --shell-bg: #191919;
  --shell-surface: #202020;
  --shell-surface-strong: #252525;
  --shell-border: rgba(255, 255, 255, 0.12);
  --shell-border-strong: rgba(255, 255, 255, 0.18);
  --shell-shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
  --shell-shadow-soft: 0 1px 1px rgba(0, 0, 0, 0.28);
  --shell-ink: #e9e9e7;
  --shell-muted: #a8a29e;
  --shell-subtle: #8b8b8b;
  --shell-accent: #818cf8;
  --shell-success: #4ade80;
  --shell-danger: #fb923c;
  --input-bg: #2a2a2a;
  --input-placeholder: #8b8b8b;
  --button-secondary-bg: #252525;
  --button-secondary-border: rgba(255, 255, 255, 0.12);
  background: #191919;
  color: var(--shell-ink);
}

.apti-shell {
  background: var(--shell-bg);
  color: var(--shell-ink);
}

.apti-shell-header,
.glass-panel,
.editorial-shell {
  border: 1px solid var(--shell-border);
  background: var(--shell-surface);
  box-shadow: var(--shell-shadow);
  backdrop-filter: none;
}

.glass-input {
  color: var(--shell-ink);
  background: var(--input-bg);
  border: 1px solid var(--shell-border-strong);
  outline: none;
}

.glass-input::placeholder {
  color: var(--input-placeholder);
}

.glass-input:focus {
  border-color: var(--shell-accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--shell-accent) 14%, transparent);
}

.apti-secondary-button {
  color: var(--shell-ink);
  background: var(--button-secondary-bg);
  border: 1px solid var(--button-secondary-border);
}

.editorial-kicker,
.text-textSubtle {
  color: var(--shell-subtle);
}

.text-textMuted,
.text-textSecondary {
  color: var(--shell-muted);
}

.text-textPrimary {
  color: var(--shell-ink);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix frontend test -- src/App.test.jsx -t "theme-aware root attribute"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/styles.css frontend/src/App.test.jsx
git commit -m "feat: add notion-like apti theme tokens"
```

### Task 4: Fix intro and journey contrast with semantic theme classes

**Files:**
- Modify: `frontend/src/components/features/AptiIntroFlow.jsx`
- Modify: `frontend/src/components/features/RecommendationJourney.jsx`

- [ ] **Step 1: Write the failing test**

Add to `frontend/src/App.test.jsx`:

```jsx
it('renders journey shell controls with readable theme button labels', () => {
  window.localStorage.setItem(
    'apti-intro-state',
    JSON.stringify({ completed: true, name: 'Raka', goal: 'find-fit', confidence: '' })
  );

  render(<App />);

  expect(screen.getByRole('button', { name: /dark mode/i })).toBeInTheDocument();
  expect(screen.getByText(/find a major direction that feels grounded/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/mathematics/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix frontend test -- src/App.test.jsx -t "renders journey shell controls"`
Expected: FAIL if theme shell or labels are not accessible after refactor.

- [ ] **Step 3: Write minimal implementation**

Update `frontend/src/components/features/AptiIntroFlow.jsx` button and surface classes:

```jsx
<section className="glass-panel w-full max-w-3xl rounded-3xl p-6 sm:p-8">
...
{error ? <p className="text-sm text-[var(--shell-danger)]">{error}</p> : null}
...
<button type="button" onClick={onSkip} className="apti-secondary-button rounded-xl px-4 py-2 text-sm font-medium">
  Skip for now
</button>
```

Update `frontend/src/components/features/RecommendationJourney.jsx` conflicting classes:

```jsx
<div className="glass-panel editorial-shell w-full max-w-3xl rounded-[28px] p-6 sm:p-8">
...
className={`glass-input rounded-xl border px-3 py-2 text-sm ${errors[key] ? 'border-[var(--shell-danger)]' : ''}`}
...
{errors[key] ? <span className="text-xs text-[var(--shell-danger)]">{errors[key]}</span> : null}
...
className={`rounded-full border px-3 py-1 text-xs transition ${
  active
    ? 'border-[var(--shell-accent)] text-[var(--shell-accent)]'
    : 'editorial-chip'
}`}
...
<button type="button" onClick={goBack} className="apti-secondary-button rounded-xl px-4 py-2 text-sm transition disabled:opacity-40">
  Back
</button>
```

Keep copy and flow unchanged.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix frontend test -- src/App.test.jsx -t "renders journey shell controls"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/features/AptiIntroFlow.jsx frontend/src/components/features/RecommendationJourney.jsx frontend/src/App.test.jsx
git commit -m "fix: improve apti intro and form contrast"
```

### Task 5: Fix result screen contrast and shared control styling

**Files:**
- Modify: `frontend/src/components/features/ResultSectionAdvanced.jsx`
- Modify: `frontend/src/styles.css`

- [ ] **Step 1: Write the failing test**

Add to `frontend/src/App.test.jsx`:

```jsx
it('shows light mode toggle label when dark theme is stored', () => {
  window.localStorage.setItem(
    'apti-intro-state',
    JSON.stringify({ completed: true, name: 'Raka', goal: 'find-fit', confidence: '' })
  );
  window.localStorage.setItem('apti-theme', 'dark');

  render(<App />);

  expect(screen.getByRole('button', { name: /light mode/i })).toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm --prefix frontend test -- src/App.test.jsx -t "light mode toggle label when dark theme is stored"`
Expected: FAIL until dark label logic is wired and stable.

- [ ] **Step 3: Write minimal implementation**

Update `frontend/src/components/features/ResultSectionAdvanced.jsx` to remove remaining hardcoded light-only borders/backgrounds:

```jsx
<div className="glass-panel editorial-shell rounded-[24px] p-5">
...
<span className="editorial-chip rounded-full px-3 py-1 text-[11px] uppercase tracking-[0.18em]">
  Latency {result.latency_ms ?? '-'} ms
</span>
...
<select className="glass-input rounded-xl px-3 py-2 text-sm">
...
<input className="glass-input rounded-xl px-3 py-2 text-sm" />
...
<textarea className="glass-input mt-3 h-20 w-full rounded-xl px-3 py-2 text-sm" />
...
<button type="button" onClick={onReset} className="apti-secondary-button rounded-xl px-4 py-2 text-sm font-medium">
  Try Different Inputs
</button>
...
{feedbackState.message ? <p className="mt-2 text-xs text-textMuted">{feedbackState.message}</p> : null}
```

If needed, extend `styles.css` with shared helper classes:

```css
.editorial-chip {
  border: 1px solid var(--shell-border);
  background: var(--shell-surface-strong);
  color: var(--shell-muted);
}

.editorial-rule {
  height: 1px;
  background: var(--shell-border);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm --prefix frontend test -- src/App.test.jsx -t "light mode toggle label when dark theme is stored"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/features/ResultSectionAdvanced.jsx frontend/src/styles.css frontend/src/App.test.jsx
git commit -m "fix: align apti results with theme system"
```

### Task 6: Full verification for both modes

**Files:**
- Modify if needed: `frontend/src/App.test.jsx`

- [ ] **Step 1: Run focused frontend tests**

Run: `npm --prefix frontend test -- src/lib/themeState.test.js src/App.test.jsx src/lib/introState.test.js`
Expected: PASS

- [ ] **Step 2: Run full frontend test suite**

Run: `npm --prefix frontend test`
Expected: PASS

- [ ] **Step 3: Run production build**

Run: `npm --prefix frontend run build`
Expected: PASS with no errors

- [ ] **Step 4: Run frontend manually**

Run: `npm --prefix frontend run dev`

Manual checklist:
- light mode default loads on fresh browser storage
- header shows `Dark mode` beside `Restart intro`
- click toggle changes to dark mode without breaking layout
- refresh preserves dark mode
- click toggle again returns to light mode
- intro card readable in both modes
- form labels and inputs readable in both modes
- result cards readable in both modes
- no glossy/glass-heavy visuals remain in Apti flow
- UI feels closer to Notion-like neutral light/dark surfaces
- recommendation submission still works
- result rendering still works

- [ ] **Step 5: Commit**

```bash
git add frontend/src/App.test.jsx

git commit -m "feat: finish apti theme toggle and contrast refresh"
```

## Self-Review

### Spec coverage
- theme helper persistence: Task 1
- App-owned theme state and shell toggle: Task 2
- `data-theme` root application: Tasks 2 and 3
- Notion-like light/dark token system: Task 3
- contrast cleanup in intro/journey/results: Tasks 4 and 5
- persistent header toggle near restart intro: Task 2
- manual and automated verification: Task 6
- no recommendation logic changes: preserved across Tasks 2-5 by limiting edits to state wiring and styles only

### Placeholder scan
No TODO/TBD placeholders remain. Each task includes exact file paths, concrete test code, implementation snippets, commands, and expected outputs.

### Type consistency
Theme state uses one stable type across plan:
- `theme: 'light' | 'dark'`

Theme helper exports stay consistent across tasks:
- `THEME_KEY`
- `defaultTheme`
- `loadTheme()`
- `saveTheme(theme)`
- `toggleTheme(theme)`
