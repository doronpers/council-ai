/**
 * Onboarding Context - Manages onboarding state and progress
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface OnboardingContextType {
  isOnboarding: boolean;
  currentStep: number;
  totalSteps: number;
  completedSteps: Set<number>;
  startOnboarding: () => void;
  completeOnboarding: () => void;
  skipOnboarding: () => void;
  goToStep: (step: number) => void;
  nextStep: () => void;
  previousStep: () => void;
  markStepComplete: (step: number) => void;
  isStepComplete: (step: number) => boolean;
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);

const ONBOARDING_STORAGE_KEY = 'council-onboarding-completed';
const ONBOARDING_PROGRESS_KEY = 'council-onboarding-progress';

export const OnboardingProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isOnboarding, setIsOnboarding] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  const totalSteps = 6; // Welcome, Provider, Config, Domain, Personas, First Consultation

  // Load onboarding state from localStorage
  useEffect(() => {
    try {
      const completed = localStorage.getItem(ONBOARDING_STORAGE_KEY);
      if (completed === 'true') {
        setIsOnboarding(false);
        return;
      }

      // Check if user wants to start onboarding
      const shouldStart = localStorage.getItem('council-start-onboarding');
      if (shouldStart === 'true') {
        setIsOnboarding(true);
        localStorage.removeItem('council-start-onboarding');
      } else {
        // Check if onboarding was never completed
        setIsOnboarding(completed === null);
      }

      // Load progress
      const progress = localStorage.getItem(ONBOARDING_PROGRESS_KEY);
      if (progress) {
        const parsed = JSON.parse(progress);
        setCurrentStep(parsed.currentStep || 0);
        setCompletedSteps(new Set(parsed.completedSteps || []));
      }
    } catch (e) {
      console.warn('Failed to load onboarding state:', e);
    }
  }, []);

  const startOnboarding = () => {
    setIsOnboarding(true);
    setCurrentStep(0);
    setCompletedSteps(new Set());
    try {
      localStorage.removeItem(ONBOARDING_STORAGE_KEY);
      localStorage.setItem(
        ONBOARDING_PROGRESS_KEY,
        JSON.stringify({ currentStep: 0, completedSteps: [] })
      );
    } catch (e) {
      console.warn('Failed to save onboarding state:', e);
    }
  };

  const completeOnboarding = () => {
    setIsOnboarding(false);
    try {
      localStorage.setItem(ONBOARDING_STORAGE_KEY, 'true');
      localStorage.removeItem(ONBOARDING_PROGRESS_KEY);
    } catch (e) {
      console.warn('Failed to save onboarding completion:', e);
    }
  };

  const skipOnboarding = () => {
    completeOnboarding();
  };

  const goToStep = (step: number) => {
    if (step >= 0 && step < totalSteps) {
      setCurrentStep(step);
      try {
        const progress = {
          currentStep: step,
          completedSteps: Array.from(completedSteps),
        };
        localStorage.setItem(ONBOARDING_PROGRESS_KEY, JSON.stringify(progress));
      } catch (e) {
        console.warn('Failed to save onboarding progress:', e);
      }
    }
  };

  const nextStep = () => {
    if (currentStep < totalSteps - 1) {
      goToStep(currentStep + 1);
    } else {
      completeOnboarding();
    }
  };

  const previousStep = () => {
    if (currentStep > 0) {
      goToStep(currentStep - 1);
    }
  };

  const markStepComplete = (step: number) => {
    setCompletedSteps((prev) => {
      const next = new Set(prev);
      next.add(step);
      try {
        const progress = {
          currentStep,
          completedSteps: Array.from(next),
        };
        localStorage.setItem(ONBOARDING_PROGRESS_KEY, JSON.stringify(progress));
      } catch (e) {
        console.warn('Failed to save step completion:', e);
      }
      return next;
    });
  };

  const isStepComplete = (step: number) => {
    return completedSteps.has(step);
  };

  return (
    <OnboardingContext.Provider
      value={{
        isOnboarding,
        currentStep,
        totalSteps,
        completedSteps,
        startOnboarding,
        completeOnboarding,
        skipOnboarding,
        goToStep,
        nextStep,
        previousStep,
        markStepComplete,
        isStepComplete,
      }}
    >
      {children}
    </OnboardingContext.Provider>
  );
};

export const useOnboarding = () => {
  const context = useContext(OnboardingContext);
  if (!context) {
    throw new Error('useOnboarding must be used within OnboardingProvider');
  }
  return context;
};
