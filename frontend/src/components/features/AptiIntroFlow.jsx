// Purpose: Collect minimal first-run personalization before the main Apti workspace.
// Callers: App shell orchestration.
// Deps: React state.
// API: Default export AptiIntroFlow({ onComplete, onSkip }).
// Side effects: Emits completed intro payload to parent callbacks.
import { useState } from 'react';

const goalOptions = [
  { value: 'find-fit', label: 'Find the best-fit major' },
  { value: 'compare-majors', label: 'Compare several majors' },
  { value: 'understand-strengths', label: 'Understand strengths first' }
];

const confidenceOptions = [
  { value: 'very-unsure', label: 'Very unsure' },
  { value: 'somewhat-unsure', label: 'Somewhat unsure' },
  { value: 'rough-idea', label: 'Already have a rough idea' }
];

export default function AptiIntroFlow({ onComplete, onSkip }) {
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [goal, setGoal] = useState('');
  const [confidence, setConfidence] = useState('');
  const [error, setError] = useState('');

  const continueFromName = () => {
    if (!name.trim()) return setError('Name is required.');
    setError('');
    setStep(2);
  };

  const continueFromGoal = () => goal && setStep(3);
  const completeIntro = () => confidence && onComplete({ completed: true, name: name.trim(), goal, confidence });

  return (
    <section className="glass-panel editorial-shell w-full max-w-3xl rounded-3xl p-6 sm:p-8">
      <p className="text-xs uppercase tracking-[0.2em] text-textSubtle">Step {step} of 3</p>
      <h1 className="mt-3 text-3xl font-semibold tracking-tight text-textPrimary">Welcome to Apti</h1>
      <p className="mt-2 text-sm text-textMuted">A short setup helps Apti shape the workspace around your decision style.</p>

      {step === 1 ? (
        <div className="mt-6 space-y-3">
          <label className="flex flex-col gap-2 text-sm text-textSecondary" htmlFor="apti-name">
            Your name
            <input
              id="apti-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="glass-input rounded-xl px-3 py-2 text-textPrimary"
            />
          </label>
          {error ? <p className="text-sm text-danger">{error}</p> : null}
          <div className="flex gap-3">
            <button type="button" onClick={continueFromName} className="rounded-xl bg-cta px-4 py-2 text-sm font-medium text-white">
              Continue
            </button>
            <button type="button" onClick={onSkip} className="apti-secondary-button rounded-xl px-4 py-2 text-sm">
              Skip for now
            </button>
          </div>
        </div>
      ) : null}

      {step === 2 ? (
        <div className="mt-6 space-y-3">
          <p className="text-sm text-textSecondary">What do you want from Apti today?</p>
          <div className="flex flex-wrap gap-3">
            {goalOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setGoal(option.value)}
                className={`editorial-chip rounded-full px-4 py-2 text-sm ${goal === option.value ? 'border-accent/30 bg-accent/10 text-accent' : 'text-textSecondary hover:border-accent/40 hover:text-textPrimary'}`}
              >
                {option.label}
              </button>
            ))}
          </div>
          <button type="button" onClick={continueFromGoal} className="rounded-xl bg-cta px-4 py-2 text-sm font-medium text-white">
            Continue
          </button>
        </div>
      ) : null}

      {step === 3 ? (
        <div className="mt-6 space-y-3">
          <p className="text-sm text-textSecondary">How certain do you feel right now?</p>
          <div className="flex flex-wrap gap-3">
            {confidenceOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setConfidence(option.value)}
                className={`editorial-chip rounded-full px-4 py-2 text-sm ${confidence === option.value ? 'border-accent/30 bg-accent/10 text-accent' : 'text-textSecondary hover:border-accent/40 hover:text-textPrimary'}`}
              >
                {option.label}
              </button>
            ))}
          </div>
          <button type="button" onClick={completeIntro} className="rounded-xl bg-cta px-4 py-2 text-sm font-medium text-white">
            Enter Apti
          </button>
        </div>
      ) : null}
    </section>
  );
}
