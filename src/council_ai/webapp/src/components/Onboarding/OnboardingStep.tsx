/**
 * OnboardingStep Component - Individual step in onboarding wizard
 */
import React, { ReactNode } from 'react';
import './OnboardingWizard.css';

interface OnboardingStepProps {
  title: string;
  description?: string;
  children: ReactNode;
  onNext?: () => void;
  onPrevious?: () => void;
  onSkip?: () => void;
  showNext?: boolean;
  showPrevious?: boolean;
  showSkip?: boolean;
  nextLabel?: string;
  previousLabel?: string;
  skipLabel?: string;
}

const OnboardingStep: React.FC<OnboardingStepProps> = ({
  title,
  description,
  children,
  onNext,
  onPrevious,
  onSkip,
  showNext = true,
  showPrevious = true,
  showSkip = true,
  nextLabel = 'Next',
  previousLabel = 'Back',
  skipLabel = 'Skip for now',
}) => {
  return (
    <div className="onboarding-step">
      <div className="onboarding-step-content">
        <h2 className="onboarding-step-title">{title}</h2>
        {description && <p className="onboarding-step-description">{description}</p>}
        <div className="onboarding-step-body">{children}</div>
      </div>
      <div className="onboarding-step-actions">
        {showSkip && (
          <button type="button" className="btn btn-minimal" onClick={onSkip}>
            {skipLabel}
          </button>
        )}
        <div className="onboarding-step-nav">
          {showPrevious && (
            <button type="button" className="btn btn-secondary" onClick={onPrevious}>
              {previousLabel}
            </button>
          )}
          {showNext && (
            <button type="button" className="btn btn-primary" onClick={onNext}>
              {nextLabel}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default OnboardingStep;
