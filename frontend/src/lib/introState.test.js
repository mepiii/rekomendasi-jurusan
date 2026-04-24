// @vitest-environment jsdom
// Purpose: Verify shared intro-state helpers centralize localStorage parsing and helper-copy selection.
// Callers: Vitest frontend suite.
// Deps: Vitest assertions, browser localStorage, introState helpers.
// API: Defines intro-state helper expectations.
// Side effects: Reads and writes window.localStorage during tests.
import { beforeEach, describe, expect, it } from 'vitest';
import { getHelperCopy, loadIntroState } from './introState';

describe('introState helpers', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('returns parsed intro state from localStorage', () => {
    const storedState = {
      completed: true,
      name: 'Raka',
      goal: 'find-fit',
      confidence: 'somewhat-unsure'
    };

    window.localStorage.setItem('apti-intro-state', JSON.stringify(storedState));

    expect(loadIntroState()).toEqual(storedState);
  });

  it('returns default helper copy when confidence is missing', () => {
    window.localStorage.setItem(
      'apti-intro-state',
      JSON.stringify({ completed: true, confidence: '' })
    );

    expect(getHelperCopy()).toBe(
      'Share your latest scores and interests to get a grounded shortlist of majors.'
    );
  });
});
