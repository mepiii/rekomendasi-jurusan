// Purpose: Collect user academic profile input and trigger recommendation request.
// Callers: App component.
// Deps: React state hooks.
// API: Props onSubmit(payload), loading, error.
// Side effects: Emits validated payload to parent submit handler.
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

function generateSessionId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export default function RecommendationForm({ onSubmit, loading, error }) {
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

  const selectedCount = interests.length;

  const hasErrors = useMemo(() => Object.keys(errors).length > 0, [errors]);

  const toggleInterest = (interest) => {
    setInterests((prev) =>
      prev.includes(interest)
        ? prev.filter((item) => item !== interest)
        : [...prev, interest]
    );
  };

  const handleScoreChange = (key, value) => {
    const next = value.replace(/[^0-9.]/g, '');
    setScores((prev) => ({ ...prev, [key]: next }));
  };

  const validate = () => {
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

    if (!smaTrack) nextErrors.smaTrack = 'High school track is required';
    if (interests.length < 1) nextErrors.interests = 'Select at least 1 interest';
    if (interests.length > 5) nextErrors.interests = 'You can select up to 5 interests';

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!validate()) return;

    const payload = {
      session_id: generateSessionId(),
      sma_track: smaTrack,
      scores: Object.fromEntries(
        Object.entries(scores).map(([key, value]) => [key, Number(value)])
      ),
      interests,
      top_n: 5
    };

    onSubmit(payload);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-[560px] rounded-lg border border-standard bg-panel p-6 shadow-subtle"
    >
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-textPrimary">
          Find the Right College Major for You
        </h1>
        <p className="mt-2 text-sm text-textMuted">
          Enter your grades and interests, and the system will generate tailored major recommendations.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {SUBJECT_FIELDS.map(({ key, label }) => (
          <label key={key} className="flex flex-col gap-1">
            <span className="text-sm text-textSecondary">{label}</span>
            <input
              type="number"
              min="0"
              max="100"
              value={scores[key]}
              onChange={(event) => handleScoreChange(key, event.target.value)}
              className={`rounded-md border bg-input px-3 py-2 text-sm text-textPrimary outline-none transition ${
                errors[key] ? 'border-red-500' : 'border-standard focus:border-accent'
              }`}
            />
            {errors[key] ? <span className="text-xs text-red-400">{errors[key]}</span> : null}
          </label>
        ))}
      </div>

      <div className="mt-5">
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
                    ? 'border-accent text-accent'
                    : 'border-standard text-textMuted hover:border-accent/60 hover:text-textSecondary'
                } ${blocked ? 'cursor-not-allowed opacity-40' : ''}`}
              >
                {interest}
              </button>
            );
          })}
        </div>
        <div className="mt-1 flex items-center justify-between">
          {errors.interests ? <span className="text-xs text-red-400">{errors.interests}</span> : <span />}
          <span className="text-xs text-textSubtle">{selectedCount} selected</span>
        </div>
      </div>

      <div className="mt-5 flex flex-col gap-1">
        <label className="text-sm text-textSecondary" htmlFor="sma-track">
          High School Track
        </label>
        <select
          id="sma-track"
          value={smaTrack}
          onChange={(event) => setSmaTrack(event.target.value)}
          className={`rounded-md border bg-input px-3 py-2 text-sm text-textPrimary outline-none ${
            errors.smaTrack ? 'border-red-500' : 'border-standard focus:border-accent'
          }`}
        >
          <option value="">Select your high school track</option>
          {TRACKS.map((track) => (
            <option key={track} value={track}>
              {track}
            </option>
          ))}
        </select>
        {errors.smaTrack ? <span className="text-xs text-red-400">{errors.smaTrack}</span> : null}
      </div>

      {error ? (
        <div className="mt-4 rounded-md border border-standard bg-white/5 px-3 py-2 text-sm text-red-300">
          {error}
        </div>
      ) : null}

      <button
        type="submit"
        disabled={loading || hasErrors}
        className="mt-6 inline-flex w-full items-center justify-center rounded-md bg-cta px-4 py-2 text-sm font-medium text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? 'Analyzing your profile...' : 'See Recommendations →'}
      </button>

      <div className="mt-5 rounded-md border border-subtle bg-white/[0.02] px-4 py-3 text-xs leading-relaxed text-textSubtle">
        These results are decision support based on the data you entered. They should not replace a conversation
        with a counselor, parent, or education advisor.
      </div>
    </form>
  );
}
