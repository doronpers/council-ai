/**
 * MemberSelectionGrid Component - Enhanced selection grid for council members
 */
import React, { useMemo, useState } from 'react';
import { useApp } from '../../context/AppContext';
import type { Persona } from '../../types';
import MemberSelectionCard from './MemberSelectionCard';
import PersonaDetailModal from './PersonaDetailModal';

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

const MemberSelectionGrid: React.FC = () => {
  const { personas, selectedMembers, setSelectedMembers } = useApp();
  const [searchQuery, setSearchQuery] = useState('');
  const [activePersona, setActivePersona] = useState<Persona | null>(null);

  const filteredPersonas = useMemo(() => {
    const query = searchQuery ? searchQuery.trim().toLowerCase() : '';

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
  }, [personas, searchQuery]);

  const groupedPersonas = useMemo(() => {
    return filteredPersonas.reduce<Record<Persona['category'], Persona[]>>(
      (acc, persona) => {
        // Initialize category array if it doesn't exist

        // Handle undefined/null category
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

  const handleToggle = (personaId: string) => {
    setSelectedMembers((prev) =>
      prev.includes(personaId) ? prev.filter((id) => id !== personaId) : [...prev, personaId]
    );
  };

  const handleSelectCategory = (category: Persona['category']) => {
    const categoryIds = groupedPersonas[category].map((persona) => persona.id);
    setSelectedMembers((prev) => Array.from(new Set([...prev, ...categoryIds])));
  };

  const handleClearSelection = () => {
    setSelectedMembers([]);
  };

  return (
    <div id="members-container" className="members-selection">
      <div className="members-selection-header">
        <div className="members-selection-title">Select members</div>
        <div className="members-selection-actions">
          <button type="button" className="btn btn-secondary" onClick={handleClearSelection}>
            Clear selection
          </button>
        </div>
      </div>

      <div className="members-selection-search">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search members by name, focus area, or trait..."
          className="members-selection-search-input"
        />
      </div>

      {Object.entries(categoryLabels).map(([category, label]) => {
        const personasInCategory = groupedPersonas[category as Persona['category']];
        if (personasInCategory.length === 0) return null;

        return (
          <div key={category} className="members-selection-category">
            <div className="members-selection-category-header">
              <div className="members-selection-category-title">{label}</div>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => handleSelectCategory(category as Persona['category'])}
              >
                Select all
              </button>
            </div>
            <div className="members-selection-grid">
              {personasInCategory.map((persona) => (
                <MemberSelectionCard
                  key={persona.id}
                  persona={persona}
                  isSelected={selectedMembers.includes(persona.id)}
                  onToggle={handleToggle}
                  onViewDetails={setActivePersona}
                />
              ))}
            </div>
          </div>
        );
      })}

      <PersonaDetailModal persona={activePersona} onClose={() => setActivePersona(null)} />
    </div>
  );
};

export default MemberSelectionGrid;
