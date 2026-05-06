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

  it('shows English curriculum track labels in English locale', async () => {
    const onSubmit = vi.fn();
    render(<RecommendationJourney onSubmit={onSubmit} loading={false} locale="en" copy={copy} />);

    fireEvent.click(screen.getByRole('button', { name: /continue/i }));

    await waitFor(() => expect(screen.getByRole('button', { name: /Science/ })).toBeTruthy());
    expect(screen.getByRole('button', { name: /Social/ })).toBeTruthy();
    expect(screen.getByRole('button', { name: /Language/ })).toBeTruthy();
    expect(screen.getByRole('button', { name: /Independent Curriculum/ })).toBeTruthy();
    expect(screen.queryByRole('button', { name: /Kurikulum Merdeka/ })).toBeNull();
  });

  it('renders prodi intake without free-text fields', async () => {
    const onSubmit = vi.fn();
    render(<RecommendationJourney onSubmit={onSubmit} loading={false} locale="en" copy={copy} />);

    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Science/ })).toBeTruthy());
    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    await waitFor(() => expect(screen.getByLabelText(/Pendidikan Agama S1/i)).toBeTruthy());
    screen.getAllByRole('spinbutton').forEach((input) => fireEvent.change(input, { target: { value: '88' } }));
    ['Technology', 'Engineering', 'Data / AI'].forEach((name) => fireEvent.click(screen.getByRole('button', { name })));
    ['Numbers', 'Technical', 'Independent'].forEach((name) => fireEvent.click(screen.getByRole('button', { name })));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Data / AI' }).getAttribute('aria-pressed')).toBe('true'));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Independent' }).getAttribute('aria-pressed')).toBe('true'));

    fireEvent.click(screen.getByRole('button', { name: /continue/i }));

    await waitFor(() => expect(screen.getByRole('button', { name: 'Strong in mathematics' })).toBeTruthy());
    expect(screen.queryByRole('textbox')).toBeNull();
  });

  it('keeps target prodi optional for no-target exploration', async () => {
    const onSubmit = vi.fn();
    render(<RecommendationJourney onSubmit={onSubmit} loading={false} locale="en" copy={copy} />);

    expect(screen.getByRole('button', { name: 'I want Apti to recommend from zero' })).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Science/ })).toBeTruthy());
    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    await waitFor(() => expect(screen.getByLabelText(/Pendidikan Agama S1/i)).toBeTruthy());
    screen.getAllByRole('spinbutton').forEach((input) => fireEvent.change(input, { target: { value: '88' } }));
    ['Technology', 'Engineering', 'Data / AI'].forEach((name) => fireEvent.click(screen.getByRole('button', { name })));
    ['Numbers', 'Technical', 'Independent'].forEach((name) => fireEvent.click(screen.getByRole('button', { name })));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Data / AI' }).getAttribute('aria-pressed')).toBe('true'));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Independent' }).getAttribute('aria-pressed')).toBe('true'));

    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Strong in mathematics' })).toBeTruthy());
    expect(screen.queryByRole('button', { name: 'Artificial Intelligence' })).toBeNull();
  });

  it('shows target picker only for target mode', async () => {
    const onSubmit = vi.fn();
    render(<RecommendationJourney onSubmit={onSubmit} loading={false} locale="en" copy={copy} />);

    fireEvent.click(screen.getByRole('button', { name: 'I already have target majors' }));
    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Science/ })).toBeTruthy());
    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    await waitFor(() => expect(screen.getByLabelText(/Pendidikan Agama S1/i)).toBeTruthy());
    screen.getAllByRole('spinbutton').forEach((input) => fireEvent.change(input, { target: { value: '88' } }));
    ['Technology', 'Engineering', 'Data / AI'].forEach((name) => fireEvent.click(screen.getByRole('button', { name })));
    ['Numbers', 'Technical', 'Independent'].forEach((name) => fireEvent.click(screen.getByRole('button', { name })));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Data / AI' }).getAttribute('aria-pressed')).toBe('true'));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Independent' }).getAttribute('aria-pressed')).toBe('true'));

    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    for (const name of ['Strong in mathematics', 'General Math', 'Heavy mathematics', 'Software engineering', 'Building apps', 'Technology builder', 'High salary', 'Jakarta only']) {
      await waitFor(() => expect(screen.getByRole('button', { name })).toBeTruthy());
      fireEvent.click(screen.getByRole('button', { name }));
      fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    }
    await waitFor(() => expect(screen.getByRole('button', { name: 'Kecerdasan Artifisial' })).toBeTruthy());
  });

  it('submits prodi-specific fields with locale language', async () => {
    const onSubmit = vi.fn();
    render(<RecommendationJourney onSubmit={onSubmit} loading={false} locale="en" copy={copy} />);

    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Science/ })).toBeTruthy());
    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    await waitFor(() => expect(screen.getByLabelText(/Pendidikan Agama S1/i)).toBeTruthy());
    screen.getAllByRole('spinbutton').forEach((input) => {
      fireEvent.change(input, { target: { value: '88' } });
    });
    ['Technology', 'Engineering', 'Data / AI'].forEach((name) => fireEvent.click(screen.getByRole('button', { name })));
    for (const name of ['Numbers', 'Technical', 'Independent']) {
      await waitFor(() => expect(screen.getByRole('button', { name })).toBeTruthy());
      fireEvent.click(screen.getByRole('button', { name }));
    }
    await waitFor(() => expect(screen.getByRole('button', { name: 'Data / AI' }).getAttribute('aria-pressed')).toBe('true'));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Independent' }).getAttribute('aria-pressed')).toBe('true'));

    fireEvent.click(screen.getByRole('button', { name: /continue/i }));
    for (const name of ['Strong in mathematics', 'General Math', 'Heavy mathematics', 'Software engineering', 'Building apps', 'Technology builder', 'High salary', 'Jakarta only', 'Kedokteran', 'Build AI products']) {
      await waitFor(() => expect(screen.getByRole('button', { name })).toBeTruthy());
      expect(screen.queryByRole('textbox')).toBeNull();
      fireEvent.click(screen.getByRole('button', { name }));
      fireEvent.click(screen.getByRole('button', { name: /continue/i }));
      if (name === 'Kedokteran') await waitFor(() => expect(screen.getByRole('button', { name: 'Build AI products' })).toBeTruthy());
    }
    fireEvent.click(screen.getByRole('button', { name: /analyze/i }));

    expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({
      survey_mode: 'mode_zero',
      academic_context: { selected: ['Kuat di matematika'] },
      subject_preferences: { preferred: ['Matematika Umum'] },
      interest_deep_dive: { selected: ['Software engineering'] },
      activities: { selected: ['Membuat aplikasi'] },
      career_direction: { selected: ['Technology builder'] },
      career_goals: { selected: ['Gaji tinggi'] },
      constraints: { selected: ['Prefer Jakarta only'] },
      expected_prodi: null,
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
