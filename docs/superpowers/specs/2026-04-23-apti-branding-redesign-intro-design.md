# Apti Branding, Editorial Redesign, and Intro Flow Design

Date: 2026-04-23
Status: Proposed

## Summary

This spec defines chunk 1 of the broader Apti product evolution:
- rename the product to **Apti**
- redesign the current web experience into a calm editorial workspace
- add a pre-home interactive intro flow
- personalize the main app using intro answers

This chunk explicitly does **not** change recommendation scoring, bilingual architecture, school-system localization, expanded interest taxonomy, deployment flows, or README overhaul. Those will be handled as later chunks.

## Goals

- Establish **Apti** as the primary brand across the interface.
- Replace the current glass-heavy visual style with a calmer editorial system.
- Introduce a short pre-home interactive flow that feels guided, not gimmicky.
- Personalize the main experience using intro answers.
- Preserve existing recommendation logic while improving trust and first-run experience.

## Non-Goals

- No model retraining or scoring changes.
- No bilingual implementation in this chunk.
- No school-track taxonomy redesign in this chunk.
- No deployment or infrastructure changes in this chunk.
- No chatbot-style product shell.

## Product Context

### Users
High school students who struggle to choose a college major.

### Job to Be Done
Understand what kind of academic direction fits them, feel more confident about where to start, and trust the result enough to continue using the product or discuss it with parents, teachers, or counselors.

### Brand Personality
Apti should feel like a calm academic advisor.

### Emotional Outcome
Users should feel:
- guided
- understood
- less overwhelmed
- more confident about taking the next step

## Experience Direction

### Chosen Direction
Guided editorial onboarding.

### Why
This direction is interactive without turning the product into a chat clone or game-like experience. It fits the requested Notion-like calm minimal tone while still giving the product a more human first impression.

## Visual Direction

### Theme
- light theme only
- no neon, no dark cyber look
- no glassmorphism-heavy treatment
- no AI-template feel
- no corporate dashboard chrome

### Layout Principles
- editorial composition with clearer visual rhythm
- left-aligned reading flow
- generous whitespace
- fewer nested cards
- calmer surfaces with stronger hierarchy

### Interaction Principles
- subtle, purposeful motion only
- fast transitions between intro steps
- visible progress and clear next action
- no fake typing animation gimmicks
- no faux-chat clutter

## Chunk Scope

This chunk covers:
1. Apti brand rename in UI shell and key user-facing labels
2. new editorial visual system for landing/app shell
3. pre-home intro flow
4. personalized main-screen copy driven by intro answers
5. returning-user handling for intro state

This chunk does not cover:
1. multilingual support
2. Indonesian/English school-system split
3. model retraining or bias changes
4. README/documentation rewrite
5. Vercel/Supabase/Railway redeploy work

## Intro Flow Design

### Purpose
The intro flow should make first-time users feel welcomed and understood before they see the full recommendation workspace.

### Structure
The intro flow contains three short steps:
1. name
2. goal
3. confidence level

### Input Types
- **Name**: free text
- **Goal**: structured option choices
- **Confidence level**: structured option choices

### Recommended Goal Options
- find the best-fit major
- compare several majors
- understand strengths first

### Recommended Confidence Options
- very unsure
- somewhat unsure
- already have a rough idea

### Behavior
- intro appears before main app on first visit
- skip action remains available
- completed intro state is saved locally
- returning users can bypass intro automatically
- user can restart intro later from UI action if needed

## Personalization Rules

### Allowed Personalization
Intro answers may affect:
- welcome copy
- helper copy
- emphasis in UI guidance
- suggested way to approach the existing form
- tone of recommendation framing

### Disallowed Personalization
Intro answers must **not** affect:
- recommendation scoring
- backend model behavior
- ranking logic
- explanation math

### Example Outcomes
- “Hi, Naila. Let’s find majors that match how you learn.”
- “You already have a rough direction. Apti will help you compare it clearly.”
- “If you’re still unsure, start with your strongest subjects and interests. Apti will guide you step by step.”

## App Shell Redesign

### Brand Layer
- rename visible product identity to **Apti**
- create cleaner identity area in top shell
- keep branding calm and academic, not startup-hype or chatbot-like

### Main Experience
After intro completion, main product opens into redesigned recommendation workspace:
- clearer form hierarchy
- stronger top-level heading
- calmer spacing rhythm
- more intentional empty/loading/error states
- better visual continuity between intro and main journey

### Tone of Voice
Apti speaks in concise, supportive, non-judgmental language.
Every prompt should ask one thing only.
It should sound like a thoughtful advisor, not a generic AI assistant.

## State Model

### Client-Side Intro State
Store locally:
- whether intro is completed
- entered name
- selected goal
- selected confidence level

### Returning User Behavior
If intro state exists:
- skip intro by default
- show personalized copy in main experience
- allow manual restart/reset later

## Component Boundaries

Likely frontend areas involved:
- app shell / root layout
- intro/onboarding component
- main recommendation entry view
- personalized heading/subcopy logic
- local persistence helper for intro state
- updated visual tokens/styles for calm editorial direction

## Error Handling

- empty name input should show clear inline validation
- skipping intro should never block access to main app
- invalid saved intro state should fall back safely to default experience
- personalization failure should degrade to generic Apti copy without breaking flow

## Accessibility

- intro flow keyboard accessible
- clear focus states maintained in redesign
- visible progress indicators readable by all users
- motion remains subtle and should respect reduced-motion preference where implemented
- text hierarchy must remain readable on small screens

## Success Criteria

This chunk succeeds when:
- Apti branding replaces prior visible brand identity in main shell
- first-time user sees pre-home intro flow
- intro can be completed or skipped cleanly
- returning user behavior works from saved local state
- main app shows personalized copy using intro answers
- redesign clearly feels calmer, cleaner, and more editorial than current build
- no scoring logic changes are introduced

## Risks

### Risk 1: Intro feels like fake chatbot UI
Mitigation: keep structure card-based and guided, not message-thread based.

### Risk 2: Redesign becomes too minimal and loses guidance
Mitigation: preserve strong prompts, progress cues, and helper copy.

### Risk 3: Personalization feels shallow or repetitive
Mitigation: use concise conditional copy patterns tied to goal/confidence rather than excessive templating.

### Risk 4: Scope creep into bilingual and ML changes
Mitigation: enforce chunk boundary and defer those systems to later specs.

## Recommendation

Implement this chunk first before multilingual or ML improvements.
Reason: it improves brand clarity, trust, and first-run UX without touching higher-risk backend/model logic.
