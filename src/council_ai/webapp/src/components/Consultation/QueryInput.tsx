/**
 * QueryInput Component - Main query and context textareas with validation
 */
import React, { useState, useEffect } from 'react';
import { useConsultation } from '../../context/ConsultationContext';
import { getValidationError } from '../../utils/errorMessages';
import { ValidationRules } from '../../utils/validation';
import QueryTemplates from './QueryTemplates';

const MAX_QUERY_LENGTH = 50000;
const MAX_CONTEXT_LENGTH = 50000;

interface QueryInputProps {
  showContext?: boolean;
  compact?: boolean;
}

const QueryInput: React.FC<QueryInputProps> = ({ showContext = true, compact = false }) => {
  const { query, setQuery, context, setContext, isConsulting } = useConsultation();
  const [showContextField, setShowContextField] = useState(false);
  const [queryError, setQueryError] = useState<string | null>(null);
  const [queryTouched, setQueryTouched] = useState(false);

  const queryLength = query.length;
  const contextLength = context.length;
  const queryNearLimit = queryLength > MAX_QUERY_LENGTH * 0.9;
  const contextNearLimit = contextLength > MAX_CONTEXT_LENGTH * 0.9;

  // Validate query on change if touched
  useEffect(() => {
    if (queryTouched) {
      const validationError = getValidationError('query', query);
      if (validationError) {
        setQueryError(validationError);
      } else {
        // Additional length validation
        const lengthError = ValidationRules.query.maxLength(MAX_QUERY_LENGTH).validate(query)
          ? null
          : ValidationRules.query.maxLength(MAX_QUERY_LENGTH).message;
        setQueryError(lengthError);
      }
    }
  }, [query, queryTouched]);

  const handleQueryChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setQuery(newValue);
    if (queryTouched) {
      const validationError = getValidationError('query', newValue);
      if (validationError) {
        setQueryError(validationError);
      } else {
        const lengthError = ValidationRules.query.maxLength(MAX_QUERY_LENGTH).validate(newValue)
          ? null
          : ValidationRules.query.maxLength(MAX_QUERY_LENGTH).message;
        setQueryError(lengthError);
      }
    }
  };

  const handleQueryBlur = () => {
    setQueryTouched(true);
    const validationError = getValidationError('query', query);
    if (validationError) {
      setQueryError(validationError);
    } else {
      const lengthError = ValidationRules.query.maxLength(MAX_QUERY_LENGTH).validate(query)
        ? null
        : ValidationRules.query.maxLength(MAX_QUERY_LENGTH).message;
      setQueryError(lengthError);
    }
  };

  return (
    <>
      <QueryTemplates />
      <div>
        <div className="flex-between">
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
          onChange={handleQueryChange}
          onBlur={handleQueryBlur}
          disabled={isConsulting}
          maxLength={MAX_QUERY_LENGTH}
          rows={compact ? 3 : 4}
          aria-invalid={queryError ? 'true' : 'false'}
          aria-describedby={queryError ? 'query-error query-counter' : 'query-counter'}
          className={queryError ? 'input-error' : ''}
        />
        {queryError && (
          <p id="query-error" className="field-error" role="alert">
            {queryError}
          </p>
        )}
      </div>

      {showContext && (
        <>
          {compact && !showContextField && (
            <button
              type="button"
              className="btn-minimal btn-small mb-8"
              onClick={() => setShowContextField(true)}
            >
              + Add Context (Optional)
            </button>
          )}
          {(showContextField || !compact) && (
            <div>
              <div className="flex-between">
                <label htmlFor="context">Context (Optional)</label>
                <div className="flex-row gap-8">
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
