# Apti Recommendation System V2 — Complete Redesign Spec

**Date:** 2026-05-06
**Status:** Draft
**Scope:** Monolithic spec, phased implementation

## 1. Problem Statement

Apti's current recommendation pipeline is biased toward school track and report card grades. Survey signals (interests, career direction, learning style, constraints, target/avoided majors) have weak influence on final ranking. The survey still uses textarea/free-text inputs for several pages, which produces unstructured data that is hard to score consistently.

### Current Pain Points

1. **Grade bias:** Subject grades dominate recommendation; two students with identical grades but opposite interests get similar results.
2. **Free-text survey:** Pages 3–10 use textarea input, making answers unstructured and inconsistent.
3. **No consistency scoring:** A student selecting "technology" across 5 pages gets the same boost as one selecting it once.
4. **No target/avoid analysis:** Target majors are not compared against top recommendations. Avoided majors are not penalized.
5. **Weak Kurikulum Merdeka support:** Elective selection is capped at 5; scoring doesn't adapt to mixed electives.
6. **Confusing result visualization:** Radar chart with mixed Indonesian/English labels is hard to read.
7. **Locale mixing:** Track labels, intro copy, and result labels mix languages.

## 2. Design Principles

1. **Schema-first:** Define all data contracts before building UI or scoring logic.
2. **Tag-driven scoring:** Every survey option maps to canonical tags. Scoring operates on tags, not raw strings.
3. **Balanced formula:** Academic fit matters but cannot dominate. Survey signals must strongly influence results.
4. **Phased safety:** Each phase is independently testable. No big-bang rewrite.
5. **Preserve visual identity:** Keep dark premium minimal style. Change logic first.
6. **Locale-complete:** Every user-facing string must have both EN and ID variants.

## 3. Data Schema

### 3.1 Subject Normalization Schema

Canonical subject keys used across all layers (UI display names are locale-aware, backend uses keys only).

```typescript
type SubjectKey =
  | 'religion' | 'civics' | 'indonesian' | 'english'
  | 'math_general' | 'math_advanced' | 'physical_education' | 'arts'
  | 'physics' | 'chemistry' | 'biology'
  | 'informatics' | 'economics' | 'sociology' | 'geography' | 'history'
  | 'anthropology' | 'indonesian_literature' | 'english_literature'
  | 'english_advanced' | 'foreign_language' | 'visual_arts' | 'design'
  | 'craft' | 'entrepreneurship';

// Alias map for legacy/variant names → canonical key
const SUBJECT_ALIASES: Record<string, SubjectKey> = {
  'Matematika Umum': 'math_general',
  'Matematika Dasar': 'math_general',
  'Matematika': 'math_general',
  'Matematika Lanjut': 'math_advanced',
  'Matematika Tingkat Lanjut': 'math_advanced',
  'Pendidikan Agama': 'religion',
  'PPKn': 'civics',
  'Bahasa Indonesia': 'indonesian',
  'Bahasa Inggris': 'english',
  'Bahasa Inggris Tingkat Lanjut': 'english_advanced',
  'Fisika': 'physics',
  'Kimia': 'chemistry',
  'Biologi': 'biology',
  'Informatika': 'informatics',
  'Ekonomi': 'economics',
  'Sosiologi': 'sociology',
  'Geografi': 'geography',
  'Sejarah': 'history',
  'Antropologi': 'anthropology',
  'Sastra Indonesia': 'indonesian_literature',
  'Sastra Inggris': 'english_literature',
  'Bahasa Asing': 'foreign_language',
  'Seni': 'arts',
  'Seni Rupa': 'visual_arts',
  'Desain': 'design',
  'PJOK': 'physical_education',
  'Prakarya': 'craft',
  'Kewirausahaan': 'entrepreneurship',
  'Prakarya / Kewirausahaan': 'craft',
};
```

**Rule:** `math_general` and `math_advanced` are NEVER merged. `math_advanced` strongly supports STEM/engineering/data-heavy majors.

### 3.2 Curriculum Subject Schema

```typescript
interface CurriculumTrack {
  key: 'IPA' | 'IPS' | 'Bahasa' | 'Merdeka';
  label: { en: string; id: string };
  curriculumType: string;
  generalSubjects: SubjectKey[];       // shared across all tracks
  specializationSubjects: SubjectKey[]; // track-specific required
  optionalSubjects: SubjectKey[];       // track optional
  electiveSubjects?: SubjectKey[];      // Merdeka only
}
```

Kurikulum Merdeka rules:
- Recommended: 2–8 elective subjects (not hard-capped at 5)
- Fewer electives → reduce confidence slightly
- More electives → normalize scoring (no overboost)

### 3.3 Survey Option Schema

```typescript
interface SurveyOption {
  id: string;                    // unique stable ID, e.g. "interest_technology"
  label: { en: string; id: string };
  tags: string[];                // canonical scoring tags
  category: SurveyCategory;     // which survey page
}

type SurveyCategory =
  | 'academic_preference'       // page 4
  | 'subject_liked'             // page 5a
  | 'subject_avoided'           // page 5b
  | 'interest_general'          // page 6
  | 'interest_deep'             // page 7
  | 'problem_to_solve'          // page 8
  | 'learning_style'            // page 9
  | 'work_style'                // page 10
  | 'career_direction'          // page 11
  | 'future_goal'               // page 12
  | 'constraint'                // page 13
  | 'target_major'              // page 14
  | 'avoided_major';            // page 15

interface SurveyPage {
  key: SurveyCategory;
  label: { en: string; id: string };
  question: { en: string; id: string };
  options: SurveyOption[];
  maxSelections: number;
  selectionMode: 'multi';       // all pages are multi-select
}
```

Max selection limits per page:
| Page | Max |
|------|-----|
| academic_preference | 8 |
| subject_liked | 6 |
| subject_avoided | 6 |
| interest_general | 8 |
| interest_deep | 8 |
| problem_to_solve | 6 |
| learning_style | 6 |
| work_style | 6 |
| career_direction | 6 |
| future_goal | 6 |
| constraint | 6 |
| target_major | 3 |
| avoided_major | 6 |

### 3.4 Scoring Tag Schema

Tags are the bridge between survey options and major metadata.

```typescript
// Tag categories
type TagCategory =
  | 'domain'          // technology, health, business, law, etc.
  | 'skill'           // coding, math_heavy, lab_work, writing, etc.
  | 'work_env'        // remote, field, office, lab, etc.
  | 'career_trait'    // stable, flexible, high_salary, etc.
  | 'learning'        // practical, theoretical, project_based, etc.
  | 'avoid';          // avoid_coding, avoid_math, avoid_lab, etc.

interface ScoringTag {
  id: string;               // e.g. "technology", "avoid_coding"
  category: TagCategory;
  weight: number;            // default 1.0, some tags weighted more
}
```

Tag normalization rules:
- When user selects N options on a page with max M, each tag's contribution = `1.0 / max(N, 1)` (diminishing returns)
- Consistency bonus: same tag appearing across 3+ pages → weight × 1.5; 2 pages → weight × 1.2; 1 page → weight × 1.0

### 3.5 Major Metadata Schema

```typescript
interface MajorProfile {
  id: string;                          // e.g. "P0120"
  name_id: string;                     // "Teknik Informatika"
  name_en: string;                     // "Informatics Engineering"
  faculty_group: string;               // "Komputer"
  science_group: string;               // "Ilmu Formal"

  // Academic dimension
  subject_weights: Record<SubjectKey, number>;  // 0.0–1.0, must sum to ~1.0
  required_subjects: SubjectKey[];
  optional_subjects: SubjectKey[];

  // Survey dimensions (tags this major matches)
  interest_tags: string[];
  career_tags: string[];
  learning_style_tags: string[];
  goal_tags: string[];
  constraint_tags: string[];
  avoid_tags: string[];                // tags that PENALIZE this major

  // Career and alternatives
  related_careers_id: string[];
  related_careers_en: string[];
  alternative_majors: string[];        // IDs of similar majors

  // Guidance
  skill_gaps: string[];
  risk_factors: string[];
  recommended_for: string[];
  not_recommended_for: string[];

  // Explanation templates
  explanation_templates: {
    strength: { en: string; id: string };
    tradeoff: { en: string; id: string };
  };
}
```

### 3.6 Scoring Output Schema

```typescript
interface FitBreakdown {
  academic_fit: number;        // 0–100
  interest_fit: number;        // 0–100
  career_fit: number;          // 0–100
  learning_style_fit: number;  // 0–100
  goal_fit: number;            // 0–100
  constraint_fit: number;      // 0–100
  target_alignment: number;    // 0–100
  avoid_penalty: number;       // 0–100 (subtracted)
}

interface RecommendationResult {
  rank: number;
  major_id: string;
  major_name: { en: string; id: string };
  final_score: number;          // 0–100
  confidence: ConfidenceLevel;
  fit_breakdown: FitBreakdown;
  key_strengths: string[];      // top 3 tag-based reasons
  risks: string[];              // top 2 tradeoffs
  career_paths: string[];
  alternative_majors: string[];
  skill_gaps: string[];
  explanation: { en: string; id: string };
  is_target: boolean;
  is_avoided: boolean;
}

interface TargetAnalysis {
  major_id: string;
  major_name: { en: string; id: string };
  score: number;
  rank_among_all: number;
  fits_well: boolean;
  conflict_reasons: string[];
  comparison_vs_top: {
    top_major: string;
    score_gap: number;
    stronger_dimensions: string[];
    weaker_dimensions: string[];
  };
}
```

### 3.7 Confidence Schema

```typescript
type ConfidenceLevel = 'high' | 'medium' | 'low';

interface ConfidenceReport {
  level: ConfidenceLevel;
  score: number;               // 0–100
  factors: {
    grades_filled: number;     // % of expected grades entered
    survey_pages_completed: number;  // count of pages with selections
    grade_survey_consistency: number; // 0–1 correlation
    interest_career_consistency: number;
    target_conflict: boolean;
    avoided_conflict: boolean;
    missing_important_subjects: SubjectKey[];
    score_gap_top2: number;    // gap between #1 and #2
    all_high_grades: boolean;  // all grades > 85
  };
  explanation: { en: string; id: string };
}
```

### 3.8 Chart Data Schema

```typescript
interface ChartData {
  fit_breakdown: {
    labels: string[];    // ["Academic", "Interest", "Career", ...]
    values: number[];    // [85, 72, 90, ...]
  };
  subject_contribution: {
    labels: string[];    // subject names in current locale
    values: number[];    // contribution scores
    major_name: string;
  };
  survey_signals: {
    labels: string[];    // top signal tags in current locale
    values: number[];    // signal strengths
  };
  major_comparison: {
    majors: string[];    // major names
    dimensions: string[];
    values: number[][];  // [major_index][dimension_index]
  };
}
```

## 4. Scoring Formula

### 4.1 Final Score Computation

```
Final Score =
  Academic Fit × 0.30
+ Interest Fit × 0.25
+ Career Fit  × 0.20
+ Learning Style Fit × 0.10
+ Goal Fit × 0.07
+ Constraint Fit × 0.05
+ Target Alignment × 0.03
- Avoid Penalty
```

### 4.2 Academic Fit

```
academic_fit = Σ (normalized_grade[subject] × major.subject_weights[subject])
```

- `normalized_grade` = average across 6 semesters, scaled 0–100
- Missing optional subjects → use 0 weight contribution (not zero grade)
- All-high-grades detection: if stddev of all grades < 5 and mean > 85, reduce academic weight from 0.30 to 0.20 and redistribute to interest (0.30) and career (0.25)

### 4.3 Interest Fit

```
interest_fit = jaccard_weighted(user_interest_tags, major.interest_tags) × consistency_bonus
```

- `jaccard_weighted` = weighted overlap between user tags and major tags
- `consistency_bonus` = 1.0 + 0.15 × (pages_with_matching_tags - 1), capped at 1.5

### 4.4 Career Fit

```
career_fit = jaccard_weighted(user_career_tags, major.career_tags) × consistency_bonus
```

### 4.5 Learning Style Fit

```
learning_style_fit = jaccard_weighted(user_learning_tags, major.learning_style_tags)
```

### 4.6 Goal Fit

```
goal_fit = jaccard_weighted(user_goal_tags, major.goal_tags)
```

### 4.7 Constraint Fit

```
constraint_fit = Σ (tag ∈ user_constraints ∩ major.constraint_tags) / max(|user_constraints|, 1)
```

### 4.8 Target Alignment

```
target_alignment = 100 if major is in user's target list, else 0
```

### 4.9 Avoid Penalty

```
avoid_penalty = 15 if major is in user's avoid list
              + Σ 3 × (tag ∈ user_avoid_tags ∩ major.avoid_tags) / max(|major.avoid_tags|, 1)
```

Avoided major still appears in target analysis section but is removed from top recommendations unless score is extremely strong (>85 after penalty).

### 4.10 Multi-Select Normalization

Per-page normalization:
```
tag_weight = base_weight / sqrt(num_selections_on_page)
```

Cross-page consistency:
```
consistency_multiplier(tag) =
  1.5 if tag appears on 3+ pages
  1.2 if tag appears on 2 pages
  1.0 if tag appears on 1 page
```

## 5. Survey Flow

### 5.1 Page Sequence

| # | Key | Title (EN) | Title (ID) | Type |
|---|-----|-----------|-----------|------|
| 1 | track | Track / Curriculum | Jalur / Kurikulum | single-select |
| 2 | grades | Subjects & Grades | Mapel dan Nilai | grade input |
| 3 | electives | Merdeka Electives | Pilihan Kurmer | multi-select (Merdeka only) |
| 4 | academic_preference | Academic Context | Preferensi Akademik | multi-select max 8 |
| 5 | subject_liked_avoided | Subjects Liked & Avoided | Mapel Disukai & Dihindari | multi-select max 6+6 |
| 6 | interest_general | General Interests | Minat Umum | multi-select max 8 |
| 7 | interest_deep | Deep Interests | Minat Mendalam | multi-select max 8 |
| 8 | problem_to_solve | Problems to Solve | Masalah yang Ingin Dipecahkan | multi-select max 6 |
| 9 | learning_style | Learning Style | Gaya Belajar | multi-select max 6 |
| 10 | work_style | Work Style | Gaya Kerja | multi-select max 6 |
| 11 | career_direction | Career Direction | Arah Karier | multi-select max 6 |
| 12 | future_goal | Future Goals | Tujuan Masa Depan | multi-select max 6 |
| 13 | constraint | Constraints | Batasan | multi-select max 6 |
| 14 | target_major | Target Majors | Target Jurusan | multi-select max 3 |
| 15 | avoided_major | Avoided Majors | Jurusan Dihindari | multi-select max 6 |
| 16 | review | Review & Submit | Tinjau & Kirim | summary |

### 5.2 Option Counts per Page

All options as specified in the user's requirements document (sections 5–17). Each option has:
- Unique stable ID
- Bilingual label `{en, id}`
- Array of scoring tags

Total option counts:
- Academic preference: 29 options
- Subject liked: 26 options
- Subject avoided: 22 options
- Interest general: 44 options
- Interest deep: 56 options
- Problems to solve: 25 options
- Learning style: 26 options
- Work style: 34 options
- Career direction: 62 options
- Future goals: 30 options
- Constraints: 30 options
- Avoided things: 33 options
- Target majors: 53 options
- Avoided majors: 53 options (same list)

### 5.3 No Free Text

**Zero textarea/input[type=text] elements on pages 4–15.** All survey data is structured option selections only.

## 6. Result Page Structure

### 6.1 Sections (in order)

1. **Profile Summary Card** — strongest subjects, strongest tags, confidence, missing data warnings
2. **Top Recommendations** (3–5 cards) — each with:
   - Rank badge
   - Major name (bilingual)
   - Final score + confidence
   - Short explanation (1–2 sentences)
   - Collapsible "Kenapa jurusan ini?" with:
     - Fit breakdown bar chart
     - Key strengths
     - Risks/tradeoffs
     - Career paths
     - Alternative majors
     - Skill gaps
3. **Target Major Analysis** (if targets selected) — comparison vs top pick, conflict explanation
4. **Avoided Major Explanation** — why each avoided major was penalized or still appeared
5. **Comparison Table** — top 3 + target majors across all fit dimensions
6. **Charts Section:**
   - Fit Breakdown Bar Chart
   - Subject Contribution Chart
   - Survey Signal Chart
   - Major Comparison Chart
7. **Next Steps** — actionable suggestions
8. **Feedback Section** — "Does this feel right?" quick survey

### 6.2 Chart Requirements

- No raw radar chart with mixed language labels
- Horizontal bar charts for fit breakdown
- Grouped bar chart for major comparison
- All chart labels follow current locale
- Responsive on mobile

## 7. Files to Change

### Phase 1 — Foundation Schema
| File | Action | Description |
|------|--------|-------------|
| `backend/app/schemas_v2.py` | CREATE | New Pydantic models for V2 request/response |
| `backend/app/subject_normalization.py` | CREATE | Subject alias map, normalization functions |
| `backend/app/scoring_tags.py` | CREATE | Tag definitions, categories, consistency logic |
| `frontend/src/lib/schemas.ts` (or .js) | CREATE | TypeScript/JS type definitions mirroring backend |

### Phase 2 — Major Dataset
| File | Action | Description |
|------|--------|-------------|
| `backend/ml/data/catalog/majors_v2.json` | CREATE | Structured major profiles (30+ MVP majors) |
| `backend/app/services/major_catalog_service.py` | CREATE | Load, query, validate major profiles |
| `backend/tests/test_major_catalog.py` | CREATE | Validate major dataset integrity |

### Phase 3 — Survey Engine
| File | Action | Description |
|------|--------|-------------|
| `frontend/src/lib/surveyOptions.js` | CREATE | All survey options with tags, organized by page |
| `frontend/src/lib/recommendationConfig.js` | MODIFY | Remove prodiIntakeSteps textarea config; update track config |
| `frontend/src/components/features/RecommendationJourney.jsx` | MODIFY | Replace ProdiTextStep with chip-only SurveyChipStep; expand from 11 to 16 steps |
| `frontend/src/components/features/SurveyChipStep.jsx` | CREATE | Reusable multi-select chip page component |

### Phase 4 — Scoring Engine
| File | Action | Description |
|------|--------|-------------|
| `backend/app/services/scoring_engine.py` | CREATE | New balanced scoring with tag-based fit computation |
| `backend/app/services/ml_service.py` | MODIFY | Integrate scoring_engine; keep ML model as one signal |
| `backend/app/services/confidence_service.py` | CREATE | Confidence calculation |
| `backend/app/recommendation_config.py` | MODIFY | Update weights, add V2 config |
| `backend/tests/test_scoring_engine.py` | CREATE | Scoring formula tests |

### Phase 5 — Result Page
| File | Action | Description |
|------|--------|-------------|
| `frontend/src/components/features/ResultSectionV2.jsx` | CREATE | New sectioned result layout |
| `frontend/src/components/features/FitBreakdownChart.jsx` | CREATE | Horizontal bar chart |
| `frontend/src/components/features/ComparisonTable.jsx` | CREATE | Major comparison table |
| `frontend/src/components/features/TargetAnalysis.jsx` | CREATE | Target major analysis section |
| `frontend/src/components/features/SkillGapSection.jsx` | CREATE | Skill gap roadmap |

### Phase 6 — Tests
| File | Action | Description |
|------|--------|-------------|
| `frontend/src/components/features/RecommendationJourney.test.jsx` | MODIFY | Add no-textarea, tag-mapping tests |
| `backend/tests/test_scoring_engine.py` | EXTEND | Survey influence, avoid penalty, all-high tests |
| `backend/tests/test_subject_normalization.py` | CREATE | Alias mapping tests |
| `frontend/src/lib/recommendationConfig.test.js` | MODIFY | Kurmer elective tests |

## 8. Implementation Phases

### Phase 1: Foundation Schema (Est. 1 session)
1. Create `subject_normalization.py` with alias map + normalize function
2. Create `scoring_tags.py` with tag registry
3. Create `schemas_v2.py` with new Pydantic models
4. Create frontend type definitions
5. Tests: normalization aliases, schema validation

### Phase 2: Major Dataset (Est. 1–2 sessions)
1. Create `majors_v2.json` starting with 30 critical Indonesian majors
2. Create `major_catalog_service.py` for loading/querying
3. Validate all majors have required fields + valid tags
4. Tests: dataset integrity, tag coverage

### Phase 3: Survey Engine (Est. 2 sessions)
1. Create `surveyOptions.js` with all options + tags
2. Create `SurveyChipStep.jsx` component
3. Refactor `RecommendationJourney.jsx` to use chip pages
4. Remove all textarea elements from survey
5. Update payload builder for V2 format
6. Tests: no textarea, max-selection limits, tag mapping

### Phase 4: Scoring Engine (Est. 2 sessions)
1. Create `scoring_engine.py` with balanced formula
2. Create `confidence_service.py`
3. Wire into `ml_service.py` (keep existing ML model as academic signal)
4. Implement consistency scoring, normalization, target/avoid logic
5. Tests: formula weights, survey influence, edge cases

### Phase 5: Result Page (Est. 2 sessions)
1. Create sectioned result layout
2. Create chart components (bar charts, comparison table)
3. Create target analysis + avoided explanation
4. Wire to V2 response schema
5. Tests: locale labels, section presence, chart data

### Phase 6: Integration Tests (Est. 1 session)
1. End-to-end test: survey → scoring → result
2. Locale consistency tests
3. Edge case tests (all-high, empty survey, conflicting signals)

## 9. Migration Strategy

- V2 endpoint lives alongside V1 initially (`/api/predict/v2`)
- Frontend feature-flags which flow to use
- Once V2 is stable, deprecate V1
- No data migration needed (stateless predictions)

## 10. ML Model Integration

The existing ML model (likely XGBoost/gradient-boosted classifier trained on synthetic data) remains as a signal within `academic_fit`. The new scoring engine wraps it:

1. **Academic Fit** uses the existing model's subject-weight logic as one component, plus the new `subject_weights` from major metadata.
2. **LLMReviewService** (Gemini-based explanation) is kept for the V1 path during migration. V2 generates explanations from structured data (fit breakdown + tag matches) without LLM dependency.
3. **Hybrid mode:** During transition, the endpoint can serve V1 (ML-only) or V2 (balanced formula) based on a request flag.

### Weighted Jaccard Formula

```
jaccard_weighted(user_tags, major_tags) =
  Σ (tag ∈ user_tags ∩ major_tags) × tag_weight
  ──────────────────────────────────────────────
  Σ (tag ∈ user_tags ∪ major_tags) × tag_weight
```

Where `tag_weight` incorporates per-page normalization and cross-page consistency multiplier.

## 11. Out of Scope (Future)

- PDF export
- Save/load progress (localStorage persistence exists, extend later)
- Debug mode
- Feedback-driven ML retraining
- 100+ major coverage (start with 30 MVP)
- Campus-specific curriculum comparison
