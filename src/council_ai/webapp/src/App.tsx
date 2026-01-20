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
import ConsultationBar from './components/Consultation/ConsultationBar';
import ProgressDashboard from './components/Consultation/ProgressDashboard';
import ResultsPanel from './components/Results/ResultsPanel';
import HistoryPanel from './components/History/HistoryPanel';

const App: React.FC = () => {
  return (
    <AppProvider>
      <NotificationProvider>
        <ConsultationProvider>
          <div className="app">
            <Header />
            <main>
              {/* Consultation Bar - Top of page with query, config, and member selection */}
              <ErrorBoundary>
                <ConsultationBar />
              </ErrorBoundary>

              {/* Progress Dashboard (shown during consultation) */}
              <ErrorBoundary>
                <ProgressDashboard />
              </ErrorBoundary>

              {/* Results Section */}
              <ErrorBoundary>
                <ResultsPanel />
              </ErrorBoundary>

              {/* Configuration Section - Collapsible for advanced settings */}
              <ErrorBoundary>
                <details className="panel" id="config-section">
                  <summary>
                    <h2>⚙️ Advanced Configuration</h2>
                  </summary>
                  <ConfigPanel />
                </details>
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
