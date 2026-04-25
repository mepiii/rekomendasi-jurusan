# Bilingual Editorial Redesign Design

Date: 2026-04-23
Status: Proposed

## Summary

Redesign the college major recommendation web app into a calm editorial workspace with first-class bilingual support for English and Indonesian. The experience should feel modern, easy to manage, interactive, motivating, and confident for high school students deciding on a college major. The redesign should remove the current glassmorphism-heavy presentation and replace it with a lighter, cleaner, more trust-oriented interface inspired by Notion's clarity without becoming a generic productivity clone.

## Goals

- Support English and Indonesian across the full user-visible experience.
- Add a visible language switch with browser auto-detect and persistent user override.
- Redesign the full UI/UX to feel calmer, clearer, and more trustworthy.
- Keep recommendation flow interactive through guided progress, live summary, and restrained motion.
- Localize not only UI copy but also backend-returned messages and displayed recommendation labels.

## Non-Goals

- No runtime machine translation.
- No support for more than English and Indonesian in v1.
- No dark theme in this phase.
- No major ML logic changes beyond localization of outputs.
- No generic template-like dashboard redesign.

## Product Context

### Users
High school students who struggle to choose a college major.

### Job to Be Done
Compare personal scores and interests against recommendation output, understand why the system suggests certain majors, and decide whether the result feels trustworthy enough to act on or discuss with counselors, teachers, or parents.

### Emotional Outcome
Users should feel guided, reassured, and capable of making progress instead of confused or judged.

## Experience Direction

### Chosen Direction
Calm editorial workspace.

### Why
This direction best matches student decision support. It makes results easier to trust, keeps language readable, and avoids styles the user explicitly rejected: game-like, corporate dashboard, dark cyber, glassmorphism, and AI-template visuals.

### Core Traits
- light and calm
- editorial hierarchy
- quiet premium surfaces
- restrained but present motion
- interactive without feeling playful
- supportive and concise copy

## Visual Design System

### Theme
Light theme only.

### Layout
- Use asymmetrical editorial composition instead of stacked generic cards.
- Keep text left-aligned for stronger reading rhythm.
- Use generous whitespace and clear grouping.
- Keep body copy within readable line lengths.
- Avoid card-inside-card nesting.

### Typography
- Use a distinctive display font paired with a refined body font.
- Build clear hierarchy with fewer sizes and more contrast.
- Favor concise labels and highly readable supporting copy.
- Ensure bilingual copy still reads cleanly when string lengths change.

### Color
- Replace current glass/accent-heavy treatment with tinted neutrals and restrained accent usage.
- Prioritize readability and trust over visual spectacle.
- Avoid neon, dark gradients, or decorative glow.

### Motion
- Use motion for step transitions, state changes, and progressive reveal.
- Keep motion smooth, brief, and purposeful.
- Avoid bounce, elastic movement, and decorative effects.

## Information Architecture

## 1. App Shell
- Minimal top bar with brand/title area on left.
- Language switch on right, always visible.
- Main content split into guided input area and supporting summary area.

## 2. Guided Input Journey
- Multi-step flow remains but becomes clearer and more editorial.
- Steps:
  1. academic scores
  2. interests + high school track
  3. review before submit
- Add stronger progress cues.
- Add live summary that updates while user fills fields.

## 3. Results Workspace
- Featured recommendation first.
- Alternative recommendations below in cleaner comparison layout.
- Explanation section stays available but becomes simpler to read.
- Charts remain only if they support interpretation rather than decoration.
- Feedback flow remains integrated and localized.

## 4. States
- Empty state teaches what to do next.
- Loading state feels active and trustworthy.
- Error state explains what happened and what user can do.
- Success state focuses attention on interpretation, not celebration.

## Localization Design

## Supported Languages
- English (`en`)
- Indonesian (`id`)

## Selection Behavior
- Detect browser language on first visit.
- If browser language starts with `id`, default to Indonesian.
- Otherwise default to English.
- If user switches language manually, store selection in `localStorage`.
- Stored selection always overrides browser language on later visits.

## Frontend Localization
Introduce a lightweight custom i18n layer instead of a full library.

### Structure
- `LanguageProvider` at app root.
- `useLanguage()` hook for component access.
- Central translation dictionaries for `en` and `id`.
- Utility for translating display labels such as subject names, interests, majors, and UI states.

### Why Custom
The app is small enough that a custom dictionary-based layer keeps control high and complexity low. Adding a full i18n framework would create more setup cost than value for current scope.

## Backend Localization
Backend should accept language context from client and localize user-facing responses.

### Scope
- validation messages
- system error messages
- feedback submission messages
- disclaimers
- majors/interests fallback labels
- explanation labels and feature names

### Rule
Keep internal/canonical values stable. Localize only outward-facing strings.

## Data Model and API Behavior

### Request Language
Preferred approach:
- include `lang` in request payloads where relevant
- allow query param for fetch-style endpoints such as explanation reads

### Response Language
Responses should return user-facing strings in requested language.

### Stable Internal Values
Canonical identifiers remain language-neutral or stable English-like values so app logic, ML mapping, and analytics stay consistent.

## Component Plan

### Frontend
Likely touched areas:
- app shell
- recommendation journey
- results section
- result card/explanation display
- API integration layer
- shared language state and dictionaries
- styling tokens and page layout

### Backend
Likely touched areas:
- request/response schemas if `lang` added
- API route message construction
- ML service display-label maps
- fallback majors/interests definitions

## Error Handling

### Fallback Rules
- unsupported language → English
- missing translation key → English fallback
- missing backend translation path → English response

### Safety
No request should fail because translation is missing. Missing localized content degrades to English.

## Accessibility
- language switch must be keyboard accessible
- preserve focus visibility across redesign
- maintain sufficient contrast in light theme
- avoid motion patterns that disorient
- support reduced-motion preference where motion exists

## Testing Strategy

### Functional
- first load picks correct browser language
- manual switch updates visible UI instantly
- manual switch persists after reload
- recommendation flow works in both languages
- backend messages localize correctly
- result labels and explanation labels switch correctly

### UX Regression
- layout still readable with longer Indonesian strings
- no clipped controls in step flow or results view
- summary and charts remain understandable in both languages

### Deployment/Config
- Vercel frontend continues to build with no extra localization service
- backend deployment remains stable with any new `lang` wiring
- docs updated to explain bilingual behavior

## Repo and Config Updates

- Update repo code to include bilingual support and redesign assets/code.
- Update deployment configuration only if language behavior requires explicit environment/config changes.
- Update README to document bilingual support and language persistence behavior.
- Keep Vercel and Railway setup simple; no external translation platform.

## Implementation Approach Recommendation

Recommended approach: lightweight custom i18n plus calm editorial redesign.

Why:
- Best fit for current app size.
- Best match for requested Notion-like calm minimal direction.
- Lowest dependency cost.
- Full control over localized recommendation labels and backend responses.
- Easier to keep trust-oriented copy consistent across both languages.

## Risks

### Risk 1: Translation logic scattered across app
Mitigation: centralize dictionaries and display-label translation utilities.

### Risk 2: Backend and frontend language maps drift
Mitigation: define stable canonical identifiers and map outward strings consistently.

### Risk 3: Indonesian strings break layout
Mitigation: test all key screens in both languages and design for length flexibility.

### Risk 4: Redesign removes useful information density
Mitigation: preserve current analytical depth while improving grouping and readability.

## Success Criteria

- User can switch between English and Indonesian from visible UI control.
- Language preference persists across reloads.
- Full major recommendation journey works in both languages.
- Recommendation, explanation, feedback, and error states all display in selected language.
- UI no longer feels glassy, dashboard-like, or template-generated.
- Redesigned interface feels calm, interactive, modern, and confidence-building.
