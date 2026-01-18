/**
 * useOnboarding Hook - Track onboarding completion status
 */
import { useCallback, useEffect, useState } from 'react';

const ONBOARDING_KEY = 'council-ai-onboarding-complete';

export const useOnboarding = () => {
  const [isComplete, setIsComplete] = useState<boolean | null>(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(ONBOARDING_KEY);
      setIsComplete(stored === 'true');
    } catch {
      setIsComplete(false);
    }
  }, []);

  const completeOnboarding = useCallback(() => {
    try {
      localStorage.setItem(ONBOARDING_KEY, 'true');
    } catch {
      // Ignore storage errors
    }
    setIsComplete(true);
  }, []);

  const resetOnboarding = useCallback(() => {
    try {
      localStorage.removeItem(ONBOARDING_KEY);
    } catch {
      // Ignore storage errors
    }
    setIsComplete(false);
  }, []);

  return {
    isComplete,
    completeOnboarding,
    resetOnboarding,
  };
};
