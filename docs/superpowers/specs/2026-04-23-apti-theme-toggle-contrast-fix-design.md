# Apti Theme Toggle and Light-Mode Contrast Fix Design

**Goal:** Fix low-contrast Apti form surfaces visible in current light theme, and add a persistent light/dark mode toggle while restyling Apti closer to a Notion-like light and dark UI without changing recommendation behavior.

**Scope:** Frontend-only. This chunk covers theme tokens, header toggle, persistence, and contrast cleanup for current Apti shell, journey, and result views. It does **not** include deployment, Git push, backend API changes, or ML logic changes.

## Problem Summary

Current frontend mixes semantic CSS variables with hardcoded utility colors such as `border-white/20`, `bg-white/70`, and dark-leaning text/border combinations. In light theme this creates washed-out panels, weak labels, and poor field contrast, as shown in screenshot. Theme state also does not exist yet, so dark mode cannot be added cleanly without first consolidating color usage.

## Chosen Approach

Use **CSS token theme system** with `data-theme="light|dark"` on root shell container.

Why this approach:
- fixes screenshot bug at root cause instead of patching scattered classes
- supports dark mode without duplicating component logic
- shifts current Apti editorial look toward a closer Notion-like replica in both light and dark modes
- limits churn to styling layer plus one small toggle control

## User Decisions

- Default theme: **light**
- Toggle placement: **header button near `Restart intro`**
- Visual direction: **closer Notion-like replica in light and dark modes**
- Light mode constraint: **fix contrast while keeping clean, quiet, document-like surfaces**
- Dark mode constraint: **mirror Notion-like neutral dark surfaces, not neon/cyber styling**

## Architecture

### 1. Theme State Model

Add small frontend helper for theme persistence.

State shape:
- `theme: 'light' | 'dark'`

Behavior:
- default to `'light'`
- load saved theme from `localStorage`
- save on user toggle
- expose helper functions similar in style to existing `introState` helper

Likely file:
- `frontend/src/lib/themeState.js`

## 2. Root Theme Application

`App.jsx` will own current theme state and pass toggle action into `AptiShell`.

`AptiShell.jsx` will:
- render header actions row with theme toggle + restart intro button
- apply theme attribute on outer wrapper, e.g. `data-theme={theme}`
- keep layout and copy responsibilities unchanged beyond header action area

This keeps theming at shell boundary rather than buried inside form/result components.

## 3. Semantic Theme Tokens

`styles.css` will define semantic variables for both modes.

Core tokens:
- `--shell-bg`
- `--shell-surface`
- `--shell-surface-strong`
- `--shell-border`
- `--shell-border-strong`
- `--shell-shadow`
- `--shell-shadow-soft`
- `--shell-ink`
- `--shell-muted`
- `--shell-subtle`
- `--shell-accent`
- `--shell-success`
- `--shell-danger`
- `--input-bg`
- `--input-placeholder`
- `--button-secondary-bg`
- `--button-secondary-border`

Light mode uses Notion-like neutral paper surfaces, soft gray borders, restrained shadows, and strong text contrast. Dark mode uses Notion-like charcoal surfaces, soft separators, muted secondary text, and same accent hierarchy. Both modes avoid glassmorphism, heavy gradients, and glossy effects.

## 4. Contrast Cleanup Rules

Replace hardcoded visual classes that conflict with theme tokens.

Examples of what changes:
- `border-white/20` → semantic border token usage
- `bg-white/70` → semantic secondary surface token
- `text-red-700` / `text-red-800` → semantic danger token
- direct slate border/text utilities on fields/buttons → semantic tokens

Files in scope:
- `frontend/src/components/features/AptiShell.jsx`
- `frontend/src/components/features/RecommendationJourney.jsx`
- `frontend/src/components/features/ResultSectionAdvanced.jsx`
- `frontend/src/components/features/AptiIntroFlow.jsx`
- `frontend/src/styles.css`

## 5. Theme Toggle UX

Header button behavior:
- placed near `Restart intro`
- label shows opposite destination clearly, e.g. `Dark mode` while in light, `Light mode` while in dark
- no icon dependency required for this chunk
- accessible button semantics only; no hidden gestures

## 6. Testing

### Automated
Add focused tests for:
- theme helper defaulting to light
- theme helper persistence roundtrip
- App/AptiShell rendering toggle and applying stored theme

Existing frontend tests must continue passing.

### Manual verification
Check both modes for:
- intro card readable
- form labels readable
- inputs clearly separated from panel background
- helper copy readable
- buttons readable in both primary and secondary styles
- result cards readable
- restart intro and toggle coexist cleanly in header
- refresh preserves chosen theme

## 7. Non-Goals

Not in this chunk:
- GitHub push
- Vercel/Railway/Supabase config
- ML ranking changes
- backend explainability updates
- bilingual support
- system-theme auto detection

## 8. Risks and Mitigations

### Risk: utility classes still override token styles
Mitigation: replace conflicting hardcoded classes in scoped Apti components instead of layering more CSS on top.

### Risk: theme toggle leaks into intro/recommendation/result inconsistently
Mitigation: apply `data-theme` at shell wrapper and use shared semantic classes/tokens everywhere in Apti path.

### Risk: Notion-like target becomes loose inspiration instead of strong visual direction
Mitigation: use neutral surfaces, minimal shadow, subtle separators, quiet header controls, and avoid decorative gradients or glass effects across both modes.

### Risk: direct visual replication hurts Apti identity
Mitigation: match interaction calmness and visual grammar closely, but keep Apti naming, copy, recommendation-specific structure, and current accent color.

## 9. Success Criteria

This chunk is complete when:
- screenshot bug is gone in light mode
- light and dark modes both feel close to Notion-like UI patterns
- dark mode toggle exists in header
- theme persists on refresh
- intro, journey, and results remain readable in both modes
- current glassy or overly decorative surfaces are removed from Apti flow
- no recommendation logic changes occur
