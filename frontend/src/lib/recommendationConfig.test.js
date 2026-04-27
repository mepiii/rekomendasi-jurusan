// Purpose: Validate dynamic Apti intake configuration.
// Callers: Vitest frontend contract suite.
// Deps: recommendationConfig.
// API: Tests subject labels and option breadth.
// Side effects: None.

import { describe, expect, it } from 'vitest';

import { buildInitialRaporScores, buildRaporPayload, prodiIntakeSteps, subjectsForGrade, trackConfig } from './recommendationConfig';

describe('recommendationConfig', () => {
  it('uses Matematika Lanjut for IPA advanced math', () => {
    expect(Object.fromEntries(trackConfig.IPA.requiredSubjects).advanced_math).toBe('Matematika Lanjut');
  });

  it('offers prodi options beyond informatics', () => {
    const optionsFor = (key) => prodiIntakeSteps.find((step) => step.key === key)?.options.map((option) => option.value) || [];

    expect(optionsFor('subject_preferences')).toEqual(expect.arrayContaining(['Law', 'Education', 'Environment', 'Language and literature']));
    expect(optionsFor('expected_prodi')).toEqual(expect.arrayContaining(['Hukum', 'Farmasi', 'Ilmu Komunikasi', 'Ilmu Lingkungan']));
  });

  it('models kelas 10 as common and kelas 11-12 as track-specific rapor scores', () => {
    expect(subjectsForGrade('IPA', 10).map(([key]) => key)).toContain('general_math');
    expect(subjectsForGrade('IPA', 10).map(([key]) => key)).not.toContain('advanced_math');
    expect(subjectsForGrade('IPA', 11).map(([key]) => key)).toContain('advanced_math');

    const initial = buildInitialRaporScores('IPA');
    expect(initial).toHaveProperty('s1_general_math');
    expect(initial).toHaveProperty('s6_advanced_math');
  });

  it('builds backend rapor payload from semester score keys', () => {
    const payload = buildRaporPayload({ s1_general_math: '80', s2_general_math: '84', s5_advanced_math: '90', s6_advanced_math: '94' }, 'IPA');

    expect(payload.kelas_10).toEqual(expect.arrayContaining([{ semester: 1, subject: 'general_math', score: 80 }]));
    expect(payload.kelas_12).toEqual(expect.arrayContaining([{ semester: 6, subject: 'advanced_math', score: 94 }]));
    expect(payload.sma_track).toBe('IPA');
  });
});
