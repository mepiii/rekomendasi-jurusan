// Purpose: Present recommendation response with summary, list, disclaimer, and reset action.
// Callers: App component.
// Deps: ResultCard component.
// API: Props result, onReset.
// Side effects: None.
import React from 'react';
import ResultCard from './ResultCard';

export default function ResultSection({ result, onReset }) {
  return (
    <section className="w-full max-w-[680px]">
      <h2 className="text-3xl font-semibold tracking-tight text-textPrimary">Rekomendasi Jurusan untuk Kamu</h2>

      <div className="mt-4 rounded-lg border border-standard bg-panel p-4">
        <p className="text-xs uppercase tracking-wide text-textSubtle">Profile Summary</p>
        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          <div>
            <p className="text-xs text-textSubtle">Mapel Terkuat</p>
            <p className="mt-1 text-sm text-textPrimary">{result.profile_summary?.strongest_subject || '-'}</p>
          </div>
          <div>
            <p className="text-xs text-textSubtle">Kelompok Terkuat</p>
            <p className="mt-1 text-sm capitalize text-textPrimary">{result.profile_summary?.strongest_group || '-'}</p>
          </div>
          <div>
            <p className="text-xs text-textSubtle">Rata-rata Nilai</p>
            <p className="mt-1 text-sm text-textPrimary">{result.profile_summary?.avg_score ?? '-'}</p>
          </div>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {result.recommendations?.map((recommendation) => (
          <ResultCard
            key={`${recommendation.rank}-${recommendation.major}`}
            recommendation={recommendation}
            highlight={recommendation.rank === 1}
          />
        ))}
      </div>

      <div className="mt-4 rounded-md border border-subtle bg-white/[0.02] px-4 py-3 text-xs leading-relaxed text-textSubtle">
        {result.disclaimer ||
          'Hasil ini adalah alat bantu pengambilan keputusan, bukan penentu final. Diskusikan dengan guru BK atau orang tua.'}
      </div>

      <button
        type="button"
        onClick={onReset}
        className="mt-4 rounded-md border border-standard px-4 py-2 text-sm text-textSecondary transition hover:border-accent/50 hover:text-textPrimary"
      >
        Coba Input Lain
      </button>
    </section>
  );
}
