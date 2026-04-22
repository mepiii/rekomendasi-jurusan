// Purpose: Collect user academic profile input and trigger recommendation request.
// Callers: App component.
// Deps: React state hooks.
// API: Props onSubmit(payload), loading, error.
// Side effects: Emits validated payload to parent submit handler.
import { useMemo, useState } from 'react';

const SUBJECT_FIELDS = [
  { key: 'math', label: 'Matematika' },
  { key: 'physics', label: 'Fisika' },
  { key: 'chemistry', label: 'Kimia' },
  { key: 'biology', label: 'Biologi' },
  { key: 'economics', label: 'Ekonomi' },
  { key: 'indonesian', label: 'Bahasa Indonesia' },
  { key: 'english', label: 'Bahasa Inggris' }
];

const INTERESTS = [
  'Teknologi',
  'Data & AI',
  'Rekayasa',
  'Sosial/Manusia',
  'Komunikasi',
  'Hukum/Politik',
  'Alam/Kesehatan',
  'Bisnis/Manajemen',
  'Seni/Kreatif',
  'Pendidikan/Bahasa'
];

const TRACKS = ['IPA', 'IPS', 'Bahasa'];

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
        nextErrors[key] = `Nilai ${label} wajib diisi`;
        return;
      }
      const parsed = Number(raw);
      if (Number.isNaN(parsed) || parsed < 0 || parsed > 100) {
        nextErrors[key] = `Nilai ${label} harus 0–100`;
      }
    });

    if (!smaTrack) nextErrors.smaTrack = 'Jurusan SMA wajib dipilih';
    if (interests.length < 1) nextErrors.interests = 'Pilih minimal 1 minat';
    if (interests.length > 5) nextErrors.interests = 'Maksimal 5 minat';

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
          Temukan Jurusan yang Tepat untuk Kamu
        </h1>
        <p className="mt-2 text-sm text-textMuted">
          Masukkan nilai rapor dan minatmu, sistem akan memberi rekomendasi jurusan.
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
        <p className="text-sm text-textSecondary">Minat</p>
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
          <span className="text-xs text-textSubtle">{selectedCount} dipilih</span>
        </div>
      </div>

      <div className="mt-5 flex flex-col gap-1">
        <label className="text-sm text-textSecondary" htmlFor="sma-track">
          Jurusan SMA
        </label>
        <select
          id="sma-track"
          value={smaTrack}
          onChange={(event) => setSmaTrack(event.target.value)}
          className={`rounded-md border bg-input px-3 py-2 text-sm text-textPrimary outline-none ${
            errors.smaTrack ? 'border-red-500' : 'border-standard focus:border-accent'
          }`}
        >
          <option value="">Pilih jurusan SMA</option>
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
        {loading ? 'Sedang menganalisis profilmu...' : 'Lihat Rekomendasi →'}
      </button>

      <div className="mt-5 rounded-md border border-subtle bg-white/[0.02] px-4 py-3 text-xs leading-relaxed text-textSubtle">
        Hasil ini adalah alat bantu pengambilan keputusan berdasarkan data yang kamu masukkan. Rekomendasi ini
        bukan pengganti diskusi dengan guru BK, orang tua, atau konselor pendidikan.
      </div>
    </form>
  );
}
