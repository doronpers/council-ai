/**
 * Council AI - Root Application Component
 */
import React from 'react';
import { AppProvider } from './context/AppContext';
import { ConsultationProvider } from './context/ConsultationContext';
import Header from './components/Layout/Header';
import ConfigPanel from './components/Configuration/ConfigPanel';
import MemberPreview from './components/Members/MemberPreview';
import QueryInput from './components/Consultation/QueryInput';
import SubmitButton from './components/Consultation/SubmitButton';
import ProgressDashboard from './components/Consultation/ProgressDashboard';
import ResultsPanel from './components/Results/ResultsPanel';
import HistoryPanel from './components/History/HistoryPanel';

const App: React.FC = () => {
    return (
        <AppProvider>
            <ConsultationProvider>
                <div className="app">
                    <Header />
                    <main>
                        {/* Configuration Section */}
                        <section className="panel" id="config-section">
                            <h2>Configuration</h2>
                            <ConfigPanel />
                        </section>

                        {/* Member Preview Section */}
                        <section className="panel" id="members-section">
                            <h2>Council Members</h2>
                            <MemberPreview />
                        </section>

                        {/* Query Section */}
                        <section className="panel" id="query-section">
                            <h2>Your Query</h2>
                            <QueryInput />
                            <SubmitButton />
                        </section>

                        {/* Progress Dashboard (shown during consultation) */}
                        <ProgressDashboard />

                        {/* Results Section */}
                        <ResultsPanel />

                        {/* History Section */}
                        <HistoryPanel />
                    </main>
                </div>
            </ConsultationProvider>
        </AppProvider>
    );
};

export default App;
