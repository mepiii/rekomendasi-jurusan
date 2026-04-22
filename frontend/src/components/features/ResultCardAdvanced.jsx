// Purpose: Render advanced recommendation card with animated score gauge, radar chart, and explainability accordion.
// Callers: ResultSectionAdvanced component.
// Deps: recharts, framer-motion, lucide-react.
// API: Props recommendation, highlight.
// Side effects: None.
import { AnimatePresence, motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { useMemo, useState } from 'react';
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip
} from 'recharts';

const subjectMap = {
  math: 'Math',
  physics: 'Physics',
  chemistry: 'Chem',
  biology: 'Bio',
  economics: 'Eco',
  indonesian: 'Indo',
  english: 'Eng'
};

function useAnimatedNumber(target, duration = 0.9) {
  const [value, setValue] = useState(0);

  useMemo(() => {
    let frame;
    const startTime = performance.now();

    const tick = (now) => {
      const progress = Math.min((now - startTime) / (duration * 1000), 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(target * eased));
      if (progress < 1) frame = requestAnimationFrame(tick);
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, duration]);

  return value;
}

function Gauge({ score }) {
  const animated = useAnimatedNumber(score);
  const circumference = 2 * Math.PI * 36;
  const offset = circumference - (animated / 100) * circumference;

  return (
    <div className="relative h-24 w-24">
      <svg className="h-24 w-24 -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="36" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="10" />
        <motion.circle
          cx="50"
          cy="50"
          r="36"
          fill="none"
          stroke="url(#grad)"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          animate={{ strokeDashoffset: offset }}
          transition={{ type: 'spring', stiffness: 110, damping: 20 }}
        />
        <defs>
          <linearGradient id="grad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#7170ff" />
            <stop offset="100%" stopColor="#5e6ad2" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex items-center justify-center text-sm font-semibold text-textPrimary">{animated}%</div>
    </div>
  );
}

function buildRadarData(recommendation) {
  const req = recommendation.major_requirements || {};
  const user = recommendation.user_scores || {};

  return Object.entries(subjectMap).map(([key, label]) => ({
    subject: label,
    user: Number(user[key] || 0),
    major: Number(req[key] || 0)
  }));
}

export default function ResultCardAdvanced({ recommendation, highlight }) {
  const [open, setOpen] = useState(false);
  const radarData = buildRadarData(recommendation);
  const shapEntries = Object.entries(recommendation.shap_values || {}).sort((a, b) => b[1] - a[1]);

  return (
    <article className={`glass-panel rounded-2xl border p-5 ${highlight ? 'border-accent/60' : 'border-white/15'}`}>
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-textSubtle">#{recommendation.rank}</p>
          <h3 className="mt-1 text-xl font-semibold text-textPrimary">{recommendation.major}</h3>
          <p className="mt-1 text-sm text-textMuted">{recommendation.cluster}</p>
          <p className="mt-3 max-w-xl text-sm leading-relaxed text-textMuted">{recommendation.explanation}</p>
        </div>

        <div className="flex items-center gap-4">
          {highlight ? (
            <span className="rounded-full border border-accent/40 bg-accent/15 px-2 py-1 text-[10px] uppercase text-accent">
              Rekomendasi Utama
            </span>
          ) : null}
          <Gauge score={recommendation.suitability_score} />
        </div>
      </div>

      <div className="mt-4 h-64 w-full rounded-xl border border-white/10 bg-white/[0.02] p-2">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData} outerRadius="72%">
            <PolarGrid stroke="rgba(255,255,255,0.15)" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#d0d6e0', fontSize: 11 }} />
            <PolarRadiusAxis domain={[0, 100]} tick={{ fill: '#8a8f98', fontSize: 10 }} />
            <Radar name="User" dataKey="user" stroke="#27a644" fill="#27a644" fillOpacity={0.25} />
            <Radar name="Major" dataKey="major" stroke="#7170ff" fill="#7170ff" fillOpacity={0.22} />
            <Tooltip />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <button
        type="button"
        className="mt-4 inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/[0.03] px-3 py-2 text-xs text-textSecondary"
        onClick={() => setOpen((prev) => !prev)}
      >
        Why this?
        <motion.span animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown size={14} />
        </motion.span>
      </button>

      <AnimatePresence initial={false}>
        {open ? (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="mt-3 space-y-2 rounded-xl border border-white/10 bg-black/20 p-3">
              {shapEntries.length ? (
                shapEntries.map(([feature, value]) => (
                  <div key={feature} className="grid grid-cols-[1fr_auto] items-center gap-3">
                    <p className="text-xs text-textSecondary">{feature}</p>
                    <p className="text-xs font-semibold text-accent">{value.toFixed(1)}%</p>
                    <div className="col-span-2 h-2 rounded-full bg-white/10">
                      <div className="h-2 rounded-full bg-accent" style={{ width: `${Math.min(100, value)}%` }} />
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-textMuted">Menunggu explainability data...</p>
              )}
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </article>
  );
}
