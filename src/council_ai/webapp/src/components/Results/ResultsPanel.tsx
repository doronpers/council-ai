/**
 * ResultsPanel Component - Container for consultation results
 */
import React, { useMemo, useState } from 'react';
import './ResultsPanel.css';
import { useConsultation } from '../../context/ConsultationContext';
import SynthesisCard from './SynthesisCard';
import ResponseCard from './ResponseCard';
import AnalysisCard from './AnalysisCard';
import UsageSummary from './UsageSummary';
import ExportMenu from './ExportMenu';

const ResultsPanel: React.FC = () => {
  const { result, streamingSynthesis, streamingResponses, streamingThinking, isConsulting } =
    useConsultation();
  const [searchTerm, setSearchTerm] = useState('');

  // During streaming, show streaming content
  const showStreamingSynthesis = isConsulting && streamingSynthesis;
  const showStreamingResponses = isConsulting && streamingResponses.size > 0;
  const showStreamingThinking = isConsulting && streamingThinking.size > 0;

  // After completion, show final results
  const showFinalResults = result && !isConsulting;

  const filteredResponses = useMemo(() => {
    if (!result || !result.responses) return [];
    const query = searchTerm.trim().toLowerCase();
    if (!query) return result.responses;
    return result.responses.filter((response) => {
      const haystack = [
        response.persona_name,
        response.persona_title,
        response.content,
        response.provider,
        response.model,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return haystack.includes(query);
    });
  }, [result, searchTerm]);

  // Show empty state if no results and not consulting
  if (!result && !isConsulting && streamingResponses.size === 0 && !streamingSynthesis) {
    return (
      <section className="panel" id="results-section">
        <h2>Results</h2>
        <div className="empty-state">
          <p className="empty-state-icon" aria-hidden="true">
            💬
          </p>
          <p className="empty-state-text">Your consultation results will appear here</p>
          <p className="empty-state-hint">Ask your council a question to get started</p>
        </div>
      </section>
    );
  }

  return (
    <section className="panel" id="results-section">
      <h2>Results</h2>

      {showFinalResults && result && (
        <div className="results-toolbar">
          <div className="results-search">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search responses..."
              className="results-search-input"
            />
          </div>
          <ExportMenu result={result} />
        </div>
      )}

      {/* Synthesis Section - Show prominently at top */}
      {(showStreamingSynthesis || (showFinalResults && result.synthesis)) && (
        <div id="synthesis" className="results-section-synthesis">
          {showStreamingSynthesis && <SynthesisCard content={streamingSynthesis} isStreaming />}
          {showFinalResults && result.synthesis && <SynthesisCard content={result.synthesis} />}
        </div>
      )}

      {/* Usage Summary Section */}
      {showFinalResults && result.usage_summary && (
        <div className="results-section-usage">
          <UsageSummary usageSummary={result.usage_summary} />
        </div>
      )}

      {/* Individual Responses Section */}
      {(showStreamingResponses || showStreamingThinking || showFinalResults) && (
        <div id="responses" className="responses results-section-responses">
          {showStreamingThinking &&
            Array.from(streamingThinking.entries()).map(([personaId, thinking]) => (
              <ResponseCard
                key={`thinking-${personaId}`}
                personaId={personaId}
                content={thinking}
                isStreaming
                isThinking
              />
            ))}
          {showStreamingResponses &&
            Array.from(streamingResponses.entries()).map(([personaId, content]) => (
              <ResponseCard key={personaId} personaId={personaId} content={content} isStreaming />
            ))}
          {showFinalResults &&
            filteredResponses.length > 0 &&
            filteredResponses.map((response) => (
              <ResponseCard
                key={response.persona_id}
                personaId={response.persona_id}
                personaName={response.persona_name}
                personaEmoji={response.persona_emoji}
                personaTitle={response.persona_title}
                content={response.content}
                error={response.error}
                provider={response.provider}
                model={response.model}
                usage={response.usage}
              />
            ))}
          {showFinalResults && filteredResponses.length === 0 && searchTerm && (
            <div className="results-no-matches">
              <p>No responses match your search term "{searchTerm}"</p>
            </div>
          )}
        </div>
      )}

      {/* Analysis Section */}
      {showFinalResults && result.analysis && (
        <div className="results-section-analysis">
          <AnalysisCard analysis={result.analysis} />
        </div>
      )}
    </section>
  );
};

export default ResultsPanel;
