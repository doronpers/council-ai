/**
 * DomainSelect Component - Domain selection dropdown with recommendations
 */
import React, { useMemo } from 'react';
import { useApp } from '../../context/AppContext';
import { useConsultation } from '../../context/ConsultationContext';
import { recommendDomain, getRecommendationExplanation } from '../../utils/recommendations';

const DomainSelect: React.FC = () => {
  const { domains, settings, updateSettings, setSelectedMembers } = useApp();
  const { query } = useConsultation();

  // Get domain recommendation based on query
  const recommendedDomain = useMemo(() => {
    if (query.trim()) {
      return recommendDomain(query, domains);
    }
    return null;
  }, [query, domains]);

  const recommendationExplanation = useMemo(() => {
    if (recommendedDomain && query.trim()) {
      return getRecommendationExplanation(recommendedDomain, query);
    }
    return null;
  }, [recommendedDomain, query]);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newDomain = e.target.value;
    updateSettings({ domain: newDomain });

    // Clear custom members when domain changes
    setSelectedMembers([]);
  };

  const handleUseRecommended = () => {
    if (recommendedDomain) {
      updateSettings({ domain: recommendedDomain.id });
      setSelectedMembers([]);
    }
  };

  return (
    <div>
      <label htmlFor="domain">Domain</label>
      <select id="domain" value={settings.domain || ''} onChange={handleChange}>
        {domains.map((domain) => (
          <option key={domain.id} value={domain.id}>
            {domain.name}
            {domain.default_personas.length > 0
              ? ` (${domain.default_personas.length} members)`
              : ''}
          </option>
        ))}
      </select>
      {recommendedDomain &&
        recommendedDomain.id !== settings.domain &&
        recommendationExplanation && (
          <div className="domain-recommendation">
            <span className="domain-recommendation-badge">Recommended</span>
            <span className="domain-recommendation-text">{recommendationExplanation}</span>
            <button
              type="button"
              className="btn-minimal btn-small domain-recommendation-button"
              onClick={handleUseRecommended}
            >
              Use Recommended
            </button>
          </div>
        )}
      <p className="field-hint">Saved to browser</p>
    </div>
  );
};

export default DomainSelect;
