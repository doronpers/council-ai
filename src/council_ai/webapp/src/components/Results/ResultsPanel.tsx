/**
 * ResultsPanel Component - Container for consultation results
 */
import React, { useMemo, useState } from 'react';
import { useConsultation } from '../../context/ConsultationContext';
import SynthesisCard from './SynthesisCard';
import ResponseCard from './ResponseCard';
import AnalysisCard from './AnalysisCard';
import UsageSummary from './UsageSummary';
import ExportMenu from './ExportMenu';

const ResultsPanel: React.FC = () => {
  const { result, streamingSynthesis, streamingResponses, isConsulting } = useConsultation();
  const [searchTerm, setSearchTerm] = useState('');

  // Show nothing if no results and not consulting
  if (!result && !isConsulting && streamingResponses.size === 0) {
    return null;
  }

  // During streaming, show streaming content
  const showStreamingSynthesis = isConsulting && streamingSynthesis;
  const showStreamingResponses = isConsulting && streamingResponses.size > 0;

  // After completion, show final results
  const showFinalResults = result && !isConsulting;

  const filteredResponses = useMemo(() => {
    if (!result) return [];
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

      {/* Synthesis Section */}
      <div id="synthesis">
        {showStreamingSynthesis && <SynthesisCard content={streamingSynthesis} isStreaming />}
        {showFinalResults && result.synthesis && <SynthesisCard content={result.synthesis} />}
      </div>

      {/* Usage Summary Section */}
      {showFinalResults && result.usage_summary && (
        <UsageSummary usageSummary={result.usage_summary} />
      )}

      {/* Individual Responses Section */}
      <div id="responses" className="responses">
        {showStreamingResponses &&
          Array.from(streamingResponses.entries()).map(([personaId, content]) => (
            <ResponseCard key={personaId} personaId={personaId} content={content} isStreaming />
          ))}
        {showFinalResults &&
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
      </div>

      {/* Analysis Section */}
      {showFinalResults && result.analysis && <AnalysisCard analysis={result.analysis} />}
    </section>
  );
};

export default ResultsPanel;
