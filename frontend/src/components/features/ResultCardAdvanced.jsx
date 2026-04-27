// Purpose: Render advanced recommendation card with animated score gauge, prodi metadata, radar chart, and explainability accordion.
// Callers: ResultSectionAdvanced component.
// Deps: recharts, framer-motion, lucide-react.
// API: Props recommendation, highlight, copy, locale.
// Side effects: None.
import { AnimatePresence, motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Tooltip } from 'recharts';

const subjectMap = {
  en: {
    math: 'Math', general_math: 'Math', basic_math: 'Math', advanced_math: 'Adv Math', physics: 'Physics', chemistry: 'Chem', biology: 'Bio', economics: 'Eco', indonesian: 'Indo', english: 'Eng', sociology: 'Soc', geography: 'Geo', history: 'Hist', anthropology: 'Anth', informatics: 'Info', arts: 'Arts', religion: 'Religion', civics: 'Civics'
  },
  id: {
    math: 'Mat', general_math: 'Mat', basic_math: 'Mat', advanced_math: 'Mat Lanjut', physics: 'Fisika', chemistry: 'Kimia', biology: 'Bio', economics: 'Eko', indonesian: 'B. Indo', english: 'B. Ing', sociology: 'Sos', geography: 'Geo', history: 'Sej', anthropology: 'Antro', informatics: 'Info', arts: 'Seni', religion: 'Agama', civics: 'PPKn'
  }
};

const matchLevelMap = {
  id: {
    'Strong match': 'Sangat cocok',
    'Good match': 'Cocok',
    'Moderate match': 'Cukup cocok',
    'Exploratory match': 'Perlu eksplorasi',
    High: 'Tinggi',
    Medium: 'Sedang',
    Emerging: 'Berkembang'
  },
  en: {}
};

const translate = (value, locale) => matchLevelMap[locale]?.[value] || value;

const idLabels = {
  Medicine: 'Kedokteran', Biology: 'Biologi', Pharmacy: 'Farmasi', Nursing: 'Keperawatan', Nutrition: 'Gizi', 'Public Health': 'Kesehatan Masyarakat', Chemistry: 'Kimia', Statistics: 'Statistika', 'Environmental Science': 'Ilmu Lingkungan', 'Computer Science': 'Ilmu Komputer', 'Informatics Engineering': 'Teknik Informatika', 'Information Systems': 'Sistem Informasi', 'Data Science': 'Sains Data', Mathematics: 'Matematika', Cybersecurity: 'Keamanan Siber', Architecture: 'Arsitektur', Psychology: 'Psikologi', Management: 'Manajemen', Accounting: 'Akuntansi', Finance: 'Keuangan', Law: 'Hukum', Sociology: 'Sosiologi', 'Political Science': 'Ilmu Politik', 'Public Administration': 'Administrasi Publik', 'International Relations': 'Hubungan Internasional', 'Communication Studies': 'Ilmu Komunikasi', 'Communication Science': 'Ilmu Komunikasi', 'English Education': 'Pendidikan Bahasa Inggris', 'Indonesian Language Education': 'Pendidikan Bahasa Indonesia', 'Elementary Teacher Education': 'PGSD', 'Guidance and Counseling': 'Bimbingan Konseling', 'Educational Technology': 'Teknologi Pendidikan', 'Mathematics Education': 'Pendidikan Matematika', 'Biology Education': 'Pendidikan Biologi', 'Economics Education': 'Pendidikan Ekonomi', 'Language Education': 'Pendidikan Bahasa', 'Visual Communication Design': 'Desain Komunikasi Visual', 'Product Design': 'Desain Produk', 'Film and Television': 'Film dan Televisi', 'Fine Arts': 'Seni Rupa', Music: 'Musik', Animation: 'Animasi', 'Creative Media': 'Media Kreatif', 'Civil Engineering': 'Teknik Sipil', 'Electrical Engineering': 'Teknik Elektro', 'Mechanical Engineering': 'Teknik Mesin', 'Industrial Engineering': 'Teknik Industri', 'Digital Business': 'Bisnis Digital', Entrepreneurship: 'Kewirausahaan', 'Business Administration': 'Administrasi Bisnis', 'Development Economics': 'Ekonomi Pembangunan', 'Indonesian Literature': 'Sastra Indonesia', 'English Literature': 'Sastra Inggris', 'Japanese Literature': 'Sastra Jepang', 'French Literature': 'Sastra Prancis', Linguistics: 'Linguistik', Anthropology: 'Antropologi', 'Translation Studies': 'Studi Penerjemahan', 'Islamic Education': 'Pendidikan Agama Islam', 'Islamic Studies': 'Studi Islam', Theology: 'Teologi', 'Christian Religious Education': 'Pendidikan Agama Kristen', 'Catholic Religious Education': 'Pendidikan Agama Katolik', 'Religious Studies': 'Studi Agama',
  'Health / Natural Science': 'Kesehatan / Sains Alam', 'STEM / Technology': 'STEM / Teknologi', 'Business / Economy': 'Bisnis / Ekonomi', 'Social / Humanities': 'Sosial / Humaniora', 'Language / Culture': 'Bahasa / Budaya', Creative: 'Kreatif', Education: 'Pendidikan', 'Religion-related': 'Keagamaan',
  Technology: 'Teknologi', Environment: 'Lingkungan', Engineering: 'Rekayasa', Business: 'Bisnis', Social: 'Sosial', Technical: 'Teknis', Numbers: 'Angka', People: 'Orang', Creativity: 'Kreativitas', Independent: 'Mandiri', Teamwork: 'Kerja tim', 'General exploration': 'Eksplorasi umum', 'Flexible approach': 'Pendekatan fleksibel',
  'Biology-led mastery': 'Kekuatan utama di Biologi', 'Patient impact': 'Dampak langsung ke pasien', 'Long-term commitment': 'Butuh komitmen jangka panjang', 'Long education path': 'Jalur pendidikan panjang', 'High emotional load': 'Beban emosional tinggi', 'Chemistry precision': 'Ketelitian kimia', 'Health systems relevance': 'Relevan dengan sistem kesehatan', 'Regulatory awareness': 'Peka terhadap aturan dan standar', 'Detail-heavy study load': 'Beban studi sangat detail', 'Scientific observation': 'Observasi ilmiah', 'Health and environment overlap': 'Irisan kesehatan dan lingkungan', 'Career path often needs specialization': 'Jalur karier sering butuh spesialisasi', 'Logic-heavy problem solving': 'Pemecahan masalah berbasis logika', 'Systems thinking': 'Berpikir sistem', 'Build orientation': 'Suka membangun solusi', 'Requires sustained technical depth': 'Butuh pendalaman teknis konsisten', 'Needs comfort with iteration': 'Perlu nyaman dengan proses iterasi', 'Technology + business bridge': 'Jembatan teknologi dan bisnis', 'Process design': 'Desain proses', 'Decision support': 'Pendukung keputusan', 'Less purely technical than computer science': 'Tidak seteknis ilmu komputer murni', 'Applied physics': 'Fisika terapan', 'Structured planning': 'Perencanaan terstruktur', 'Long-horizon thinking': 'Berpikir jangka panjang', 'Field-work heavy in many roles': 'Banyak peran melibatkan kerja lapangan', 'Technical depth': 'Kedalaman teknis', Precision: 'Presisi', 'Applied mathematics': 'Matematika terapan', 'Steep quantitative curve': 'Kurva kuantitatif cukup curam', 'Abstract reasoning': 'Penalaran abstrak', 'Pattern detection': 'Deteksi pola', 'High transferability': 'Mudah diterapkan lintas bidang', 'Theory can feel demanding': 'Teori bisa terasa menantang', 'People insight': 'Pemahaman manusia', Listening: 'Kemampuan mendengar', 'Behavior analysis': 'Analisis perilaku', 'Needs strong empathy + patience': 'Butuh empati dan kesabaran kuat', 'Narrative clarity': 'Kejelasan narasi', 'Audience awareness': 'Peka terhadap audiens', 'Media fluency': 'Melek media', 'Portfolio and execution matter a lot': 'Portofolio dan eksekusi sangat penting', 'Argument quality': 'Kualitas argumentasi', 'Reading stamina': 'Daya tahan membaca', 'Public reasoning': 'Penalaran publik', 'Text-heavy and competitive': 'Banyak teks dan kompetitif', 'Language fluency': 'Kefasihan bahasa', 'Guiding others': 'Membimbing orang lain', 'Structured communication': 'Komunikasi terstruktur', 'Strong fit if teaching energy is real': 'Cocok jika energi mengajar kuat', 'Business judgment': 'Pertimbangan bisnis', Coordination: 'Koordinasi', Adaptability: 'Adaptif', 'Needs self-direction to stand out': 'Butuh inisiatif agar menonjol', 'Numerical consistency': 'Konsistensi numerik', 'Detail discipline': 'Disiplin detail', 'Business relevance': 'Relevan dengan bisnis', 'Precision work can feel repetitive': 'Pekerjaan presisi bisa repetitif', 'Creative execution': 'Eksekusi kreatif', 'Visual communication': 'Komunikasi visual', 'Portfolio building': 'Membangun portofolio', 'Output quality and practice matter a lot': 'Kualitas karya dan latihan sangat penting', 'This major may require extra exploration because detailed program metadata is limited.': 'Jurusan ini perlu eksplorasi tambahan karena metadata program masih terbatas.',
  Doctor: 'Dokter', 'Clinical Researcher': 'Peneliti klinis', 'Healthcare Leader': 'Pemimpin layanan kesehatan', Pharmacist: 'Apoteker', 'Drug Safety Specialist': 'Spesialis keamanan obat', 'Clinical Support': 'Pendukung klinis', 'Research Assistant': 'Asisten peneliti', 'Lab Analyst': 'Analis laboratorium', 'Environmental Scientist': 'Ilmuwan lingkungan', 'Software Engineer': 'Software Engineer', 'AI Engineer': 'AI Engineer', 'Product Analyst': 'Analis produk', 'Business Analyst': 'Analis bisnis', 'Systems Consultant': 'Konsultan sistem', 'Product Operations': 'Operasi produk', 'Project Engineer': 'Project Engineer', 'Infrastructure Planner': 'Perencana infrastruktur', 'Site Engineer': 'Site Engineer', 'Controls Engineer': 'Controls Engineer', 'Power Systems Engineer': 'Insinyur sistem tenaga', 'Embedded Engineer': 'Embedded Engineer', 'Quant Analyst': 'Analis kuantitatif', 'Data Scientist': 'Data Scientist', 'Actuarial Analyst': 'Analis aktuaria', Counselor: 'Konselor', 'HR Specialist': 'Spesialis HR', 'Behavior Researcher': 'Peneliti perilaku', Strategist: 'Strategis', 'PR Specialist': 'Spesialis PR', 'Content Lead': 'Pemimpin konten', Lawyer: 'Pengacara', 'Policy Analyst': 'Analis kebijakan', 'Compliance Officer': 'Compliance Officer', Teacher: 'Guru', 'Curriculum Developer': 'Pengembang kurikulum', 'Language Trainer': 'Pelatih bahasa', 'Brand Associate': 'Brand Associate', 'Business Development': 'Business Development', 'Operations Lead': 'Pemimpin operasional', Auditor: 'Auditor', 'Finance Analyst': 'Analis keuangan', 'Tax Associate': 'Staf pajak', Designer: 'Desainer', 'Art Director': 'Art Director', 'Brand Visual Strategist': 'Strategis visual merek', 'Program coordinator': 'Koordinator program'
};

const subjectAliases = { mathematics: 'general_math', mathematics_advanced: 'advanced_math', bahasa_indonesia: 'indonesian', arts_culture: 'arts', religion_ethics: 'religion' };
const reverseAliases = Object.fromEntries(Object.entries(subjectAliases).map(([source, target]) => [target, source]));
const readScore = (scores, key) => Number(scores[key] ?? scores[subjectAliases[key]] ?? scores[reverseAliases[key]] ?? 0);

const localizeText = (text, locale) => {
  if (locale !== 'id' || !text) return text;
  if (text.startsWith('Track:')) return text.replace('Track:', 'Jalur:');
  if (text.startsWith('Interest focus:')) return `Fokus minat: ${localizeText(text.replace('Interest focus:', '').trim(), locale)}`;
  if (text.startsWith('Preference:')) return `Preferensi: ${localizeText(text.replace('Preference:', '').trim(), locale)}`;
  if (text.startsWith('Electives:')) return text.replace('Electives:', 'Mapel pilihan:');
  return idLabels[text]
    || text.replace('stands out because your strongest academic signal is', 'menonjol karena sinyal akademik terkuatmu adalah')
      .replace('and it aligns with your interest in', 'dan selaras dengan minatmu pada')
      .replace('Academic fit contributes', 'Kecocokan akademik menyumbang')
      .replace('based on major-relevant subjects.', 'berdasarkan mapel yang relevan dengan jurusan.')
      .replace('Interest fit reflects your stated focus:', 'Kecocokan minat mencerminkan fokusmu:')
      .replace('is above this major benchmark by', 'di atas patokan jurusan ini sebesar')
      .replace('is near this major benchmark by', 'dekat dengan patokan jurusan ini, selisih')
      .replace('points.', 'poin.');
};

const flattenListItem = (item) => {
  if (item === null || item === undefined || item === '') return [];
  if (Array.isArray(item)) return item.flatMap(flattenListItem);
  if (typeof item === 'object') {
    if (Array.isArray(item.subjects)) return item.subjects.flatMap(flattenListItem);
    if (item.raw || item.key) return [item.raw || item.key];
    return Object.values(item).flatMap(flattenListItem);
  }
  return [String(item)];
};

const localizeList = (items, locale) => flattenListItem(items).map((item) => localizeText(item, locale));

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
  const safeScore = Number(score);
  const target = Number.isFinite(safeScore) ? Math.min(100, Math.max(0, safeScore)) : 0;
  const animated = useAnimatedNumber(target);
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

function buildRadarData(recommendation, locale) {
  const req = recommendation.major_requirements || {};
  const user = recommendation.user_scores || {};
  const labels = subjectMap[locale] || subjectMap.en;
  const keys = Array.from(new Set([...Object.keys(req), ...Object.keys(user)]))
    .map((key) => ({
      key,
      user: readScore(user, key),
      major: Number(req[key] || 0),
      delta: Math.abs(readScore(user, key) - Number(req[key] || 0))
    }))
    .filter((item) => item.user > 0 || item.major > 0)
    .sort((a, b) => (b.major + b.delta) - (a.major + a.delta))
    .slice(0, 6);

  return keys.map((item) => ({
    subject: labels[item.key] || item.key,
    user: item.user,
    major: item.major
  }));
}

function RadarTooltip({ active, payload, label, locale }) {
  if (!active || !payload?.length) return null;
  const userLabel = locale === 'id' ? 'Nilaimu' : 'Your score';
  const majorLabel = locale === 'id' ? 'Patokan jurusan' : 'Major benchmark';
  return (
    <div className="rounded-xl border border-white/15 bg-[rgba(15,18,28,0.92)] px-3 py-2 text-xs text-textPrimary shadow-xl backdrop-blur">
      <p className="font-semibold">{label}</p>
      <p className="mt-1 text-emerald-300">{userLabel}: {payload.find((item) => item.dataKey === 'user')?.value ?? 0}</p>
      <p className="text-indigo-300">{majorLabel}: {payload.find((item) => item.dataKey === 'major')?.value ?? 0}</p>
    </div>
  );
}

function RichList({ title, items }) {
  const list = Array.isArray(items) ? items : items ? [items] : [];
  if (!list.length) return null;
  return (
    <div className="space-y-2 rounded-xl border border-white/10 p-3">
      <p className="text-[11px] uppercase tracking-[0.18em] text-textSubtle">{title}</p>
      <ul className="space-y-1 text-sm text-textMuted">
        {list.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function DetailPill({ label, value }) {
  if (value === undefined || value === null || value === '') return null;
  return (
    <span className="editorial-chip rounded-full px-3 py-1 text-[11px] text-textSecondary">
      {label}: {value}
    </span>
  );
}

export default function ResultCardAdvanced({ recommendation, highlight, copy, locale = 'en', fallbackUsed = false }) {
  const [open, setOpen] = useState(false);
  const radarData = useMemo(() => buildRadarData(recommendation, locale), [recommendation, locale]);
  const gaugeScore = recommendation.suitability_score ?? recommendation.match_score ?? recommendation.fit_score ?? recommendation.score ?? 0;
  const prodiName = recommendation.nama_prodi || recommendation.major;
  const prodiMeta = [
    ['Prodi ID', recommendation.prodi_id],
    [locale === 'id' ? 'Kelompok prodi' : 'Prodi group', recommendation.kelompok_prodi],
    [locale === 'id' ? 'Rumpun ilmu' : 'Knowledge cluster', recommendation.rumpun_ilmu]
  ];
  const shapEntries = Object.entries(recommendation.shap_values || {})
    .map(([feature, value]) => [feature, Number(value)])
    .filter(([, value]) => Number.isFinite(value))
    .sort((a, b) => b[1] - a[1]);

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
            <h3 className="mt-1 text-xl font-semibold text-textPrimary">{localizeText(prodiName, locale)}</h3>
            <p className="mt-1 text-sm text-textMuted">{localizeText(recommendation.cluster || recommendation.kelompok_prodi || recommendation.rumpun_ilmu, locale)}</p>
          </div>
          <p className="max-w-xl text-sm leading-relaxed text-textMuted">{localizeText(Array.isArray(recommendation.explanation) ? recommendation.explanation[0] : recommendation.explanation || recommendation.reason || recommendation.summary, locale)}</p>
          <div className="flex flex-wrap gap-2">
            <DetailPill label={copy.confidence || 'Confidence'} value={translate(recommendation.confidence_label || recommendation.confidence, locale)} />
            <DetailPill label={copy.matchLevel || copy.matchScore || 'Match'} value={translate(recommendation.match_level, locale)} />
            <DetailPill label={copy.fallback || 'Fallback'} value={recommendation.fallback_reason || recommendation.fallback} />
            <DetailPill label={copy.notes || 'Notes'} value={recommendation.notes || recommendation.note} />
            {prodiMeta.map(([label, value]) => <DetailPill key={label} label={label} value={value} />)}
          </div>
          <div className="flex flex-wrap gap-2">
            {(recommendation.fit_summary || []).map((item) => (
              <span key={item} className="editorial-chip rounded-full px-3 py-1 text-xs text-textSecondary">{localizeText(item, locale)}</span>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-4">
          {highlight ? <span className="rounded-full border border-accent/40 bg-accent/15 px-2 py-1 text-[10px] uppercase text-accent">{copy.topRecommendation}</span> : null}
          <Gauge score={gaugeScore} />
        </div>
      </div>

      <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.3 }} transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }} className="mt-4 h-80 w-full rounded-xl border border-white/10 p-2 apti-shimmer">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData} outerRadius="82%">
            <PolarGrid stroke="rgba(140,140,140,0.28)" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#6f7480', fontSize: 12 }} />
            <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
            <Radar name={locale === 'id' ? 'Nilaimu' : 'Your score'} dataKey="user" stroke="#16a34a" fill="#16a34a" fillOpacity={0.34} strokeWidth={2} />
            <Radar name={locale === 'id' ? 'Patokan jurusan' : 'Major benchmark'} dataKey="major" stroke="#6366f1" fill="#6366f1" fillOpacity={0.28} strokeWidth={2} />
            <Tooltip content={<RadarTooltip locale={locale} />} />
          </RadarChart>
        </ResponsiveContainer>
      </motion.div>

      <div className="mt-4 grid gap-3 lg:grid-cols-2">
        <RichList title={copy.strengths} items={localizeList(recommendation.strength_signals, locale)} />
        <RichList title={copy.tradeoffs} items={localizeList(recommendation.tradeoffs, locale)} />
        <RichList title={copy.careerPaths} items={localizeList(recommendation.career_paths, locale)} />
        <RichList title={copy.alternateMajors} items={localizeList(recommendation.alternative_majors, locale)} />
        <RichList title={locale === 'id' ? 'Mapel pendukung' : 'Supporting subjects'} items={localizeList(recommendation.supporting_subjects, locale)} />
        <RichList title={locale === 'id' ? 'Alasan spesifik' : 'Specific reason'} items={localizeList(recommendation.why_specific, locale)} />
        <RichList title={locale === 'id' ? 'Celah keterampilan' : 'Skill gaps'} items={localizeList(recommendation.skill_gaps, locale)} />
        <RichList title="LLM review" items={localizeList(recommendation.llm_review, locale)} />
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
                <p className="text-xs text-textMuted">{fallbackUsed ? (locale === 'id' ? 'Penjelasan berbasis aturan digunakan saat model belum siap.' : 'Rule-based explanation used while the model is not ready.') : copy.waitingExplainability}</p>
              )}
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </motion.article>
  );
}
