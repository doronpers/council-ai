/**
 * Council AI - Root Application Component
 */
import React from 'react';
import { AppProvider } from './context/AppContext';
import { ConsultationProvider } from './context/ConsultationContext';
import { NotificationProvider } from './components/Layout/NotificationContainer';
import ErrorBoundary from './components/Layout/ErrorBoundary';
import Header from './components/Layout/Header';
import ConfigPanel from './components/Configuration/ConfigPanel';
import MemberPreview from './components/Members/MemberPreview';
import QueryInput from './components/Consultation/QueryInput';
import SubmitButton from './components/Consultation/SubmitButton';
import ProgressDashboard from './components/Consultation/ProgressDashboard';
import ResultsPanel from './components/Results/ResultsPanel';
import HistoryPanel from './components/History/HistoryPanel';
import OnboardingWizard from './components/Onboarding/OnboardingWizard';
import { useOnboarding } from './hooks/useOnboarding';

const App: React.FC = () => {
  const { isComplete, completeOnboarding } = useOnboarding();

  return (
    <AppProvider>
      <NotificationProvider>
        <ConsultationProvider>
          <div className="app">
            <Header />
            {isComplete === false && (
              <OnboardingWizard onComplete={completeOnboarding} onSkip={completeOnboarding} />
            )}
            <main>
              {/* Configuration Section */}
              <ErrorBoundary>
                <section className="panel" id="config-section">
                  <h2>Configuration</h2>
                  <ConfigPanel />
                </section>
              </ErrorBoundary>

              {/* Member Preview Section */}
              <ErrorBoundary>
                <section className="panel" id="members-section">
                  <h2>Council Members</h2>
                  <MemberPreview />
                </section>
              </ErrorBoundary>

              {/* Query Section */}
              <ErrorBoundary>
                <section className="panel" id="query-section">
                  <h2>Your Query</h2>
                  <QueryInput />
                  <SubmitButton />
                </section>
              </ErrorBoundary>

              {/* Progress Dashboard (shown during consultation) */}
              <ErrorBoundary>
                <ProgressDashboard />
              </ErrorBoundary>

              {/* Results Section */}
              <ErrorBoundary>
                <ResultsPanel />
              </ErrorBoundary>

              {/* History Section */}
              <ErrorBoundary>
                <HistoryPanel />
              </ErrorBoundary>
            </main>
          </div>
        </ConsultationProvider>
      </NotificationProvider>
    </AppProvider>
  );
};

export default App;
