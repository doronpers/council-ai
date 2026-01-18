/**
 * OnboardingWizard Component - First-time user walkthrough
 */
import React, { useMemo, useState, useCallback } from 'react';
import './OnboardingWizard.css';
import WizardStep from './WizardStep';
import DomainSelect from '../Configuration/DomainSelect';
import ProviderSelect from '../Configuration/ProviderSelect';
import ApiKeyInput from '../Configuration/ApiKeyInput';
import MemberSelectionGrid from '../Members/MemberSelectionGrid';
import QueryInput from '../Consultation/QueryInput';
import PersonalIntegrationStep from './PersonalIntegrationStep';
import { useApp } from '../../context/AppContext';
import { useNotifications } from '../Layout/NotificationContainer';

interface OnboardingWizardProps {
  onComplete: () => void;
  onSkip: () => void;
}

const OnboardingWizard: React.FC<OnboardingWizardProps> = ({ onComplete, onSkip }) => {
  const [stepIndex, setStepIndex] = useState(0);
  const [validationErrors, setValidationErrors] = useState<Record<number, string[]>>({});
  const [isTestingConfig, setIsTestingConfig] = useState(false);
  const { settings, saveSettings } = useApp();
  const { showNotification } = useNotifications();

  // Validation functions
  const validateStep = useCallback(
    async (step: number): Promise<string[]> => {
      const errors: string[] = [];

      switch (step) {
        case 1: // Domain selection
          if (!settings.domain) {
            errors.push('Please select a domain to continue.');
          }
          break;

        case 2: // Member selection
          // Check if at least one member is selected
          if (!settings.members || settings.members.length === 0) {
            errors.push('Please select at least one council member.');
          }
          break;

        case 3: // Provider and API key
          if (!settings.provider) {
            errors.push('Please select an AI provider.');
          }

          // Check if API key is configured (either in settings or environment)
          const hasApiKey =
            settings.api_key ||
            (settings.provider &&
              (process.env[`${settings.provider.toUpperCase()}_API_KEY`] ||
                process.env.COUNCIL_API_KEY));

          if (!hasApiKey) {
            errors.push(
              `Please provide an API key for ${settings.provider || 'your selected provider'}.`
            );
          }

          // Validate API key format (basic check)
          if (settings.api_key && settings.api_key.includes('your-')) {
            errors.push('Please replace the placeholder API key with your actual key.');
          }
          break;

        case 4: // Personal integration (optional, no validation needed)
          break;

        case 5: // Query input
          if (!settings.query || settings.query.trim().length === 0) {
            errors.push('Please enter a question for the council.');
          } else if (settings.query.trim().length < 10) {
            errors.push('Please provide a more detailed question (at least 10 characters).');
          }
          break;
      }

      return errors;
    },
    [settings]
  );

  // Test configuration by making a small API call
  const testConfiguration = useCallback(async () => {
    if (!settings.provider || !settings.api_key) {
      showNotification('Provider and API key are required for testing', 'error');
      return;
    }

    setIsTestingConfig(true);
    try {
      // Make a simple test request
      const response = await fetch('/api/consult', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'Hello',
          provider: settings.provider,
          api_key: settings.api_key,
          members: ['rams'], // Just test with one member
          mode: 'individual',
        }),
      });

      if (response.ok) {
        showNotification('Configuration test successful!', 'success');
      } else {
        const error = await response.json();
        showNotification(`Configuration test failed: ${error.detail || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      showNotification('Configuration test failed: Network error', 'error');
    } finally {
      setIsTestingConfig(false);
    }
  }, [settings, showNotification]);

  const steps = useMemo(
    () => [
      {
        title: 'Welcome to Council AI',
        description:
          'Set up your council in a few quick steps. You can skip this and configure later.',
        content: (
          <div className="wizard-intro">
            <p>
              Council AI helps you get advice from multiple expert personas at once. Pick a domain,
              choose members, and ask your question.
            </p>
            <ul>
              <li>Select a domain to load recommended personas</li>
              <li>Choose members to include in the council</li>
              <li>Configure your LLM provider</li>
            </ul>
          </div>
        ),
      },
      {
        title: 'Choose a domain',
        description: 'Domains preload recommended personas and modes.',
        content: <DomainSelect />,
      },
      {
        title: 'Select council members',
        description: 'Pick the personas that should respond to your query.',
        content: <MemberSelectionGrid />,
      },
      {
        title: 'Configure provider',
        description: 'Select your LLM provider and add an API key if needed.',
        content: (
          <div className="wizard-provider">
            <ProviderSelect />
            <ApiKeyInput />
          </div>
        ),
      },
      {
        title: 'Personal Integration (Optional)',
        description: 'Integrate your personal configurations and personas.',
        content: <PersonalIntegrationStep />,
      },
      {
        title: 'Write your first query',
        description: 'You are ready to ask your first question.',
        content: <QueryInput />,
      },
    ],
    []
  );

  const isLastStep = stepIndex === steps.length - 1;
  const isFirstStep = stepIndex === 0;

  const handleNext = async () => {
    // Validate current step before proceeding
    const errors = await validateStep(stepIndex);
    if (errors.length > 0) {
      setValidationErrors((prev) => ({ ...prev, [stepIndex]: errors }));
      return;
    }

    // Clear any previous validation errors for this step
    setValidationErrors((prev) => {
      const updated = { ...prev };
      delete updated[stepIndex];
      return updated;
    });

    if (!isLastStep) {
      setStepIndex((prev) => prev + 1);
    } else {
      // Save settings before completing
      try {
        await saveSettings();
        onComplete();
      } catch (error) {
        showNotification('Failed to save settings', 'error');
      }
    }
  };

  const handleBack = () => {
    if (!isFirstStep) {
      setStepIndex((prev) => prev - 1);
    }
  };

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true">
      <div className="onboarding-wizard">
        <div className="wizard-progress">
          {steps.map((_, index) => (
            <span
              key={`wizard-step-${index}`}
              className={`wizard-step-dot ${
                index === stepIndex ? 'active' : index < stepIndex ? 'complete' : ''
              }`}
            />
          ))}
        </div>
        <div className="wizard-content">
          <WizardStep title={steps[stepIndex].title} description={steps[stepIndex].description}>
            {steps[stepIndex].content}

            {/* Validation errors */}
            {validationErrors[stepIndex] && validationErrors[stepIndex].length > 0 && (
              <div className="wizard-validation-errors">
                {validationErrors[stepIndex].map((error, index) => (
                  <div key={index} className="wizard-error">
                    <span className="error-icon">⚠️</span>
                    <span className="error-message">{error}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Test configuration button for provider step */}
            {stepIndex === 3 && (
              <div className="wizard-test-config">
                <button
                  type="button"
                  className="btn btn-secondary wizard-test-btn"
                  onClick={testConfiguration}
                  disabled={isTestingConfig}
                >
                  {isTestingConfig ? 'Testing...' : 'Test Configuration'}
                </button>
                <p className="wizard-test-help">
                  Click to verify your API key and provider work correctly.
                </p>
              </div>
            )}

            {/* Helpful hints */}
            {stepIndex === 0 && (
              <div className="wizard-hint">
                💡 <strong>Tip:</strong> You can skip this wizard and configure settings later in
                Advanced Settings.
              </div>
            )}

            {stepIndex === 1 && (
              <div className="wizard-hint">
                💡 <strong>Tip:</strong> Domains pre-select personas for common use cases. You can
                customize members in the next step.
              </div>
            )}

            {stepIndex === 2 && (
              <div className="wizard-hint">
                💡 <strong>Tip:</strong> Start with 3-5 members for balanced responses. You can
                adjust this later.
              </div>
            )}

            {stepIndex === 3 && (
              <div className="wizard-hint">
                💡 <strong>Tip:</strong> API keys are stored locally and never sent to external
                servers except the AI provider.
              </div>
            )}

            {stepIndex === 4 && (
              <div className="wizard-hint">
                💡 <strong>Tip:</strong> Ask specific questions for better responses. The council
                works best with detailed queries.
              </div>
            )}
          </WizardStep>
        </div>
        <div className="wizard-actions">
          <button type="button" className="btn btn-secondary" onClick={onSkip}>
            Skip
          </button>
          <div className="wizard-nav">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleBack}
              disabled={isFirstStep}
            >
              Back
            </button>
            <button type="button" className="btn btn-primary" onClick={handleNext}>
              {isLastStep ? 'Finish' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingWizard;
