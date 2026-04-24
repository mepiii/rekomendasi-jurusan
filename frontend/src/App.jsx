// Purpose: Coordinate intro-state orchestration, theme persistence, journey submit, prediction lifecycle, and feedback submission.
// Callers: React root entrypoint.
// Deps: Apti shell components, recommendation flow, API helpers, explainability hook, introState and themeState helpers.
// API: Default exported App component.
// Side effects: Performs prediction, feedback, explanation polling, and intro/theme-state persistence.
import { useEffect, useState } from 'react';
import AptiIntroFlow from './components/features/AptiIntroFlow';
import AptiShell from './components/features/AptiShell';
import RecommendationJourney from './components/features/RecommendationJourney';
import ResultSectionAdvanced from './components/features/ResultSectionAdvanced';
import useExplainabilityPoll from './hooks/useExplainabilityPoll';
import { pingHealth, predict, submitFeedback } from './lib/api';
import { clearIntroState, getHelperCopy, loadIntroState, saveIntroState } from './lib/introState';
import { copy, loadLocale, saveLocale } from './lib/i18n';
import { loadTheme, saveTheme, toggleTheme } from './lib/themeState';

const getShellContent = (introState, onRestartIntro, localeCopy) => {
  if (!introState.completed) return { title: '', subtitle: '', actions: null };

  return {
    title:
      introState.name && localeCopy.introFallbackTitle !== 'Selamat datang kembali'
        ? `Welcome back, ${introState.name}`
        : introState.name
          ? `Selamat datang kembali, ${introState.name}`
          : localeCopy.introFallbackTitle,
    subtitle: localeCopy.goals[introState.goal] || localeCopy.goals['find-fit'],
    actions: (
      <button type="button" onClick={onRestartIntro} className="apti-secondary-button rounded-xl px-4 py-2 text-sm text-textSecondary">
        {localeCopy.restartIntro}
      </button>
    )
  };
};

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [feedbackState, setFeedbackState] = useState({ loading: false, message: '' });
  const [introState, setIntroState] = useState(() => loadIntroState());
  const [theme, setTheme] = useState(() => loadTheme());
  const [locale, setLocale] = useState(() => loadLocale());
  const localeCopy = copy[locale];

  const sessionId = result?.session_id || null;
  const explainability = useExplainabilityPoll(sessionId);

  useEffect(() => {
    pingHealth();
  }, []);

  const handleIntroComplete = (nextState) => {
    saveIntroState(nextState);
    setIntroState(nextState);
  };

  const handleRestartIntro = () => {
    clearIntroState();
    explainability.stop();
    setIntroState(loadIntroState());
    setResult(null);
    setError('');
    setFeedbackState({ loading: false, message: '' });
  };

  const handleThemeToggle = () => {
    const nextTheme = toggleTheme(theme);
    saveTheme(nextTheme);
    setTheme(nextTheme);
  };

  const handleLocaleToggle = () => {
    const nextLocale = locale === 'en' ? 'id' : 'en';
    saveLocale(nextLocale);
    setLocale(nextLocale);
  };

  const submitForm = async (payload) => {
    setLoading(true);
    setError('');
    setFeedbackState({ loading: false, message: '' });

    try {
      const response = await predict(payload, 10000);
      const enriched = {
        ...response,
        recommendations: (response.recommendations || []).map((item) => ({
          ...item,
          user_scores: payload.scores
        }))
      };
      setResult(enriched);
    } catch (err) {
      if (err.name === 'AbortError') {
        setError(localeCopy.busyError);
      } else if (err.status === 422) {
        setError(localeCopy.invalidError);
      } else if (err.status === 500) {
        setError(localeCopy.systemError);
      } else {
        setError(localeCopy.genericError);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackSubmit = async (payload) => {
    if (!result?.session_id) return;

    setFeedbackState({ loading: true, message: '' });
    try {
      await submitFeedback({
        session_id: result.session_id,
        ...payload
      });
      setFeedbackState({ loading: false, message: localeCopy.feedbackSaved });
    } catch {
      setFeedbackState({ loading: false, message: localeCopy.feedbackFailed });
    }
  };

  const shellContent = getShellContent(introState, handleRestartIntro, localeCopy);
  const helperCopy = getHelperCopy();

  return (
    <AptiShell
      theme={theme}
      onToggleTheme={handleThemeToggle}
      locale={locale}
      onToggleLocale={handleLocaleToggle}
      copy={localeCopy}
      title={shellContent.title}
      subtitle={shellContent.subtitle}
      actions={shellContent.actions}
    >
      {!introState.completed ? (
        <AptiIntroFlow
          onComplete={handleIntroComplete}
          onSkip={() => handleIntroComplete({ completed: true, name: '', goal: 'find-fit', confidence: '' })}
        />
      ) : !result ? (
        <RecommendationJourney onSubmit={submitForm} loading={loading} error={error} helperCopy={helperCopy} locale={locale} copy={localeCopy} />
      ) : (
        <ResultSectionAdvanced
          result={result}
          locale={locale}
          copy={localeCopy}
          explanations={{
            ready: explainability.ready,
            explanations: explainability.explanations
          }}
          onReset={() => {
            explainability.stop();
            setResult(null);
            setError('');
            setFeedbackState({ loading: false, message: '' });
          }}
          onSubmitFeedback={handleFeedbackSubmit}
          feedbackState={feedbackState}
        />
      )}
    </AptiShell>
  );
}
