/**
 * MemberSelectionCard Component - Rich selection card for personas
 */
import React from 'react';
import type { Persona } from '../../types';
import { escapeHtml } from '../../utils/helpers';

interface MemberSelectionCardProps {
  persona: Persona;
  isSelected: boolean;
  onToggle: (personaId: string) => void;
  onViewDetails: (persona: Persona) => void;
}

const MemberSelectionCard: React.FC<MemberSelectionCardProps> = ({
  persona,
  isSelected,
  onToggle,
  onViewDetails,
}) => {
  return (
    <div className={`member-selection-card-enhanced ${isSelected ? 'selected' : ''}`}>
      <button
        type="button"
        className="member-selection-card-toggle"
        onClick={() => onToggle(persona.id)}
        aria-pressed={isSelected}
      >
        <div className="member-selection-card-header">
          <span className="member-emoji">{escapeHtml(persona.emoji)}</span>
          <div className="member-selection-card-info">
            <div className="member-selection-card-name">{escapeHtml(persona.name)}</div>
            <div className="member-selection-card-title">{escapeHtml(persona.title)}</div>
          </div>
          <span className={`member-selection-card-badge ${persona.category}`}>
            {escapeHtml(persona.category)}
          </span>
        </div>
        <div className="member-selection-card-razor">{escapeHtml(persona.razor)}</div>
        <div className="member-selection-card-focus">
          {persona.focus_areas.slice(0, 3).map((area, index) => (
            <span key={`${persona.id}-focus-${index}`} className="focus-tag">
              {escapeHtml(area)}
            </span>
          ))}
        </div>
      </button>
      <button
        type="button"
        className="member-selection-card-details"
        onClick={() => onViewDetails(persona)}
      >
        Learn more
      </button>
    </div>
  );
};

export default MemberSelectionCard;
