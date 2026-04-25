// @vitest-environment jsdom
// Purpose: Verify advanced result card renders prodi v2 metadata safely.
// Callers: Vitest frontend suite.
// Deps: Testing Library, ResultCardAdvanced component.
// API: Defines rendering expectations for nested supporting-subject payloads.
// Side effects: Renders DOM.
import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import ResultCardAdvanced from './ResultCardAdvanced';

vi.mock('recharts', () => ({
  PolarAngleAxis: () => null,
  PolarGrid: () => null,
  PolarRadiusAxis: () => null,
  Radar: () => null,
  RadarChart: ({ children }) => <div>{children}</div>,
  ResponsiveContainer: ({ children }) => <div>{children}</div>,
  Tooltip: () => null
}));

const copy = {
  alternateMajors: 'Alternatives',
  careerPaths: 'Careers',
  confidence: 'Confidence',
  fallback: 'Fallback',
  matchLevel: 'Match',
  notes: 'Notes',
  strengths: 'Strengths',
  topRecommendation: 'Top recommendation',
  tradeoffs: 'Tradeoffs',
  whyThis: 'Why this?'
};

describe('ResultCardAdvanced', () => {
  beforeAll(() => {
    globalThis.IntersectionObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    };
  });

  afterEach(() => cleanup());

  it('renders nested supporting subjects without crashing', () => {
    render(
      <ResultCardAdvanced
        recommendation={{
          rank: 1,
          major: 'Kecerdasan Artifisial',
          suitability_score: 83,
          match_level: 'Good match',
          explanation: ['Strong math fit.'],
          confidence_label: 'High',
          fit_summary: ['Komputer'],
          strength_signals: ['advanced_math'],
          tradeoffs: ['Compare curriculum'],
          career_paths: ['AI Engineer'],
          alternative_majors: ['Teknik Informatika'],
          supporting_subjects: {
            k13_ipa: {
              raw: 'Matematika dari kelompok peminatan MIPA',
              subjects: [{ raw: 'Matematika dari kelompok peminatan MIPA', key: 'mathematics' }]
            },
            kurikulum_merdeka: {
              raw: 'Matematika Tingkat Lanjut',
              subjects: [{ raw: 'Matematika Tingkat Lanjut', key: 'mathematics_advanced' }]
            }
          },
          why_specific: ['Kecocokan akademik kuat'],
          skill_gaps: ['Etika AI'],
          user_scores: { advanced_math: 93 },
          major_requirements: { advanced_math: 76.5 }
        }}
        copy={copy}
        locale="en"
        highlight
      />
    );

    expect(screen.getByText('Kecerdasan Artifisial')).toBeTruthy();
    expect(screen.getAllByText('Matematika Tingkat Lanjut').length).toBeGreaterThan(0);
  });
});
