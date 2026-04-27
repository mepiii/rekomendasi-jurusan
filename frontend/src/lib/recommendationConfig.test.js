// Purpose: Validate dynamic Apti intake configuration.
// Callers: Vitest frontend contract suite.
// Deps: recommendationConfig.
// API: Tests subject labels and option breadth.
// Side effects: None.

import { describe, expect, it } from 'vitest';

import { prodiIntakeSteps, trackConfig } from './recommendationConfig';

describe('recommendationConfig', () => {
  it('uses Matematika Lanjut for IPA advanced math', () => {
    expect(Object.fromEntries(trackConfig.IPA.requiredSubjects).advanced_math).toBe('Matematika Lanjut');
  });

  it('offers prodi options beyond informatics', () => {
    const optionsFor = (key) => prodiIntakeSteps.find((step) => step.key === key)?.options.map((option) => option.value) || [];

    expect(optionsFor('subject_preferences')).toEqual(expect.arrayContaining(['Law', 'Education', 'Environment', 'Language and literature']));
    expect(optionsFor('expected_prodi')).toEqual(expect.arrayContaining(['Hukum', 'Farmasi', 'Ilmu Komunikasi', 'Ilmu Lingkungan']));
  });
});
