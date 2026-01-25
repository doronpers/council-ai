/**
 * OnboardingWizard Component - Multi-step onboarding flow
 */
import React, { useState, useEffect } from 'react';
import { useOnboarding } from './OnboardingContext';
import { useApp } from '../../context/AppContext';
import { useConsultation } from '../../context/ConsultationContext';
import Modal from '../Layout/Modal';
import OnboardingStep from './OnboardingStep';
import ProviderSelect from '../Configuration/ProviderSelect';
import DomainSelect from '../Configuration/DomainSelect';
import ApiKeyInput from '../Configuration/ApiKeyInput';
import BaseUrlInput from '../Configuration/BaseUrlInput';
import QueryInput from '../Consultation/QueryInput';
import './OnboardingWizard.css';

const OnboardingWizard: React.FC = () => {
  const {
    isOnboarding,
    currentStep,
    totalSteps,
    nextStep,
    previousStep,
    skipOnboarding,
    completeOnboarding,
    markStepComplete,
  } = useOnboarding();
  const { settings, updateSettings, personas, domains } = useApp();
  const { query, setQuery } = useConsultation();
  const [exampleQuery, setExampleQuery] = useState('');

  // Example queries by domain
  const exampleQueries: Record<string, string> = {
    coding: 'Review this API design: POST /users creates a new user. What issues do you see?',
    business: "We're a B2B SaaS with $2M ARR. A competitor raised $50M. Should we raise funding?",
    startup: 'We have 18 months runway. Should we focus on growth or profitability?',
    product: 'Our users say the app is too complex. How should we simplify?',
    general: 'I need advice on an important decision. What should I consider?',
  };

  // Set example query based on selected domain
  useEffect(() => {
    if (currentStep === 5 && settings.domain) {
      const domainExample = exampleQueries[settings.domain] || exampleQueries.general;
      setExampleQuery(domainExample);
      if (!query) {
        setQuery(domainExample);
      }
    }
  }, [currentStep, settings.domain, query, setQuery]);

  if (!isOnboarding) {
    return null;
  }

  const progressPercent = ((currentStep + 1) / totalSteps) * 100;

  const handleNext = () => {
    markStepComplete(currentStep);
    nextStep();
  };

  const handlePrevious = () => {
    previousStep();
  };

  const handleSkip = () => {
    skipOnboarding();
  };

  const handleComplete = () => {
    markStepComplete(currentStep);
    completeOnboarding();
  };

  // Step 1: Welcome
  const renderWelcomeStep = () => (
    <OnboardingStep
      title="Welcome to Council AI"
      description="Get advice from a council of AI-powered personas with diverse perspectives and expertise."
      onNext={handleNext}
      onSkip={handleSkip}
      showPrevious={false}
      nextLabel="Get Started"
    >
      <div className="onboarding-welcome-content">
        <div className="onboarding-welcome-icon">🏛️</div>
        <div className="onboarding-features">
          <div className="onboarding-feature">
            <strong>14 Built-in Personas</strong> - Advisory Council, Red Team, and Specialists
          </div>
          <div className="onboarding-feature">
            <strong>15 Domain Presets</strong> - Coding, business, startup, creative, and more
          </div>
          <div className="onboarding-feature">
            <strong>Multiple Modes</strong> - Individual, synthesis, debate, vote, or sequential
          </div>
          <div className="onboarding-feature">
            <strong>Free Option</strong> - Use LM Studio for local, cost-free consultations
          </div>
        </div>
      </div>
    </OnboardingStep>
  );

  // Step 2: Provider Selection
  const renderProviderStep = () => (
    <OnboardingStep
      title="Choose Your LLM Provider"
      description="Select how you want to run consultations. LM Studio is free and local, while cloud providers require API keys."
      onNext={handleNext}
      onPrevious={handlePrevious}
      onSkip={handleSkip}
    >
      <div className="onboarding-provider-options">
        <div className="onboarding-provider-option">
          <h4>🆓 LM Studio (Recommended for beginners)</h4>
          <p>Free, local, private. No API key needed. Download from lmstudio.ai</p>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              updateSettings({ provider: 'openai' });
              updateSettings({ base_url: 'http://localhost:1234/v1' });
              handleNext();
            }}
          >
            Use LM Studio
          </button>
        </div>
        <div className="onboarding-provider-option">
          <h4>☁️ Cloud Providers</h4>
          <p>Anthropic, OpenAI, or Google Gemini. Requires API key.</p>
          <ProviderSelect />
        </div>
      </div>
    </OnboardingStep>
  );

  // Step 3: Configuration
  const renderConfigStep = () => (
    <OnboardingStep
      title="Configure Your Setup"
      description="Set up your API key or base URL. For LM Studio, just set the base URL."
      onNext={handleNext}
      onPrevious={handlePrevious}
      onSkip={handleSkip}
    >
      <div className="onboarding-config-fields">
        {settings.provider === 'openai' && settings.base_url?.includes('localhost') ? (
          <BaseUrlInput />
        ) : (
          <ApiKeyInput />
        )}
        {settings.provider === 'openai' && !settings.base_url?.includes('localhost') && (
          <BaseUrlInput />
        )}
      </div>
    </OnboardingStep>
  );

  // Step 4: Domain Selection
  const renderDomainStep = () => (
    <OnboardingStep
      title="Choose Your Domain"
      description="Select a domain that matches your use case. This will pre-select recommended personas."
      onNext={handleNext}
      onPrevious={handlePrevious}
      onSkip={handleSkip}
    >
      <DomainSelect />
      {settings.domain && (
        <div className="onboarding-domain-info">
          <p className="onboarding-domain-description">
            {domains.find((d) => d.id === settings.domain)?.description || ''}
          </p>
        </div>
      )}
    </OnboardingStep>
  );

  // Step 5: Persona Introduction
  const renderPersonaStep = () => {
    const domain = domains.find((d) => d.id === settings.domain);
    const domainPersonas = domain?.default_personas || [];
    const selectedPersonas = domainPersonas
      .slice(0, 3)
      .map((id) => personas.find((p) => p.id === id))
      .filter((p): p is NonNullable<typeof p> => p !== undefined);

    return (
      <OnboardingStep
        title="Meet Your Council"
        description="These personas will provide diverse perspectives on your questions."
        onNext={handleNext}
        onPrevious={handlePrevious}
        onSkip={handleSkip}
      >
        <div className="onboarding-personas">
          {selectedPersonas.length > 0 ? (
            selectedPersonas.map((persona) => (
              <div key={persona.id} className="onboarding-persona-card">
                <div className="onboarding-persona-emoji">{persona.emoji}</div>
                <div className="onboarding-persona-info">
                  <h4>{persona.name}</h4>
                  <p className="onboarding-persona-title">{persona.title}</p>
                  <p className="onboarding-persona-question">{persona.core_question}</p>
                </div>
              </div>
            ))
          ) : (
            <p className="onboarding-persona-note">No personas available for this domain.</p>
          )}
          <p className="onboarding-persona-note">
            You can customize personas and add more in Advanced Settings.
          </p>
        </div>
      </OnboardingStep>
    );
  };

  // Step 6: First Consultation
  const renderFirstConsultationStep = () => (
    <OnboardingStep
      title="Your First Consultation"
      description="Try asking your council a question. We've pre-filled an example, but you can change it."
      onNext={handleComplete}
      onPrevious={handlePrevious}
      onSkip={handleSkip}
      nextLabel="Start Consultation"
      showNext={!!query.trim()}
    >
      <QueryInput showContext={false} compact={false} />
      <div className="onboarding-consultation-hint">
        <p>
          <strong>Tip:</strong> After submitting, you'll see individual responses from each persona
          and a synthesized summary.
        </p>
      </div>
    </OnboardingStep>
  );

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return renderWelcomeStep();
      case 1:
        return renderProviderStep();
      case 2:
        return renderConfigStep();
      case 3:
        return renderDomainStep();
      case 4:
        return renderPersonaStep();
      case 5:
        return renderFirstConsultationStep();
      default:
        return null;
    }
  };

  return (
    <Modal
      isOpen={isOnboarding}
      onClose={skipOnboarding}
      title=""
      className="onboarding-modal"
      showCloseButton={false}
    >
      <div className="onboarding-wizard">
        {/* Progress bar */}
        <div className="onboarding-progress">
          <div className="onboarding-progress-bar" style={{ width: `${progressPercent}%` }} />
          <div className="onboarding-progress-text">
            Step {currentStep + 1} of {totalSteps}
          </div>
        </div>

        {/* Step content */}
        <div className="onboarding-wizard-content">{renderStep()}</div>
      </div>
    </Modal>
  );
};

export default OnboardingWizard;
