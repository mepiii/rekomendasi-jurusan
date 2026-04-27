// @vitest-environment jsdom
// Purpose: Verify prodi-specific Apti intake payload and localized wizard scaffolding.
// Callers: Vitest frontend suite.
// Deps: Testing Library, RecommendationJourney component.
// API: Defines intake payload expectations for backend submission.
// Side effects: Renders DOM and triggers synthetic form events.
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import RecommendationJourney from './RecommendationJourney';

const copy = {
  journeyKicker: 'Apti intake',
  journeyTitle: 'Find your prodi',
  journeyHelper: 'Helper',
  steps: ['Track', 'Scores', 'Interests', 'Direction', 'Constraints', 'Expected', 'Avoid', 'Goal', 'Review', 'Submit'],
  track: 'Track',
  subjects: 'Subjects',
  selected: 'selected',
  interests: 'Interests',
  preferences: 'Preferences',
  profileReview: 'Profile review',
  averageScore: 'Average score',
  decisionSupport: 'Decision support',
  back: 'Back',
  continue: 'Continue',
  analyze: 'Analyze',
  analyzing: 'Analyzing',
  inputsError: 'Required'
};

describe('RecommendationJourney prodi intake', () => {
  afterEach(() => cleanup());

  it('submits prodi-specific fields with locale language', async () => {
    const onSubmit = vi.fn();
    render(<RecommendationJourney onSubmit={onSubmit} loading={false} locale="en" copy={copy} />);

    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    await waitFor(() => expect(screen.getByLabelText(/Pendidikan Agama S1/i)).toBeTruthy());
    screen.getAllByRole('spinbutton').forEach((input) => {
      fireEvent.change(input, { target: { value: '88' } });
    });
    ['Technology', 'Engineering', 'Data / AI'].forEach((name) => fireEvent.click(screen.getByRole('button', { name })));
    ['Numbers', 'Technical', 'Independent'].forEach((name) => fireEvent.click(screen.getByRole('button', { name })));

    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    for (const name of ['STEM-heavy classes', 'Computer Science', 'Software engineering', 'Technology builder', 'Jakarta only', 'Artificial Intelligence', 'Medicine', 'Build AI products']) {
      await waitFor(() => expect(screen.getByRole('textbox')).toBeTruthy());
      fireEvent.click(screen.getByRole('button', { name }));
      fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    }
    fireEvent.click(screen.getByRole('button', { name: /analyze/i }));

    expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({
      academic_context: { note: 'STEM-heavy classes' },
      subject_preferences: { preferred: ['Computer Science'] },
      interest_deep_dive: { note: 'Software engineering' },
      career_direction: { note: 'Technology builder' },
      constraints: { note: 'Prefer Jakarta only' },
      expected_prodi: 'Kecerdasan Artifisial',
      prodi_to_avoid: ['Kedokteran'],
      free_text_goal: 'Build AI products',
      language: 'en',
      scores: expect.objectContaining({ advanced_math: 88, general_math: 88 }),
      rapor: expect.objectContaining({
        kelas_10: expect.arrayContaining([expect.objectContaining({ semester: 1, subject: 'general_math', score: 88 })]),
        kelas_12: expect.arrayContaining([expect.objectContaining({ semester: 6, subject: 'advanced_math', score: 88 })])
      })
    }));
  }, 30000);
});
