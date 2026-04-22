// Purpose: Present advanced recommendation results, explainability status, and user feedback capture.
// Callers: App component.
// Deps: ResultCardAdvanced, framer-motion.
// API: Props result, explanations, onReset, onSubmitFeedback, feedbackState.
// Side effects: Submits feedback payload.
import { motion } from 'framer-motion';
import { useMemo, useState } from 'react';
import ResultCardAdvanced from './ResultCardAdvanced';

function mergeRecommendationWithExplanations(recommendations, explanations) {
  const map = new Map((explanations || []).map((item) => [item.major, item.shap_values || {}]));
  return (recommendations || []).map((item) => ({
    ...item,
    shap_values: map.get(item.major) || item.shap_values || {},
    user_scores: item.user_scores || {}
  }));
}

export default function ResultSectionAdvanced({
  result,
  explanations,
  onReset,
  onSubmitFeedback,
  feedbackState
}) {
  const [aligns, setAligns] = useState(true);
  const [selectedMajor, setSelectedMajor] = useState('');
  const [rating, setRating] = useState(5);
  const [notes, setNotes] = useState('');

  const recommendationItems = useMemo(
    () => mergeRecommendationWithExplanations(result?.recommendations || [], explanations?.explanations || []),
    [result, explanations]
  );

  const handleFeedback = (event) => {
    event.preventDefault();
    onSubmitFeedback({
      selected_major: selectedMajor || null,
      aligns_with_goals: aligns,
      rating,
      notes: notes.trim() || null
    });
  };

  return (
    <section className="w-full max-w-5xl space-y-4">
      <motion.h2
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-3xl font-semibold tracking-tight text-textPrimary"
      >
        Your Best-Fit College Major Recommendations
      </motion.h2>

      <div className="glass-panel rounded-2xl border border-white/15 p-4">
        <p className="text-xs uppercase tracking-wide text-textSubtle">Profile Summary</p>
        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          <div>
            <p className="text-xs text-textSubtle">Strongest Subject</p>
            <p className="mt-1 text-sm text-textPrimary">{result.profile_summary?.strongest_subject || '-'}</p>
          </div>
          <div>
            <p className="text-xs text-textSubtle">Strongest Group</p>
            <p className="mt-1 text-sm capitalize text-textPrimary">{result.profile_summary?.strongest_group || '-'}</p>
          </div>
          <div>
            <p className="text-xs text-textSubtle">Average Score</p>
            <p className="mt-1 text-sm text-textPrimary">{result.profile_summary?.avg_score ?? '-'}</p>
          </div>
        </div>
        <div className="mt-3 text-xs text-textMuted">Latency: {result.latency_ms ?? '-'} ms</div>
      </div>

      <div className="space-y-3">
        {recommendationItems.map((recommendation) => (
          <ResultCardAdvanced
            key={`${recommendation.rank}-${recommendation.major}`}
            recommendation={recommendation}
            highlight={recommendation.rank === 1}
          />
        ))}
      </div>

      <form onSubmit={handleFeedback} className="glass-panel rounded-2xl border border-white/15 p-4">
        <p className="text-sm font-medium text-textPrimary">Verification</p>
        <p className="mt-1 text-xs text-textMuted">Does this align with your goals? Submit real outcome for active learning.</p>

        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <label className="flex items-center gap-2 text-sm text-textSecondary">
            <input
              type="radio"
              checked={aligns === true}
              onChange={() => setAligns(true)}
              className="accent-accent"
            />
            Yes, it matches
          </label>
          <label className="flex items-center gap-2 text-sm text-textSecondary">
            <input
              type="radio"
              checked={aligns === false}
              onChange={() => setAligns(false)}
              className="accent-accent"
            />
            Not yet
          </label>

          <select
            value={selectedMajor}
            onChange={(event) => setSelectedMajor(event.target.value)}
            className="glass-input rounded-xl border border-white/20 px-3 py-2 text-sm text-textPrimary"
          >
            <option value="">Select your actual major (optional)</option>
            {recommendationItems.map((item) => (
              <option key={item.major} value={item.major}>
                {item.major}
              </option>
            ))}
          </select>

          <input
            type="number"
            min="1"
            max="5"
            value={rating}
            onChange={(event) => setRating(Number(event.target.value || 5))}
            className="glass-input rounded-xl border border-white/20 px-3 py-2 text-sm text-textPrimary"
            placeholder="Rating 1-5"
          />
        </div>

        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          className="glass-input mt-3 h-20 w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-textPrimary"
          placeholder="Additional notes..."
        />

        <div className="mt-3 flex items-center justify-between gap-3">
          <button
            type="submit"
            disabled={feedbackState.loading}
            className="rounded-xl bg-cta px-4 py-2 text-sm font-medium text-white transition hover:brightness-110 disabled:opacity-60"
          >
            {feedbackState.loading ? 'Saving...' : 'Send Feedback'}
          </button>
          <button
            type="button"
            onClick={onReset}
            className="rounded-xl border border-white/20 px-4 py-2 text-sm text-textSecondary transition hover:border-accent/50"
          >
            Try Different Inputs
          </button>
        </div>

        {feedbackState.message ? <p className="mt-2 text-xs text-textMuted">{feedbackState.message}</p> : null}
      </form>

      <div className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-xs leading-relaxed text-textSubtle">
        {result.disclaimer ||
          'These results are decision support, not a final verdict. Discuss them with a counselor, teacher, or parent.'}
      </div>
    </section>
  );
}
