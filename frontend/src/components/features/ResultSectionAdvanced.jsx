// Purpose: Present advanced recommendation results, explainability status, and user feedback capture.
// Callers: App component.
// Deps: ResultCardAdvanced, framer-motion.
// API: Props result, locale, copy, explanations, onReset, onSubmitFeedback, feedbackState.
// Side effects: Submits feedback payload.
import { motion } from 'framer-motion';
import { useMemo, useState } from 'react';
import ResultCardAdvanced from './ResultCardAdvanced';

const profileLabel = (value, locale) => {
  if (locale !== 'id' || !value) return value;
  return {
    'Pendidikan Agama': 'Pendidikan Agama', 'Matematika Umum': 'Matematika Umum', science: 'sains', social: 'sosial', language: 'bahasa', humanities: 'humaniora', technical: 'teknis', High: 'Tinggi', Medium: 'Sedang', Emerging: 'Berkembang'
  }[value] || value;
};

const localizedNotice = (note, locale) => {
  if (locale !== 'id') return note;
  if (note.includes('fallback')) return 'Apti memakai rekomendasi cadangan sementara karena model prediktif belum siap.';
  if (note.includes('Optional missing subjects')) return 'Mapel opsional yang kosong diperlakukan netral, bukan sebagai nilai rendah.';
  if (note.includes('extra caution')) return 'Apti memakai kehati-hatian ekstra karena profil ini berbeda dari contoh latihan terbaru.';
  return note;
};

function mergeRecommendationWithExplanations(recommendations, explanations) {
  const map = new Map((explanations || []).map((item) => [item.major, item]));
  return (recommendations || []).map((item) => {
    const explanation = map.get(item.major) || {};
    return {
      ...item,
      shap_values: explanation.shap_values || item.shap_values || {},
      user_scores: item.user_scores || {},
      fallback_reason: item.fallback_reason || explanation.fallback_reason,
      notes: item.notes || explanation.notes
    };
  });
}

export default function ResultSectionAdvanced({ result, locale = 'en', copy, explanations, onReset, onSubmitFeedback, feedbackState }) {
  const [aligns, setAligns] = useState(true);
  const [selectedMajor, setSelectedMajor] = useState('');
  const [rating, setRating] = useState(5);
  const [notes, setNotes] = useState('');

  const recommendationItems = useMemo(
    () => mergeRecommendationWithExplanations(result?.recommendations || [], explanations?.explanations || []),
    [result, explanations]
  );

  const clampRating = (value) => {
    const parsed = Number(value || 5);
    return Number.isFinite(parsed) ? Math.min(5, Math.max(1, parsed)) : 5;
  };

  const handleFeedback = (event) => {
    event.preventDefault();
    onSubmitFeedback({
      selected_major: selectedMajor || null,
      aligns_with_goals: aligns,
      rating: clampRating(rating),
      notes: notes.trim() || null
    });
  };

  return (
    <section className="w-full max-w-5xl space-y-4">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-3">
        <p className="editorial-kicker text-xs font-medium uppercase">{copy.appName} recommendations</p>
        <h2 className="text-3xl font-semibold tracking-tight text-textPrimary">{copy.topRecommendations}</h2>
        <p className="max-w-3xl text-sm leading-6 text-textMuted">{copy.resultIntro}</p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.3 }} transition={{ duration: 0.38, ease: [0.16, 1, 0.3, 1] }} className="glass-panel editorial-shell apti-interactive-lift rounded-[24px] border p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs uppercase tracking-[0.24em] text-textSubtle">{copy.profileReview}</p>
          <span className="editorial-chip rounded-full px-3 py-1 text-[11px] uppercase tracking-[0.18em]">Latency {result.latency_ms ?? '-'} ms</span>
        </div>
        <div className="mt-3 grid gap-3 sm:grid-cols-4">
          <div>
            <p className="text-xs text-textSubtle">{copy.strongestSubject}</p>
            <p className="mt-1 text-sm text-textPrimary">{profileLabel(result.profile_summary?.strongest_subject, locale) || '-'}</p>
          </div>
          <div>
            <p className="text-xs text-textSubtle">{copy.strongestGroup}</p>
            <p className="mt-1 text-sm capitalize text-textPrimary">{profileLabel(result.profile_summary?.strongest_group, locale) || '-'}</p>
          </div>
          <div>
            <p className="text-xs text-textSubtle">{copy.averageScore}</p>
            <p className="mt-1 text-sm text-textPrimary">{result.profile_summary?.avg_score ?? '-'}</p>
          </div>
          <div>
            <p className="text-xs text-textSubtle">{copy.confidence}</p>
            <p className="mt-1 text-sm text-textPrimary">{profileLabel(result.profile_summary?.confidence_label, locale) || '-'}</p>
          </div>
        </div>
      </motion.div>

      {result.fallback_used || result.fallback_reason || result.notes?.length ? (
        <motion.div initial={{ opacity: 0, y: 14 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.3 }} transition={{ duration: 0.34, ease: [0.16, 1, 0.3, 1] }} className="editorial-shell rounded-[22px] border px-4 py-4 text-xs leading-relaxed text-textSubtle">
          {result.fallback_used ? <p>{locale === 'id' ? 'Apti memakai rekomendasi cadangan sementara. Hasil tetap dihitung dari pola nilai, minat, dan preferensi kamu.' : 'Apti used temporary backup recommendations. Results still use your score pattern, interests, and preferences.'}</p> : null}
          {result.fallback_reason ? <p>{copy.fallback || 'Fallback'}: {localizedNotice(result.fallback_reason, locale)}</p> : null}
          {Array.isArray(result.notes) ? result.notes.map((note) => <p key={note}>{localizedNotice(note, locale)}</p>) : result.notes ? <p>{copy.notes || 'Notes'}: {localizedNotice(result.notes, locale)}</p> : null}
        </motion.div>
      ) : null}

      <div className="space-y-3">
        {recommendationItems.map((recommendation) => (
          <ResultCardAdvanced key={`${recommendation.rank}-${recommendation.major}`} recommendation={recommendation} highlight={recommendation.rank === 1} copy={copy} locale={locale} fallbackUsed={Boolean(result.fallback_used)} />
        ))}
      </div>

      <motion.form onSubmit={handleFeedback} initial={{ opacity: 0, y: 18 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.25 }} transition={{ duration: 0.42, ease: [0.16, 1, 0.3, 1] }} className="glass-panel editorial-shell apti-interactive-lift rounded-[24px] border p-5 apti-shimmer">
        <p className="editorial-kicker text-xs font-medium uppercase">{copy.reflection}</p>
        <p className="mt-2 text-sm font-medium text-textPrimary">{copy.reflectionPrompt}</p>
        <p className="mt-1 max-w-2xl text-xs leading-6 text-textMuted">{copy.reflectionHelper}</p>

        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <label className="flex items-center gap-2 text-sm text-textSecondary">
            <input type="radio" checked={aligns === true} onChange={() => setAligns(true)} className="accent-accent" />
            {copy.yesMatch}
          </label>
          <label className="flex items-center gap-2 text-sm text-textSecondary">
            <input type="radio" checked={aligns === false} onChange={() => setAligns(false)} className="accent-accent" />
            {copy.notYet}
          </label>

          <select value={selectedMajor} onChange={(event) => setSelectedMajor(event.target.value)} className="glass-input rounded-xl px-3 py-2 text-sm text-textPrimary">
            <option value="">{copy.actualMajor}</option>
            {recommendationItems.map((item) => (
              <option key={item.major} value={item.major}>
                {item.major}
              </option>
            ))}
          </select>

          <input type="number" min="1" max="5" value={rating} onChange={(event) => setRating(clampRating(event.target.value))} className="glass-input rounded-xl px-3 py-2 text-sm text-textPrimary" placeholder={copy.rating} />
        </div>

        <textarea value={notes} onChange={(event) => setNotes(event.target.value)} className="glass-input mt-3 h-20 w-full rounded-xl px-3 py-2 text-sm text-textPrimary" placeholder={copy.notes} />

        <div className="mt-3 flex items-center justify-between gap-3">
          <button type="submit" disabled={feedbackState.loading} className="apti-primary-button px-5 py-2.5 text-sm font-semibold disabled:opacity-60">
            {feedbackState.loading ? <span className="apti-button-spinner" aria-hidden="true" /> : null}
            {feedbackState.loading ? copy.saving : copy.sendFeedback}
          </button>
          <button type="button" onClick={onReset} className="apti-secondary-button rounded-xl px-4 py-2 text-sm transition">
            {copy.tryDifferentInputs}
          </button>
        </div>

        {feedbackState.message ? <p className="mt-2 text-xs text-textMuted">{feedbackState.message}</p> : null}
      </motion.form>

      <motion.div initial={{ opacity: 0, y: 14 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.4 }} transition={{ duration: 0.34, ease: [0.16, 1, 0.3, 1] }} className="editorial-shell apti-interactive-lift rounded-[22px] border px-4 py-4 text-xs leading-relaxed text-textSubtle">{result.disclaimer || copy.disclaimer}</motion.div>
    </section>
  );
}
