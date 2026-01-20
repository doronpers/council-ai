/**
 * QueryInput Component - Main query and context textareas
 */
import React from 'react';
import { useConsultation } from '../../context/ConsultationContext';

const MAX_QUERY_LENGTH = 50000;
const MAX_CONTEXT_LENGTH = 50000;

const QueryInput: React.FC = () => {
  const { query, setQuery, context, setContext, isConsulting } = useConsultation();

  const queryLength = query.length;
  const contextLength = context.length;
  const queryNearLimit = queryLength > MAX_QUERY_LENGTH * 0.9;
  const contextNearLimit = contextLength > MAX_CONTEXT_LENGTH * 0.9;

  return (
    <>
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <label htmlFor="query">Query</label>
          <span
            className={`character-counter ${queryNearLimit ? 'character-counter--warning' : ''}`}
            aria-live="polite"
          >
            {queryLength.toLocaleString()} / {MAX_QUERY_LENGTH.toLocaleString()}
          </span>
        </div>
        <textarea
          id="query"
          placeholder="What would you like the council to discuss?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={isConsulting}
          maxLength={MAX_QUERY_LENGTH}
          rows={4}
          aria-describedby="query-counter"
        />
      </div>

      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <label htmlFor="context">Context (Optional)</label>
          <span
            className={`character-counter ${contextNearLimit ? 'character-counter--warning' : ''}`}
            aria-live="polite"
          >
            {contextLength.toLocaleString()} / {MAX_CONTEXT_LENGTH.toLocaleString()}
          </span>
        </div>
        <textarea
          id="context"
          placeholder="Provide additional context, background, or constraints..."
          value={context}
          onChange={(e) => setContext(e.target.value)}
          disabled={isConsulting}
          maxLength={MAX_CONTEXT_LENGTH}
          rows={3}
          aria-describedby="context-counter"
        />
      </div>
    </>
  );
};

export default QueryInput;
