// Purpose: Render advanced recommendation card with animated score gauge, radar chart, and explainability accordion.
// Callers: ResultSectionAdvanced component.
// Deps: recharts, framer-motion, lucide-react.
// API: Props recommendation, highlight, copy, locale.
// Side effects: None.
import { AnimatePresence, motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Tooltip } from 'recharts';

const subjectMap = {
  math: 'Math',
  general_math: 'Math',
  basic_math: 'Math',
  advanced_math: 'Adv Math',
  physics: 'Physics',
  chemistry: 'Chem',
  biology: 'Bio',
  economics: 'Eco',
  indonesian: 'Indo',
  english: 'Eng',
  sociology: 'Soc',
  geography: 'Geo',
  history: 'Hist',
  anthropology: 'Anth',
  informatics: 'Info',
  language: 'Lang'
};

function useAnimatedNumber(target, duration = 0.9) {
  const [value, setValue] = useState(0);

  useEffect(() => {
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
        <circle cx="50" cy="50" r="36" fill="none" stroke="rgba(120,120,120,0.18)" strokeWidth="10" />
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
  const keys = Array.from(new Set([...Object.keys(req), ...Object.keys(user)])).slice(0, 8);

  return keys.map((key) => ({
    subject: subjectMap[key] || key,
    user: Number(user[key] || 0),
    major: Number(req[key] || 0)
  }));
}

function RichList({ title, items }) {
  if (!items?.length) return null;
  return (
    <div className="space-y-2 rounded-xl border border-white/10 p-3">
      <p className="text-[11px] uppercase tracking-[0.18em] text-textSubtle">{title}</p>
      <ul className="space-y-1 text-sm text-textMuted">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function ResultCardAdvanced({ recommendation, highlight, copy }) {
  const [open, setOpen] = useState(false);
  const radarData = useMemo(() => buildRadarData(recommendation), [recommendation]);
  const shapEntries = Object.entries(recommendation.shap_values || {}).sort((a, b) => b[1] - a[1]);

  return (
    <motion.article
      initial={{ opacity: 0, y: 22 }}
      whileInView={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      viewport={{ once: true, amount: 0.18 }}
      transition={{ duration: 0.38, ease: [0.16, 1, 0.3, 1] }}
      className={`glass-panel apti-interactive-lift rounded-2xl border p-5 ${highlight ? 'border-accent/60' : 'border-white/15'}`}
    >
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-textSubtle">#{recommendation.rank}</p>
            <h3 className="mt-1 text-xl font-semibold text-textPrimary">{recommendation.major}</h3>
            <p className="mt-1 text-sm text-textMuted">{recommendation.cluster}</p>
          </div>
          <p className="max-w-xl text-sm leading-relaxed text-textMuted">{recommendation.explanation}</p>
          <div className="flex flex-wrap gap-2">
            {(recommendation.fit_summary || []).map((item) => (
              <span key={item} className="editorial-chip rounded-full px-3 py-1 text-xs text-textSecondary">{item}</span>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-4">
          {highlight ? <span className="rounded-full border border-accent/40 bg-accent/15 px-2 py-1 text-[10px] uppercase text-accent">{copy.topRecommendation}</span> : null}
          <Gauge score={recommendation.suitability_score} />
        </div>
      </div>

      <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.3 }} transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }} className="mt-4 h-64 w-full rounded-xl border border-white/10 p-2 apti-shimmer">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData} outerRadius="72%">
            <PolarGrid stroke="rgba(140,140,140,0.22)" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#8a8f98', fontSize: 11 }} />
            <PolarRadiusAxis domain={[0, 100]} tick={{ fill: '#8a8f98', fontSize: 10 }} />
            <Radar name="User" dataKey="user" stroke="#27a644" fill="#27a644" fillOpacity={0.22} />
            <Radar name="Major" dataKey="major" stroke="#7170ff" fill="#7170ff" fillOpacity={0.2} />
            <Tooltip />
          </RadarChart>
        </ResponsiveContainer>
      </motion.div>

      <div className="mt-4 grid gap-3 lg:grid-cols-2">
        <RichList title={copy.strengths} items={recommendation.strength_signals} />
        <RichList title={copy.tradeoffs} items={recommendation.tradeoffs} />
        <RichList title={copy.careerPaths} items={recommendation.career_paths} />
        <RichList title={copy.alternateMajors} items={recommendation.alternative_majors} />
      </div>

      <motion.button type="button" className="apti-secondary-button apti-interactive-lift mt-4 inline-flex items-center gap-2 rounded-lg px-3 py-2 text-xs text-textSecondary" onClick={() => setOpen((prev) => !prev)} whileTap={{ scale: 0.985 }}>
        {copy.whyThis}
        <motion.span animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown size={14} />
        </motion.span>
      </motion.button>

      <AnimatePresence initial={false}>
        {open ? (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
            <div className="mt-3 space-y-2 rounded-xl border border-white/10 p-3">
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
                <p className="text-xs text-textMuted">{copy.waitingExplainability}</p>
              )}
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </motion.article>
  );
}
