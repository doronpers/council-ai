/**
 * ResultsPanel Component - Container for consultation results
 */
import React from 'react';
import { useConsultation } from '../../context/ConsultationContext';
import SynthesisCard from './SynthesisCard';
import ResponseCard from './ResponseCard';
import AnalysisCard from './AnalysisCard';

const ResultsPanel: React.FC = () => {
    const { result, streamingSynthesis, streamingResponses, isConsulting } = useConsultation();

    // Show nothing if no results and not consulting
    if (!result && !isConsulting && streamingResponses.size === 0) {
        return null;
    }

    // During streaming, show streaming content
    const showStreamingSynthesis = isConsulting && streamingSynthesis;
    const showStreamingResponses = isConsulting && streamingResponses.size > 0;

    // After completion, show final results
    const showFinalResults = result && !isConsulting;

    return (
        <section className="panel" id="results-section">
            <h2>Results</h2>

            {/* Synthesis Section */}
            <div id="synthesis">
                {showStreamingSynthesis && (
                    <SynthesisCard content={streamingSynthesis} isStreaming />
                )}
                {showFinalResults && result.synthesis && (
                    <SynthesisCard content={result.synthesis} />
                )}
            </div>

            {/* Individual Responses Section */}
            <div id="responses" className="responses">
                {showStreamingResponses &&
                    Array.from(streamingResponses.entries()).map(([personaId, content]) => (
                        <ResponseCard
                            key={personaId}
                            personaId={personaId}
                            content={content}
                            isStreaming
                        />
                    ))}
                {showFinalResults &&
                    result.responses.map((response) => (
                        <ResponseCard
                            key={response.persona_id}
                            personaId={response.persona_id}
                            personaName={response.persona_name}
                            personaEmoji={response.persona_emoji}
                            personaTitle={response.persona_title}
                            content={response.content}
                            error={response.error}
                        />
                    ))}
            </div>

            {/* Analysis Section */}
            {showFinalResults && result.analysis && (
                <AnalysisCard analysis={result.analysis} />
            )}
        </section>
    );
};

export default ResultsPanel;
