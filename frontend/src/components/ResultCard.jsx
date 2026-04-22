// Purpose: Render single ranked recommendation card with score badge and explanation.
// Callers: ResultSection component.
// Deps: React.
// API: Props recommendation, highlight.
// Side effects: None.
import React from 'react';

function scoreStyle(score) {
  if (score >= 80) {
    return {
      badge: 'border-[rgba(39,166,68,0.2)] bg-[rgba(39,166,68,0.12)] text-success'
    };
  }
  if (score >= 60) {
    return {
      badge: 'border-[rgba(113,112,255,0.2)] bg-[rgba(113,112,255,0.12)] text-accent'
    };
  }
  return {
    badge: 'border-[rgba(98,102,109,0.2)] bg-[rgba(98,102,109,0.12)] text-textMuted'
  };
}

export default function ResultCard({ recommendation, highlight }) {
  const style = scoreStyle(recommendation.suitability_score);

  return (
    <article
      className={`rounded-lg border bg-panel p-5 shadow-subtle transition ${
        highlight ? 'border-accent/60' : 'border-standard'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-textSubtle">#{recommendation.rank}</p>
          <h3 className="mt-1 text-xl font-semibold text-textPrimary">{recommendation.major}</h3>
          <p className="mt-1 text-sm text-textMuted">{recommendation.cluster}</p>
        </div>

        <div className="flex flex-col items-end gap-2">
          {highlight ? (
            <span className="rounded-full border border-accent/40 px-2 py-1 text-[10px] uppercase text-accent">
              Top Recommendation
            </span>
          ) : null}
          <span className={`rounded-full border px-3 py-1 text-sm ${style.badge}`}>
            {recommendation.suitability_score}%
          </span>
        </div>
      </div>

      <p className="mt-4 text-sm leading-relaxed text-textMuted">{recommendation.explanation}</p>
    </article>
  );
}
