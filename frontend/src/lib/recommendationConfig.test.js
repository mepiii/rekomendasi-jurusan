// Purpose: Validate dynamic Apti intake configuration.
// Callers: Vitest frontend contract suite.
// Deps: recommendationConfig.
// API: Tests subject labels and option breadth.
// Side effects: None.

import { describe, expect, it } from 'vitest';

import { buildInitialRaporScores, buildRaporPayload, expandedMajorOptions, explorationOptionSets, prodiIntakeSteps, subjectsForGrade, surveyModeOptions, targetSpecificOptionSets, trackConfig } from './recommendationConfig';

describe('recommendationConfig', () => {
  it('uses Matematika Lanjut for IPA advanced math', () => {
    expect(Object.fromEntries(trackConfig.IPA.requiredSubjects).advanced_math).toBe('Matematika Lanjut');
  });

  it('offers tagged exploration modes and broad major options', () => {
    const option = explorationOptionSets.academic_strength[0];

    expect(surveyModeOptions.map((item) => item.id)).toEqual(expect.arrayContaining(['mode_target', 'mode_zero']));
    expect(option).toEqual(expect.objectContaining({ id: expect.any(String), label_id: expect.any(String), label_en: expect.any(String), tags: expect.any(Array), cluster_tags: expect.any(Array), scoring_weight: expect.any(Number) }));
    expect(expandedMajorOptions.length).toBeGreaterThanOrEqual(100);
    expect(prodiIntakeSteps.find((step) => step.key === 'expected_prodi').required).toBe(false);
    expect(targetSpecificOptionSets['Teknik Informatika'].length).toBeGreaterThanOrEqual(8);
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
