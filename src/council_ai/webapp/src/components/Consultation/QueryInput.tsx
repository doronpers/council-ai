/**
 * QueryInput Component - Main query and context textareas
 */
import React, { useState } from 'react';
import { useConsultation } from '../../context/ConsultationContext';

const MAX_QUERY_LENGTH = 50000;
const MAX_CONTEXT_LENGTH = 50000;

interface QueryInputProps {
  showContext?: boolean;
  compact?: boolean;
}

const QueryInput: React.FC<QueryInputProps> = ({ showContext = true, compact = false }) => {
  const { query, setQuery, context, setContext, isConsulting } = useConsultation();
  const [showContextField, setShowContextField] = useState(false);

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
          rows={compact ? 3 : 4}
          aria-describedby="query-counter"
        />
      </div>

      {showContext && (
        <>
          {compact && !showContextField && (
            <button
              type="button"
              className="btn-minimal btn-small"
              onClick={() => setShowContextField(true)}
              style={{ marginBottom: '8px' }}
            >
              + Add Context (Optional)
            </button>
          )}
          {(showContextField || !compact) && (
            <div>
              <div
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
              >
                <label htmlFor="context">Context (Optional)</label>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span
                    className={`character-counter ${contextNearLimit ? 'character-counter--warning' : ''}`}
                    aria-live="polite"
                  >
                    {contextLength.toLocaleString()} / {MAX_CONTEXT_LENGTH.toLocaleString()}
                  </span>
                  {compact && (
                    <button
                      type="button"
                      className="btn-minimal btn-small"
                      onClick={() => {
                        setShowContextField(false);
                        if (!context) setContext('');
                      }}
                      title="Hide context field"
                    >
                      ×
                    </button>
                  )}
                </div>
              </div>
              <textarea
                id="context"
                placeholder="Provide additional context, background, or constraints..."
                value={context}
                onChange={(e) => setContext(e.target.value)}
                disabled={isConsulting}
                maxLength={MAX_CONTEXT_LENGTH}
                rows={compact ? 2 : 3}
                aria-describedby="context-counter"
              />
            </div>
          )}
        </>
      )}
    </>
  );
};

export default QueryInput;
