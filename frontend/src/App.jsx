// Purpose: Coordinate journey submit, prediction lifecycle, explainability polling, and feedback submission.
// Callers: React root entrypoint.
// Deps: RecommendationJourney, ResultSectionAdvanced, API helpers, explainability hook.
// API: Default exported App component.
// Side effects: Performs prediction, feedback, and explanation polling requests.
import { useEffect, useMemo, useState } from 'react';
import RecommendationJourney from './components/features/RecommendationJourney';
import ResultSectionAdvanced from './components/features/ResultSectionAdvanced';
import useExplainabilityPoll from './hooks/useExplainabilityPoll';
import { pingHealth, predict, submitFeedback } from './lib/api';

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [feedbackState, setFeedbackState] = useState({ loading: false, message: '' });

  const sessionId = result?.session_id || null;
  const explainability = useExplainabilityPoll(sessionId);

  useEffect(() => {
    pingHealth();
  }, []);

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
        setError('Sistem sedang sibuk, coba lagi sebentar');
      } else if (err.status === 422) {
        setError('Input tidak valid, periksa kembali nilai yang kamu masukkan');
      } else if (err.status === 500) {
        setError('Terjadi kesalahan pada sistem');
      } else {
        setError('Terjadi kesalahan. Coba lagi beberapa saat.');
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
      setFeedbackState({ loading: false, message: 'Feedback tersimpan. Terima kasih!' });
    } catch {
      setFeedbackState({ loading: false, message: 'Gagal menyimpan feedback. Coba lagi.' });
    }
  };

  const wrapperClass = useMemo(
    () => 'min-h-screen w-full bg-bg px-4 py-10 text-textPrimary sm:px-6 lg:px-8',
    []
  );

  return (
    <main className={wrapperClass}>
      <div className="mx-auto flex w-full max-w-6xl flex-col items-center gap-6">
        {!result ? (
          <RecommendationJourney onSubmit={submitForm} loading={loading} error={error} />
        ) : (
          <ResultSectionAdvanced
            result={result}
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
      </div>
    </main>
  );
}
