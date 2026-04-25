// Purpose: Collect minimal first-run personalization before the main Apti workspace.
// Callers: App shell orchestration.
// Deps: React state.
// API: Default export AptiIntroFlow({ onComplete, onSkip }).
// Side effects: Emits completed intro payload to parent callbacks.
import { useMemo, useState } from 'react';

const introCopy = {
  en: {
    step: 'Step',
    of: 'of',
    title: 'Welcome to Apti',
    helper: 'A short setup helps Apti shape the workspace around your decision style.',
    nameLabel: 'Your name',
    nameRequired: 'Name is required.',
    continue: 'Continue',
    skip: 'Skip for now',
    goalPrompt: 'What do you want from Apti today?',
    confidencePrompt: 'How certain do you feel right now?',
    enter: 'Enter Apti',
    goals: [
      { value: 'find-fit', label: 'Find the best-fit major' },
      { value: 'compare-majors', label: 'Compare several majors' },
      { value: 'understand-strengths', label: 'Understand strengths first' }
    ],
    confidenceOptions: [
      { value: 'very-unsure', label: 'Very unsure' },
      { value: 'somewhat-unsure', label: 'Somewhat unsure' },
      { value: 'rough-idea', label: 'Already have a rough idea' }
    ]
  },
  id: {
    step: 'Langkah',
    of: 'dari',
    title: 'Selamat datang di Apti',
    helper: 'Setup singkat membantu Apti menyesuaikan workspace dengan gaya pengambilan keputusanmu.',
    nameLabel: 'Nama kamu',
    nameRequired: 'Nama wajib diisi.',
    continue: 'Lanjut',
    skip: 'Lewati dulu',
    goalPrompt: 'Apa yang kamu butuhkan dari Apti hari ini?',
    confidencePrompt: 'Seberapa yakin perasaanmu sekarang?',
    enter: 'Masuk ke Apti',
    goals: [
      { value: 'find-fit', label: 'Cari jurusan yang paling cocok' },
      { value: 'compare-majors', label: 'Bandingkan beberapa jurusan' },
      { value: 'understand-strengths', label: 'Pahami kekuatan diri dulu' }
    ],
    confidenceOptions: [
      { value: 'very-unsure', label: 'Sangat belum yakin' },
      { value: 'somewhat-unsure', label: 'Lumayan belum yakin' },
      { value: 'rough-idea', label: 'Sudah punya gambaran kasar' }
    ]
  }
};

export default function AptiIntroFlow({ onComplete, onSkip, locale = 'en' }) {
  const content = useMemo(() => introCopy[locale] || introCopy.en, [locale]);
  const goalOptions = content.goals;
  const confidenceOptions = content.confidenceOptions;
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [goal, setGoal] = useState('');
  const [confidence, setConfidence] = useState('');
  const [error, setError] = useState('');

  const continueFromName = () => {
    if (!name.trim()) return setError(content.nameRequired);
    setError('');
    setStep(2);
  };

  const continueFromGoal = () => goal && setStep(3);
  const completeIntro = () => confidence && onComplete({ completed: true, name: name.trim(), goal, confidence });

  return (
    <section className="glass-panel editorial-shell w-full max-w-3xl rounded-3xl p-6 sm:p-8">
      <p className="text-xs uppercase tracking-[0.2em] text-textSubtle">{content.step} {step} {content.of} 3</p>
      <h1 className="mt-3 text-3xl font-semibold tracking-tight text-textPrimary">{content.title}</h1>
      <p className="mt-2 text-sm text-textMuted">{content.helper}</p>

      {step === 1 ? (
        <div className="mt-6 space-y-3">
          <label className="flex flex-col gap-2 text-sm text-textSecondary" htmlFor="apti-name">
            {content.nameLabel}
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
              {content.continue}
            </button>
            <button type="button" onClick={onSkip} className="apti-secondary-button rounded-xl px-4 py-2 text-sm">
              {content.skip}
            </button>
          </div>
        </div>
      ) : null}

      {step === 2 ? (
        <div className="mt-6 space-y-3">
          <p className="text-sm text-textSecondary">{content.goalPrompt}</p>
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
            {content.continue}
          </button>
        </div>
      ) : null}

      {step === 3 ? (
        <div className="mt-6 space-y-3">
          <p className="text-sm text-textSecondary">{content.confidencePrompt}</p>
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
            {content.enter}
          </button>
        </div>
      ) : null}
    </section>
  );
}
