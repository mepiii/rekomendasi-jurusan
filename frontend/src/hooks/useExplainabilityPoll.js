// Purpose: Poll explanations endpoint until explanation rows become ready for active session.
// Callers: App component.
// Deps: React hooks, api.fetchExplanations.
// API: useExplainabilityPoll(sessionId) returns explanations state and control handlers.
// Side effects: Starts/stops polling interval and performs network requests.
import { useCallback, useEffect, useRef, useState } from 'react';
import { fetchExplanations } from '../lib/api';

export default function useExplainabilityPoll(sessionId) {
  const [state, setState] = useState({ loading: false, ready: false, explanations: [] });
  const intervalRef = useRef(null);

  const stop = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const load = useCallback(async () => {
    if (!sessionId) return;
    try {
      const data = await fetchExplanations(sessionId);
      setState({
        loading: false,
        ready: Boolean(data.ready),
        explanations: data.explanations || []
      });
      if (data.ready) stop();
    } catch {
      setState((prev) => ({ ...prev, loading: false }));
      stop();
    }
  }, [sessionId, stop]);

  useEffect(() => {
    stop();

    if (!sessionId) {
      setState({ loading: false, ready: false, explanations: [] });
      return undefined;
    }

    setState({ loading: true, ready: false, explanations: [] });
    load();

    intervalRef.current = setInterval(load, 1500);
    return () => stop();
  }, [sessionId, load, stop]);

  return {
    ...state,
    refresh: load,
    stop
  };
}
