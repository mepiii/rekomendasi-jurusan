// Purpose: Multi-step recommendation journey with animated transitions for grades and interests.
// Callers: App component.
// Deps: React, framer-motion.
// API: Props onSubmit(payload), loading, error.
// Side effects: Emits validated payload to parent submit handler.
import { AnimatePresence, motion } from 'framer-motion';
import { useMemo, useState } from 'react';

const SUBJECT_FIELDS = [
  { key: 'math', label: 'Mathematics' },
  { key: 'physics', label: 'Physics' },
  { key: 'chemistry', label: 'Chemistry' },
  { key: 'biology', label: 'Biology' },
  { key: 'economics', label: 'Economics' },
  { key: 'indonesian', label: 'Indonesian Language' },
  { key: 'english', label: 'English Language' }
];

const INTERESTS = [
  'Technology',
  'Data & AI',
  'Engineering',
  'Social Sciences & Humanities',
  'Communication',
  'Law & Politics',
  'Science & Health',
  'Business & Management',
  'Arts & Creativity',
  'Education & Languages'
];

const TRACKS = ['Science', 'Social Studies', 'Language'];

const stepMotion = {
  initial: { opacity: 0, x: 30, filter: 'blur(8px)' },
  animate: { opacity: 1, x: 0, filter: 'blur(0px)' },
  exit: { opacity: 0, x: -30, filter: 'blur(8px)' },
  transition: { duration: 0.35, ease: 'easeInOut' }
};

function generateSessionId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function GlassCard({ children }) {
  return (
    <div className="glass-panel w-full max-w-3xl rounded-2xl border border-white/15 p-6 shadow-[0_20px_80px_rgba(0,0,0,0.45)] backdrop-blur-xl sm:p-8">
      {children}
    </div>
  );
}

function StepIndicator({ step }) {
  const labels = ['Scores', 'Interests', 'Review'];
  return (
    <div className="mb-6 flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-textSubtle">
      {labels.map((label, idx) => {
        const active = idx + 1 === step;
        return (
          <div key={label} className={`rounded-full px-3 py-1 ${active ? 'bg-accent/20 text-accent' : 'bg-white/5 text-textSubtle'}`}>
            {label}
          </div>
        );
      })}
    </div>
  );
}

export default function RecommendationJourney({ onSubmit, loading, error }) {
  const [step, setStep] = useState(1);
  const [scores, setScores] = useState({
    math: '',
    physics: '',
    chemistry: '',
    biology: '',
    economics: '',
    indonesian: '',
    english: ''
  });
  const [interests, setInterests] = useState([]);
  const [smaTrack, setSmaTrack] = useState('');
  const [errors, setErrors] = useState({});

  const hasErrors = useMemo(() => Object.keys(errors).length > 0, [errors]);

  const handleScoreChange = (key, value) => {
    const next = value.replace(/[^0-9.]/g, '');
    setScores((prev) => ({ ...prev, [key]: next }));
  };

  const toggleInterest = (interest) => {
    setInterests((prev) => (prev.includes(interest) ? prev.filter((item) => item !== interest) : [...prev, interest]));
  };

  const validateScores = () => {
    const nextErrors = {};
    SUBJECT_FIELDS.forEach(({ key, label }) => {
      const raw = scores[key];
      if (raw === '') {
        nextErrors[key] = `${label} score is required`;
        return;
      }
      const parsed = Number(raw);
      if (Number.isNaN(parsed) || parsed < 0 || parsed > 100) {
        nextErrors[key] = `${label} score must be between 0 and 100`;
      }
    });

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const validateInterests = () => {
    const nextErrors = {};
    if (!smaTrack) nextErrors.smaTrack = 'High school track is required';
    if (interests.length < 1) nextErrors.interests = 'Select at least 1 interest';
    if (interests.length > 5) nextErrors.interests = 'You can select up to 5 interests';
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const goNext = () => {
    if (step === 1 && validateScores()) setStep(2);
    if (step === 2 && validateInterests()) setStep(3);
  };

  const goBack = () => {
    setErrors({});
    setStep((prev) => Math.max(1, prev - 1));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!validateScores() || !validateInterests()) {
      setStep(1);
      return;
    }

    const payload = {
      session_id: generateSessionId(),
      sma_track: smaTrack,
      scores: Object.fromEntries(Object.entries(scores).map(([key, value]) => [key, Number(value)])),
      interests,
      top_n: 5
    };

    onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl">
      <GlassCard>
        <StepIndicator step={step} />
        <h1 className="mb-2 text-2xl font-semibold tracking-tight text-textPrimary sm:text-3xl">College Major Journey</h1>
        <p className="mb-6 text-sm text-textMuted">Step-by-step profiling with animated transitions.</p>

        <AnimatePresence mode="wait">
          {step === 1 ? (
            <motion.div key="step-1" {...stepMotion} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {SUBJECT_FIELDS.map(({ key, label }) => (
                <label key={key} className="flex flex-col gap-1">
                  <span className="text-sm text-textSecondary">{label}</span>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={scores[key]}
                    onChange={(event) => handleScoreChange(key, event.target.value)}
                    className={`glass-input rounded-xl border px-3 py-2 text-sm text-textPrimary outline-none ${
                      errors[key] ? 'border-red-500' : 'border-white/20 focus:border-accent'
                    }`}
                  />
                  {errors[key] ? <span className="text-xs text-red-300">{errors[key]}</span> : null}
                </label>
              ))}
            </motion.div>
          ) : null}

          {step === 2 ? (
            <motion.div key="step-2" {...stepMotion} className="space-y-5">
              <div>
                <p className="text-sm text-textSecondary">Interests</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {INTERESTS.map((interest) => {
                    const active = interests.includes(interest);
                    const blocked = !active && interests.length >= 5;
                    return (
                      <button
                        key={interest}
                        type="button"
                        onClick={() => {
                          if (!blocked) toggleInterest(interest);
                        }}
                        className={`rounded-full border px-3 py-1 text-xs transition ${
                          active
                            ? 'border-accent bg-accent/20 text-accent'
                            : 'border-white/20 text-textMuted hover:border-accent/60 hover:text-textSecondary'
                        } ${blocked ? 'cursor-not-allowed opacity-40' : ''}`}
                      >
                        {interest}
                      </button>
                    );
                  })}
                </div>
                <div className="mt-1 flex items-center justify-between">
                  {errors.interests ? <span className="text-xs text-red-300">{errors.interests}</span> : <span />}
                  <span className="text-xs text-textSubtle">{interests.length} selected</span>
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-sm text-textSecondary" htmlFor="sma-track">
                  High School Track
                </label>
                <select
                  id="sma-track"
                  value={smaTrack}
                  onChange={(event) => setSmaTrack(event.target.value)}
                  className={`glass-input rounded-xl border px-3 py-2 text-sm text-textPrimary outline-none ${
                    errors.smaTrack ? 'border-red-500' : 'border-white/20 focus:border-accent'
                  }`}
                >
                  <option value="">Select your high school track</option>
                  {TRACKS.map((track) => (
                    <option key={track} value={track}>
                      {track}
                    </option>
                  ))}
                </select>
                {errors.smaTrack ? <span className="text-xs text-red-300">{errors.smaTrack}</span> : null}
              </div>
            </motion.div>
          ) : null}

          {step === 3 ? (
            <motion.div key="step-3" {...stepMotion} className="space-y-4">
              <div className="rounded-xl border border-white/15 bg-white/5 p-4 text-sm text-textMuted">
                <p className="mb-2 text-textSecondary">Profile Review</p>
                <p>Track: {smaTrack || '-'}</p>
                <p>Interests: {interests.join(', ') || '-'}</p>
                <p>
                  Average score:{' '}
                  {Math.round(
                    Object.values(scores).reduce((acc, value) => acc + Number(value || 0), 0) /
                      SUBJECT_FIELDS.length
                  )}
                </p>
              </div>

              <div className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-xs leading-relaxed text-textSubtle">
                These results are decision support, not a final answer. Confirm them with a counselor, mentor, or trusted teacher.
              </div>
            </motion.div>
          ) : null}
        </AnimatePresence>

        {error ? <div className="mt-4 rounded-xl border border-red-500/50 bg-red-500/10 px-3 py-2 text-sm text-red-200">{error}</div> : null}

        <div className="mt-6 flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={goBack}
            disabled={step === 1 || loading}
            className="rounded-xl border border-white/20 px-4 py-2 text-sm text-textSecondary transition hover:border-accent/60 disabled:opacity-40"
          >
            Back
          </button>

          {step < 3 ? (
            <button
              type="button"
              onClick={goNext}
              className="rounded-xl bg-cta px-4 py-2 text-sm font-medium text-white transition hover:brightness-110"
            >
              Continue
            </button>
          ) : (
            <button
              type="submit"
              disabled={loading || hasErrors}
              className="rounded-xl bg-cta px-4 py-2 text-sm font-medium text-white transition hover:brightness-110 disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'See Recommendations'}
            </button>
          )}
        </div>
      </GlassCard>
    </form>
  );
}
