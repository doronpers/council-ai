/**
 * ConsultationBar Component - Compact top bar for query, config, and member selection
 */
import React, { useState, useMemo, useRef, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { useConsultation } from '../../context/ConsultationContext';
import QueryInput from './QueryInput';
import SubmitButton from './SubmitButton';
import DomainSelect from '../Configuration/DomainSelect';
import ProviderSelect from '../Configuration/ProviderSelect';
import ApiKeyInput from '../Configuration/ApiKeyInput';
import ModeSelect from '../Configuration/ModeSelect';
import PersonaDetailModal from '../Members/PersonaDetailModal';
import { recommendPersonasForQuery, recommendPersonasForDomain } from '../../utils/recommendations';
import type { Persona } from '../../types';
import './ConsultationBar.css';

const categoryLabels: Record<Persona['category'], string> = {
  advisory: 'Advisory Council',
  adversarial: 'Red Team',
  creative: 'Creative',
  analytical: 'Analytical',
  strategic: 'Strategic',
  operational: 'Operational',
  specialist: 'Specialists',
  red_team: 'Red Team',
  custom: 'Custom',
};

const ConsultationBar: React.FC = () => {
  const { personas, selectedMembers, setSelectedMembers, domains, settings } = useApp();
  const { query } = useConsultation();
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [memberSearchQuery, setMemberSearchQuery] = useState('');
  const [activePersona, setActivePersona] = useState<Persona | null>(null);
  const memberDropdownRef = useRef<HTMLDivElement>(null);

  // Filter personas by search query
  const filteredPersonas = useMemo(() => {
    const query = memberSearchQuery ? memberSearchQuery.trim().toLowerCase() : '';
    if (!query) return personas;
    return personas.filter((persona) => {
      const haystack = [
        persona.name || '',
        persona.title || '',
        persona.razor || '',
        persona.core_question || '',
        ...(persona.focus_areas || []),
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return haystack.includes(query);
    });
  }, [personas, memberSearchQuery]);

  // Get recommended personas based on query or domain
  const recommendedPersonas = useMemo(() => {
    if (query.trim()) {
      return recommendPersonasForQuery(query, domains, personas);
    } else if (settings.domain) {
      const domain = domains.find((d) => d.id === settings.domain);
      if (domain) {
        return recommendPersonasForDomain(domain, personas);
      }
    }
    return [];
  }, [query, settings.domain, domains, personas]);

  // Group personas by category
  const groupedPersonas = useMemo(() => {
    return filteredPersonas.reduce<Record<Persona['category'], Persona[]>>(
      (acc, persona) => {
        if (!persona || persona.category == null || persona.category === undefined) {
          return acc;
        }
        if (!acc[persona.category]) {
          acc[persona.category] = [];
        }
        acc[persona.category].push(persona);
        return acc;
      },
      {
        advisory: [],
        adversarial: [],
        creative: [],
        analytical: [],
        strategic: [],
        operational: [],
        specialist: [],
        red_team: [],
        custom: [],
      }
    );
  }, [filteredPersonas]);

  const handleMemberToggle = (personaId: string) => {
    setSelectedMembers((prev) =>
      prev.includes(personaId) ? prev.filter((id) => id !== personaId) : [...prev, personaId]
    );
  };

  const handleSelectCategory = (category: Persona['category']) => {
    const categoryIds = groupedPersonas[category].map((persona) => persona.id);
    setSelectedMembers((prev) => Array.from(new Set([...prev, ...categoryIds])));
  };

  const handleClearMembers = () => {
    setSelectedMembers([]);
  };

  const handleUseRecommended = () => {
    if (recommendedPersonas.length > 0) {
      setSelectedMembers(recommendedPersonas.map((p) => p.id));
    }
  };

  const selectedPersonas = personas.filter((p) => selectedMembers.includes(p.id));

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        memberDropdownRef.current &&
        !memberDropdownRef.current.contains(event.target as Node) &&
        !(event.target as HTMLElement).closest('.member-select-input')
      ) {
        setShowAdvanced(false);
      }
    };

    if (showAdvanced) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showAdvanced]);

  return (
    <section className="consultation-bar" id="consultation-bar">
      <div className="consultation-bar-main">
        {/* Query Section - Left Side */}
        <div className="consultation-bar-query">
          <QueryInput compact showContext />
        </div>

        {/* Member Selection - Right Side */}
        <div className="consultation-bar-members">
          <div className="consultation-bar-members-header">
            <label htmlFor="member-select">Council Members</label>
            {selectedMembers.length > 0 && (
              <button
                type="button"
                className="btn-minimal btn-small"
                onClick={handleClearMembers}
                title="Clear selection"
              >
                Clear
              </button>
            )}
          </div>

          {/* Selected Members Display */}
          {selectedPersonas.length > 0 && (
            <div className="selected-members-pills">
              {selectedPersonas.map((persona) => (
                <span key={persona.id} className="member-pill">
                  <span className="member-pill-emoji">{persona.emoji}</span>
                  <span className="member-pill-name">{persona.name}</span>
                  <button
                    type="button"
                    className="member-pill-remove"
                    onClick={() => handleMemberToggle(persona.id)}
                    aria-label={`Remove ${persona.name}`}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}

          {/* Member Selection Dropdown */}
          <div className="member-select-wrapper" ref={memberDropdownRef}>
            <input
              type="text"
              id="member-select"
              className="member-select-input"
              placeholder="Search and select members..."
              value={memberSearchQuery}
              onChange={(e) => setMemberSearchQuery(e.target.value)}
              onFocus={() => setShowAdvanced(true)}
            />
            {showAdvanced && (
              <div className="member-select-dropdown">
                {recommendedPersonas.length > 0 && (
                  <div className="member-select-recommended-banner">
                    <strong>Recommended:</strong>{' '}
                    {recommendedPersonas.map((p) => `${p.emoji} ${p.name}`).join(', ')}
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={handleUseRecommended}
                      style={{ marginLeft: '8px' }}
                    >
                      Use all
                    </button>
                  </div>
                )}

                <div className="member-select-search">
                  <input
                    type="text"
                    placeholder="Search members..."
                    value={memberSearchQuery}
                    onChange={(e) => setMemberSearchQuery(e.target.value)}
                    className="member-select-search-input"
                    autoFocus
                  />
                </div>

                <div className="member-select-categories">
                  {Object.entries(categoryLabels).map(([category, label]) => {
                    const personasInCategory = groupedPersonas[category as Persona['category']];
                    if (personasInCategory.length === 0) return null;

                    const allSelected = personasInCategory.every((p) =>
                      selectedMembers.includes(p.id)
                    );

                    return (
                      <div key={category} className="member-select-category">
                        <div className="member-select-category-header">
                          <span className="member-select-category-title">{label}</span>
                          <button
                            type="button"
                            className="btn-minimal btn-small"
                            onClick={() => handleSelectCategory(category as Persona['category'])}
                          >
                            {allSelected ? 'Deselect All' : 'Select All'}
                          </button>
                        </div>
                        <div className="member-select-category-list">
                          {personasInCategory.map((persona) => {
                            const isSelected = selectedMembers.includes(persona.id);
                            const isRecommended = recommendedPersonas.some(
                              (p) => p.id === persona.id
                            );
                            return (
                              <div
                                key={persona.id}
                                className={`member-select-option-wrapper ${isRecommended ? 'recommended' : ''}`}
                              >
                                <label
                                  className={`member-select-option ${isSelected ? 'selected' : ''}`}
                                >
                                  <input
                                    type="checkbox"
                                    checked={isSelected}
                                    onChange={() => handleMemberToggle(persona.id)}
                                  />
                                  <span className="member-select-option-emoji">
                                    {persona.emoji}
                                  </span>
                                  <div className="member-select-option-info">
                                    <span className="member-select-option-name">
                                      {persona.name}
                                    </span>
                                    {persona.title && (
                                      <span className="member-select-option-title">
                                        {persona.title}
                                      </span>
                                    )}
                                  </div>
                                </label>
                                <button
                                  type="button"
                                  className="member-select-option-details-btn"
                                  onClick={() => setActivePersona(persona)}
                                  title={`View ${persona.name} details`}
                                  aria-label={`View details for ${persona.name}`}
                                >
                                  ℹ️
                                </button>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="member-select-footer">
                  <button
                    type="button"
                    className="btn-minimal"
                    onClick={() => setShowAdvanced(false)}
                  >
                    Close
                  </button>
                  <span className="member-select-count">{selectedMembers.length} selected</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Submit Button - Right Side */}
        <div className="consultation-bar-submit">
          <SubmitButton />
        </div>
      </div>

      {/* Quick Config Row */}
      <div className="consultation-bar-quick-config">
        <div className="consultation-bar-quick-config-item">
          <DomainSelect />
        </div>
        <div className="consultation-bar-quick-config-item">
          <ProviderSelect />
        </div>
        <div className="consultation-bar-quick-config-item">
          <ModeSelect />
        </div>
        <div className="consultation-bar-quick-config-item">
          <ApiKeyInput />
        </div>
      </div>

      {/* Persona Detail Modal */}
      <PersonaDetailModal persona={activePersona} onClose={() => setActivePersona(null)} />
    </section>
  );
};

export default ConsultationBar;
