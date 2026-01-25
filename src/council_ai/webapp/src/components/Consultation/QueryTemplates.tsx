/**
 * QueryTemplates Component - Example queries by domain and use case
 */
import React, { useState } from 'react';
import { useConsultation } from '../../context/ConsultationContext';
import { useApp } from '../../context/AppContext';
import { queryTemplates } from '../../data/queryTemplates';
import './QueryTemplates.css';

const QueryTemplates: React.FC = () => {
  const { query, setQuery } = useConsultation();
  const { settings } = useApp();
  const [isExpanded, setIsExpanded] = useState(false);

  // Get templates for current domain or general templates
  const domainTemplates = queryTemplates[settings.domain || 'general'] || queryTemplates.general;
  const useCaseTemplates = queryTemplates.useCases || [];

  // Show templates if query is empty
  if (query.trim() && !isExpanded) {
    return null;
  }

  const handleTemplateSelect = (template: string) => {
    setQuery(template);
    setIsExpanded(false);
  };

  return (
    <div className="query-templates">
      <div className="query-templates-header">
        <button
          type="button"
          className="query-templates-toggle"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-expanded={isExpanded}
          aria-label="Show example queries"
        >
          {isExpanded ? '▼' : '▶'} Try these examples
        </button>
      </div>

      {isExpanded && (
        <div className="query-templates-content">
          {/* Domain-specific templates */}
          {domainTemplates && domainTemplates.length > 0 && (
            <div className="query-templates-section">
              <h4 className="query-templates-section-title">
                Examples for {settings.domain || 'general'} domain
              </h4>
              <div className="query-templates-list">
                {domainTemplates.map((template, index) => (
                  <button
                    key={index}
                    type="button"
                    className="query-template-item"
                    onClick={() => handleTemplateSelect(template.query)}
                  >
                    <div className="query-template-title">{template.title}</div>
                    <div className="query-template-preview">{template.query}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Use case templates */}
          {useCaseTemplates.length > 0 && (
            <div className="query-templates-section">
              <h4 className="query-templates-section-title">Common use cases</h4>
              <div className="query-templates-list">
                {useCaseTemplates.map((template, index) => (
                  <button
                    key={index}
                    type="button"
                    className="query-template-item"
                    onClick={() => handleTemplateSelect(template.query)}
                  >
                    <div className="query-template-title">{template.title}</div>
                    <div className="query-template-preview">{template.query}</div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default QueryTemplates;
