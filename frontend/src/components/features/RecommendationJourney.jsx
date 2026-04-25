// Purpose: Present schema-driven recommendation intake across curriculum, subjects, prodi context, preferences, and review.
// Callers: App component.
// Deps: React, framer-motion, recommendation config, i18n copy.
// API: Props onSubmit(payload), loading, error, helperCopy, locale, copy.
// Side effects: Emits normalized payload to parent submit handler.
import { AnimatePresence, motion } from 'framer-motion';
import { useMemo, useState } from 'react';
import { buildInitialScores, interestOptions, preferenceGroups, prodiIntakeSteps, religionRelatedMajorPreferences, trackConfig } from '../../lib/recommendationConfig';

const stepMotion = {
  initial: { opacity: 0, y: 26, scale: 0.985, filter: 'blur(10px)' },
  animate: { opacity: 1, y: 0, scale: 1, filter: 'blur(0px)' },
  exit: { opacity: 0, y: -18, scale: 0.99, filter: 'blur(8px)' },
  transition: { duration: 0.42, ease: [0.16, 1, 0.3, 1] }
};

const staggerMotion = {
  animate: {
    transition: {
      staggerChildren: 0.06,
      delayChildren: 0.04
    }
  }
};

const itemMotion = {
  initial: { opacity: 0, y: 14 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.28, ease: [0.25, 1, 0.5, 1] }
};

const buttonTap = { whileTap: { scale: 0.985 } };

const cardHover = {
  whileHover: { y: -3 },
  transition: { duration: 0.22, ease: [0.25, 1, 0.5, 1] }
};

const chipHover = {
  whileHover: { y: -2, scale: 1.01 },
  transition: { duration: 0.18, ease: [0.25, 1, 0.5, 1] }
};

const groupLabels = {
  en: {
    orientation: 'What feels most natural?',
    approach: 'What kind of problems attract you?',
    style: 'How do you like to work?'
  },
  id: {
    orientation: 'Apa yang terasa paling natural?',
    approach: 'Masalah seperti apa yang paling menarik?',
    style: 'Bagaimana cara kerja yang kamu suka?'
  }
};

const toList = (value) => value.split(',').map((item) => item.trim()).filter(Boolean);
const toContext = (value) => ({ note: value.trim() });

function generateSessionId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function GlassCard({ children }) {
  return <div className="glass-panel editorial-shell w-full max-w-4xl rounded-[28px] border p-6 sm:p-8">{children}</div>;
}

function StepIndicator({ step, labels }) {
  return (
    <div className="mb-8 flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.24em] text-textSubtle">
      {labels.map((label, idx) => {
        const active = idx + 1 === step;
        return (
          <div
            key={label}
            className={`editorial-chip rounded-full px-3 py-1.5 ${active ? 'border-accent/30 bg-accent/10 text-accent' : 'text-textSubtle'}`}
          >
            {label}
          </div>
        );
      })}
    </div>
  );
}

function SubjectField({ label, value, onChange, error, optional }) {
  return (
    <label className="apti-field-enter flex flex-col gap-1">
      <span className="text-sm text-textSecondary">
        {label}
        {optional ? <span className="ml-1 text-textSubtle">(optional)</span> : null}
      </span>
      <input
        type="number"
        min="0"
        max="100"
        value={value}
        onChange={onChange}
        className={`glass-input rounded-xl px-3 py-2 text-sm text-textPrimary outline-none ${error ? 'border-danger' : 'focus:border-accent'}`}
      />
      {error ? <span className="text-xs text-danger">{error}</span> : null}
    </label>
  );
}

function ProdiTextStep({ config, value, onChange, error, locale }) {
  const label = config.label[locale] || config.label.en;
  const selectedValues = toList(value);
  const handleOptionClick = (optionValue) => {
    if (config.optionMode === 'append') {
      const next = selectedValues.includes(optionValue) ? selectedValues.filter((item) => item !== optionValue) : [...selectedValues, optionValue];
      onChange(config.key, next.join(', '));
      return;
    }
    onChange(config.key, value === optionValue ? '' : optionValue);
  };

  return (
    <motion.div key={config.key} {...stepMotion} className="space-y-4">
      <div className="editorial-shell rounded-[22px] border p-4">
        <div className="flex flex-col gap-3">
          <span className="text-sm text-textSecondary">
            {label}
            {!config.required ? <span className="ml-1 text-textSubtle">({locale === 'id' ? 'opsional' : 'optional'})</span> : null}
          </span>
          <span className="text-xs leading-5 text-textSubtle">{config.helper[locale] || config.helper.en}</span>
          {config.options?.length ? (
            <div className="flex flex-wrap gap-2">
              {config.options.map((option) => {
                const active = config.optionMode === 'append' ? selectedValues.includes(option.value) : value === option.value;
                return (
                  <motion.button
                    key={option.value}
                    type="button"
                    aria-pressed={active}
                    onClick={() => handleOptionClick(option.value)}
                    className={`editorial-chip apti-interactive-lift rounded-full px-3 py-1 text-xs transition ${active ? 'apti-choice-active border-accent/30 bg-accent/10 text-accent' : 'apti-choice-idle hover:border-accent/40 hover:text-textPrimary'}`}
                    {...chipHover}
                    {...buttonTap}
                  >
                    {option.label[locale] || option.label.en}
                  </motion.button>
                );
              })}
            </div>
          ) : null}
          <textarea
            aria-label={label}
            value={value}
            onChange={(event) => onChange(config.key, event.target.value)}
            className={`glass-input min-h-24 rounded-xl px-3 py-2 text-sm text-textPrimary outline-none ${error ? 'border-danger' : 'focus:border-accent'}`}
            placeholder={config.placeholder[locale] || config.placeholder.en}
          />
        </div>
        {error ? <span className="mt-2 block text-xs text-danger">{error}</span> : null}
      </div>
    </motion.div>
  );
}

export default function RecommendationJourney({ onSubmit, loading, error, helperCopy, locale = 'en', copy }) {
  const [step, setStep] = useState(1);
  const [trackKey, setTrackKey] = useState('IPA');
  const [scores, setScores] = useState(() => buildInitialScores('IPA'));
  const [selectedElectives, setSelectedElectives] = useState([]);
  const [interests, setInterests] = useState([]);
  const [preferences, setPreferences] = useState({ orientation: '', approach: '', style: '' });
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [religionRelatedMajorPreference, setReligionRelatedMajorPreference] = useState('Not relevant');
  const [prodiContext, setProdiContext] = useState(() => Object.fromEntries(prodiIntakeSteps.map(({ key }) => [key, ''])));
  const [errors, setErrors] = useState({});

  const track = trackConfig[trackKey];
  const localizedGroupLabels = groupLabels[locale] || groupLabels.en;
  const hasErrors = useMemo(() => Object.keys(errors).length > 0, [errors]);
  const scoreEntries = useMemo(() => {
    const required = track.requiredSubjects.map(([key, label]) => ({ key, label, optional: false }));
    const optional = track.optionalSubjects?.map(([key, label]) => ({ key, label, optional: true })) || [];
    const electives =
      trackKey === 'Merdeka'
        ? track.electiveSubjects.map(([key, label]) => ({ key, label, optional: !selectedElectives.includes(key), elective: true }))
        : [];
    return [...required, ...optional, ...electives];
  }, [track, trackKey, selectedElectives]);

  const handleTrackChange = (nextTrack) => {
    setTrackKey(nextTrack);
    setScores(buildInitialScores(nextTrack));
    setSelectedElectives([]);
    setErrors({});
  };

  const handleScoreChange = (key, value) => {
    const next = value.replace(/[^0-9.]/g, '');
    setScores((prev) => ({ ...prev, [key]: next }));
  };

  const toggleInterest = (interest) => {
    setInterests((prev) => (prev.includes(interest) ? prev.filter((item) => item !== interest) : [...prev, interest]));
  };

  const toggleElective = (key) => {
    setSelectedElectives((prev) => {
      if (prev.includes(key)) {
        const next = prev.filter((item) => item !== key);
        setScores((current) => ({ ...current, [key]: '' }));
        return next;
      }
      if (prev.length >= 5) return prev;
      return [...prev, key];
    });
  };

  const handleProdiContextChange = (key, value) => {
    setProdiContext((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => {
      if (!prev[key]) return prev;
      const { [key]: _removed, ...rest } = prev;
      return rest;
    });
  };

  const validateProdiStep = (stepNumber = step) => {
    const config = prodiIntakeSteps[stepNumber - 3];
    if (!config?.required || prodiContext[config.key]?.trim()) return true;
    setErrors((prev) => ({ ...prev, [config.key]: locale === 'id' ? `${config.label.id} wajib diisi` : `${config.label.en} is required` }));
    return false;
  };

  const validateProfile = () => {
    const nextErrors = {};
    const validateScore = (key, label, required = false) => {
      const raw = scores[key];
      if (raw === undefined || String(raw).trim() === '') {
        if (required) nextErrors[key] = `${label} ${locale === 'id' ? 'wajib diisi' : 'score is required'}`;
        return;
      }
      const parsed = Number(raw);
      if (Number.isNaN(parsed) || !Number.isFinite(parsed) || parsed < 0 || parsed > 100) {
        nextErrors[key] = `${label} ${locale === 'id' ? 'harus antara 0 sampai 100' : 'score must be between 0 and 100'}`;
      }
    };

    if (!trackKey) nextErrors.trackKey = copy.inputsError;

    for (const [key, label] of track.requiredSubjects) validateScore(key, label, true);
    for (const [key, label] of track.optionalSubjects || []) validateScore(key, label);

    if (trackKey === 'Merdeka') {
      if (selectedElectives.length < 4 || selectedElectives.length > 5) {
        nextErrors.selectedElectives = locale === 'id' ? 'Pilih 4-5 mata pelajaran pilihan' : 'Pick 4-5 elective subjects';
      }
      for (const elective of selectedElectives) {
        const label = track.electiveSubjects.find(([key]) => key === elective)?.[1] || elective;
        validateScore(elective, label, true);
      }
    }

    if (interests.length < 3) nextErrors.interests = locale === 'id' ? 'Pilih minimal 3 minat' : 'Select at least 3 interests';
    if (interests.length > 6) nextErrors.interests = locale === 'id' ? 'Pilih maksimal 6 minat' : 'Select up to 6 interests';

    for (const key of Object.keys(preferences)) {
      if (!preferences[key]) nextErrors[key] = locale === 'id' ? 'Pilih satu opsi' : 'Select one option';
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const goNext = () => {
    if (step === 1) setStep(2);
    if (step === 2 && validateProfile()) setStep(3);
    if (step >= 3 && step < 11 && validateProdiStep(step)) setStep((prev) => prev + 1);
  };

  const goBack = () => {
    setErrors({});
    setStep((prev) => Math.max(1, prev - 1));
  };

  const activeSubjects = Object.fromEntries(
    Object.entries(scores)
      .map(([key, value]) => [key, Number(value)])
      .filter(([key, value]) => Number.isFinite(value) && value >= 0 && value <= 100 && (track.requiredSubjects.some(([subjectKey]) => subjectKey === key) || (track.optionalSubjects || []).some(([subjectKey]) => subjectKey === key) || selectedElectives.includes(key)))
  );

  const averageScore = Object.values(activeSubjects).length
    ? Math.round(Object.values(activeSubjects).reduce((acc, value) => acc + Number(value || 0), 0) / Object.values(activeSubjects).length)
    : 0;

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!validateProfile()) {
      setStep(2);
      return;
    }

    const invalidStep = prodiIntakeSteps.findIndex(({ key, required }) => required && !prodiContext[key]?.trim());
    if (invalidStep >= 0) {
      setStep(invalidStep + 3);
      validateProdiStep(invalidStep + 3);
      return;
    }

    onSubmit({
      session_id: generateSessionId(),
      sma_track: trackKey,
      curriculum_type: track.curriculumType,
      scores: activeSubjects,
      selected_electives: selectedElectives,
      interests,
      preferences: {
        ...preferences,
        religion_related_major_preference: religionRelatedMajorPreference || 'Not relevant'
      },
      religion_related_major_preference: religionRelatedMajorPreference || 'Not relevant',
      academic_context: toContext(prodiContext.academic_context),
      subject_preferences: { preferred: toList(prodiContext.subject_preferences) },
      interest_deep_dive: { note: prodiContext.interest_deep_dive.trim() },
      career_direction: { note: prodiContext.career_direction.trim() },
      constraints: toContext(prodiContext.constraints),
      expected_prodi: prodiContext.expected_prodi.trim() || null,
      prodi_to_avoid: toList(prodiContext.prodi_to_avoid),
      free_text_goal: prodiContext.free_text_goal.trim() || null,
      language: locale,
      top_n: 5
    });
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-4xl">
      <GlassCard>
        <p className="editorial-kicker mb-3 text-xs font-medium uppercase">{copy.journeyKicker}</p>
        <StepIndicator step={step} labels={copy.steps} />
        <div className="mb-8 space-y-3">
          <h1 className="text-2xl font-semibold tracking-tight text-textPrimary sm:text-3xl">{copy.journeyTitle}</h1>
          <p className="max-w-2xl text-sm leading-6 text-textMuted">{helperCopy || copy.journeyHelper}</p>
          <div className="editorial-rule apti-section-divider" />
        </div>

        <AnimatePresence mode="wait">
          {step === 1 ? (
            <motion.div key="step-1" {...stepMotion} variants={staggerMotion} initial="initial" animate="animate" className="space-y-6">
              <div className="space-y-3">
                <p className="text-sm text-textSecondary">{copy.track}</p>
                <div className="grid gap-3 sm:grid-cols-2">
                  {Object.entries(trackConfig).map(([key, config]) => {
                    const active = key === trackKey;
                    return (
                      <motion.button
                        key={key}
                        type="button"
                        aria-pressed={active}
                        onClick={() => handleTrackChange(key)}
                        className={`editorial-chip apti-interactive-lift rounded-2xl px-4 py-4 text-left text-sm transition ${active ? 'apti-choice-active border-accent/30 bg-accent/10 text-accent' : 'apti-choice-idle hover:border-accent/40 hover:text-textPrimary'}`}
                        variants={itemMotion}
                        {...cardHover}
                        {...buttonTap}
                      >
                        <span className="block font-medium">{config.label[locale] || config.label.en}</span>
                        <span className="mt-1 block text-xs text-textMuted">{config.requiredSubjects.length} {copy.subjects.toLowerCase()}</span>
                      </motion.button>
                    );
                  })}
                </div>
              </div>

              {trackKey === 'Merdeka' ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm text-textSecondary">{locale === 'id' ? 'Mata pelajaran pilihan' : 'Elective subjects'}</p>
                    <span className="text-xs text-textSubtle">{selectedElectives.length}/5</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {track.electiveSubjects.map(([key, label]) => {
                      const active = selectedElectives.includes(key);
                      const blocked = !active && selectedElectives.length >= 5;
                      return (
                        <motion.button
                          key={key}
                          type="button"
                          aria-pressed={active}
                          onClick={() => !blocked && toggleElective(key)}
                          className={`editorial-chip apti-interactive-lift rounded-full px-3 py-1 text-xs transition ${active ? 'apti-choice-active border-accent/30 bg-accent/10 text-accent' : 'apti-choice-idle hover:border-accent/40 hover:text-textPrimary'} ${blocked ? 'cursor-not-allowed opacity-40' : ''}`}
                          {...chipHover}
                          {...buttonTap}
                        >
                          {label}
                        </motion.button>
                      );
                    })}
                  </div>
                  {errors.selectedElectives ? <span className="text-xs text-danger">{errors.selectedElectives}</span> : null}
                </div>
              ) : null}
            </motion.div>
          ) : null}

          {step === 2 ? (
            <motion.div key="step-2" {...stepMotion} variants={staggerMotion} initial="initial" animate="animate" className="space-y-6">
              <div className="space-y-3">
                <p className="text-sm text-textSecondary">{copy.subjects}</p>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {scoreEntries
                    .filter((entry) => !entry.elective || selectedElectives.includes(entry.key))
                    .map(({ key, label, optional }) => (
                      <SubjectField
                        key={key}
                        label={label}
                        optional={optional}
                        value={scores[key] || ''}
                        onChange={(event) => handleScoreChange(key, event.target.value)}
                        error={errors[key]}
                      />
                    ))}
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm text-textSecondary">{copy.interests}</p>
                  <span className="text-xs text-textSubtle">{interests.length} {copy.selected}</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {interestOptions.map((interest) => {
                    const active = interests.includes(interest.value);
                    const blocked = !active && interests.length >= 6;
                    return (
                      <motion.button
                        key={interest.value}
                        type="button"
                        aria-pressed={active}
                        onClick={() => !blocked && toggleInterest(interest.value)}
                        className={`editorial-chip apti-interactive-lift rounded-full px-3 py-1 text-xs transition ${active ? 'apti-choice-active border-accent/30 bg-accent/10 text-accent' : 'apti-choice-idle hover:border-accent/40 hover:text-textPrimary'} ${blocked ? 'cursor-not-allowed opacity-40' : ''}`}
                        {...chipHover}
                        {...buttonTap}
                      >
                        {interest.label[locale] || interest.label.en}
                      </motion.button>
                    );
                  })}
                </div>
                {errors.interests ? <span className="text-xs text-danger">{errors.interests}</span> : null}
              </div>

              <div className="space-y-3">
                <p className="text-sm text-textSecondary">{copy.preferences}</p>
                <div className="grid gap-4 lg:grid-cols-3">
                  {Object.entries(preferenceGroups).map(([groupKey, options]) => (
                    <motion.div key={groupKey} variants={itemMotion} className="editorial-shell apti-interactive-lift rounded-2xl border p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-textSubtle">{localizedGroupLabels[groupKey]}</p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {options.map((option) => {
                          const active = preferences[groupKey] === option.value;
                          return (
                            <motion.button
                              key={option.value}
                              type="button"
                              aria-pressed={active}
                              onClick={() => setPreferences((prev) => ({ ...prev, [groupKey]: option.value }))}
                              className={`editorial-chip apti-interactive-lift rounded-full px-3 py-1 text-xs transition ${active ? 'apti-choice-active border-accent/30 bg-accent/10 text-accent' : 'apti-choice-idle hover:border-accent/40 hover:text-textPrimary'}`}
                              {...chipHover}
                              {...buttonTap}
                            >
                              {option.label[locale] || option.label.en}
                            </motion.button>
                          );
                        })}
                      </div>
                      {errors[groupKey] ? <span className="mt-2 block text-xs text-danger">{errors[groupKey]}</span> : null}
                    </motion.div>
                  ))}
                </div>

                <motion.div variants={itemMotion} className="editorial-shell rounded-2xl border p-4">
                  <button type="button" aria-pressed={advancedOpen} onClick={() => setAdvancedOpen((prev) => !prev)} className="flex w-full items-center justify-between gap-3 text-left text-sm text-textSecondary">
                    <span>{locale === 'id' ? 'Preferensi lanjutan' : 'Advanced preferences'}</span>
                    <span className="text-xs text-textSubtle">{advancedOpen ? (locale === 'id' ? 'Tutup' : 'Hide') : (locale === 'id' ? 'Buka' : 'Show')}</span>
                  </button>
                  <AnimatePresence initial={false}>
                    {advancedOpen ? (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                        <div className="mt-3 space-y-2">
                          <p className="text-xs text-textSubtle">{locale === 'id' ? 'Preferensi ini opsional dan default-nya tidak relevan.' : 'This optional preference defaults to not relevant.'}</p>
                          <div className="flex flex-wrap gap-2">
                            {religionRelatedMajorPreferences.map((option) => {
                              const active = religionRelatedMajorPreference === option.value;
                              return (
                                <motion.button
                                  key={option.value}
                                  type="button"
                                  aria-pressed={active}
                                  onClick={() => setReligionRelatedMajorPreference(option.value)}
                                  className={`editorial-chip apti-interactive-lift rounded-full px-3 py-1 text-xs transition ${active ? 'apti-choice-active border-accent/30 bg-accent/10 text-accent' : 'apti-choice-idle hover:border-accent/40 hover:text-textPrimary'}`}
                                  {...chipHover}
                                  {...buttonTap}
                                >
                                  {option.label[locale] || option.label.en}
                                </motion.button>
                              );
                            })}
                          </div>
                        </div>
                      </motion.div>
                    ) : null}
                  </AnimatePresence>
                </motion.div>
              </div>
            </motion.div>
          ) : null}

          {step >= 3 && step <= 10 ? (
            <ProdiTextStep
              config={prodiIntakeSteps[step - 3]}
              value={prodiContext[prodiIntakeSteps[step - 3].key]}
              onChange={handleProdiContextChange}
              error={errors[prodiIntakeSteps[step - 3].key]}
              locale={locale}
            />
          ) : null}

          {step === 11 ? (
            <motion.div key="step-11" {...stepMotion} className="space-y-4">
              <div className="editorial-shell rounded-[22px] border p-4 text-sm text-textMuted">
                <p className="mb-2 text-textSecondary">{copy.profileReview}</p>
                <p>{copy.track}: {track.label[locale] || track.label.en}</p>
                <p>{copy.interests}: {interests.join(', ') || '-'}</p>
                <p>{copy.preferences}: {Object.values(preferences).join(' · ') || '-'}</p>
                <p>{copy.averageScore}: {averageScore || '-'}</p>
                <p>{(prodiIntakeSteps[5].label[locale] || prodiIntakeSteps[5].label.en)}: {prodiContext.expected_prodi || '-'}</p>
                <p>{(prodiIntakeSteps[6].label[locale] || prodiIntakeSteps[6].label.en)}: {prodiContext.prodi_to_avoid || '-'}</p>
              </div>

              <div className="editorial-shell rounded-[22px] border px-4 py-3 text-xs leading-relaxed text-textSubtle">{copy.decisionSupport}</div>
            </motion.div>
          ) : null}
        </AnimatePresence>

        {error ? <div className="mt-4 rounded-xl border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</div> : null}

        <div className="mt-6 flex items-center justify-between gap-3">
          <button type="button" onClick={goBack} disabled={step === 1 || loading} className="apti-secondary-button rounded-xl px-4 py-2 text-sm transition disabled:opacity-40">
            {copy.back}
          </button>

          {step < 11 ? (
            <button type="button" onClick={goNext} className="apti-primary-button px-5 py-2.5 text-sm font-semibold">
              {copy.continue}
            </button>
          ) : (
            <button type="submit" disabled={loading || hasErrors} className="apti-primary-button px-5 py-2.5 text-sm font-semibold disabled:opacity-50">
              {loading ? <span className="apti-button-spinner" aria-hidden="true" /> : null}
              {loading ? copy.analyzing : copy.analyze}
            </button>
          )}
        </div>
      </GlassCard>
    </form>
  );
}
