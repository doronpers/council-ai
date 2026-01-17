/**
 * QueryInput Component - Main query and context textareas
 */
import React from 'react';
import { useConsultation } from '../../context/ConsultationContext';

const QueryInput: React.FC = () => {
  const { query, setQuery, context, setContext, isConsulting } = useConsultation();

  return (
    <>
      <div>
        <label htmlFor="query">Query</label>
        <textarea
          id="query"
          placeholder="What would you like the council to discuss?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={isConsulting}
          rows={4}
        />
      </div>

      <div>
        <label htmlFor="context">Context (Optional)</label>
        <textarea
          id="context"
          placeholder="Provide additional context, background, or constraints..."
          value={context}
          onChange={(e) => setContext(e.target.value)}
          disabled={isConsulting}
          rows={3}
        />
      </div>
    </>
  );
};

export default QueryInput;
