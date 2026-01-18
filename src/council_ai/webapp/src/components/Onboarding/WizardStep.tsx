/**
 * WizardStep Component - Wrapper for onboarding steps
 */
import React from 'react';

interface WizardStepProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

const WizardStep: React.FC<WizardStepProps> = ({ title, description, children }) => {
  return (
    <div className="wizard-step">
      <h3 className="wizard-step-title">{title}</h3>
      {description && <p className="wizard-step-description">{description}</p>}
      <div className="wizard-step-content">{children}</div>
    </div>
  );
};

export default WizardStep;
