// @vitest-environment jsdom
// Purpose: Verify Apti intro orchestration and confidence-aware helper copy.
// Callers: Vitest frontend suite.
// Deps: Testing Library, App component, browser localStorage.
// API: Defines App personalization integration expectations.
// Side effects: Reads and writes window.localStorage during tests.
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';

vi.mock('./components/features/RecommendationJourney', () => ({
  default: ({ helperCopy }) => <div data-testid="recommendation-journey">{helperCopy || 'journey'}</div>
}));

vi.mock('./components/features/ResultSectionAdvanced', () => ({
  default: () => <div data-testid="result-section">Result section</div>
}));

vi.mock('./hooks/useExplainabilityPoll', () => ({
  default: () => ({ ready: false, explanations: [], stop: vi.fn() })
}));

vi.mock('./lib/api', () => ({
  pingHealth: vi.fn(),
  predict: vi.fn(),
  submitFeedback: vi.fn()
}));

describe('App intro orchestration', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  afterEach(() => {
    cleanup();
  });

  it('shows intro flow for first-time users', () => {
    render(<App />);

    expect(screen.getByText(/welcome to apti/i)).toBeTruthy();
    expect(screen.getByLabelText(/your name/i)).toBeTruthy();
  });

  it('shows strongest-subjects helper copy for very-unsure returning users', () => {
    window.localStorage.setItem(
      'apti-intro-state',
      JSON.stringify({
        completed: true,
        name: 'Raka',
        goal: 'understand-strengths',
        confidence: 'very-unsure'
      })
    );

    render(<App />);

    expect(screen.getByText(/welcome back, raka/i)).toBeTruthy();
    expect(screen.getByTestId('recommendation-journey').textContent).toMatch(
      /start with your strongest subjects and interests, then narrow from there/i
    );
  });

  it('uses sensible default helper copy when intro confidence is missing', () => {
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

    expect(screen.getByTestId('recommendation-journey').textContent).toMatch(
      /share your latest scores and interests to get a grounded shortlist of majors/i
    );
  });

  it('allows restarting intro from main shell', () => {
    window.localStorage.setItem(
      'apti-intro-state',
      JSON.stringify({
        completed: true,
        name: 'Naila',
        goal: 'find-fit',
        confidence: 'very-unsure'
      })
    );

    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /restart intro/i }));

    expect(screen.getByText(/welcome to apti/i)).toBeTruthy();
    expect(window.localStorage.getItem('apti-intro-state')).toBeNull();
  });

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

    expect(screen.getByRole('button', { name: /dark mode/i })).toBeTruthy();
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

    expect(screen.getByTestId('apti-shell').getAttribute('data-theme')).toBe('dark');
    expect(screen.getByRole('button', { name: /light mode/i })).toBeTruthy();
  });

  it('renders shell with theme-aware root attribute for CSS token styling', () => {
    window.localStorage.setItem(
      'apti-intro-state',
      JSON.stringify({ completed: true, name: 'Raka', goal: 'find-fit', confidence: '' })
    );

    render(<App />);

    expect(screen.getByTestId('apti-shell').getAttribute('data-theme')).toBe('light');
  });
});
