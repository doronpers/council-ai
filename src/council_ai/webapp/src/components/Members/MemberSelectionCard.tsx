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
    <div
      className={`member-selection-card-enhanced ${isSelected ? 'selected' : ''}`}
      onClick={() => onToggle(persona.id)}
      role="button"
      aria-pressed={isSelected}
      tabIndex={0}
    >
      <div className="member-selection-card-header">
        <span className="member-emoji">{escapeHtml(persona.emoji)}</span>
        <div className="member-selection-card-info">
          <div className="member-selection-card-name">{escapeHtml(persona.name)}</div>
          <div className="member-selection-card-title">{escapeHtml(persona.title)}</div>
        </div>

        <button
          type="button"
          className="member-info-button"
          onClick={(e) => {
            e.stopPropagation();
            onViewDetails(persona);
          }}
          aria-label="Learn more"
        >
          ℹ️
        </button>
      </div>

      <div className="member-selection-card-content">
        <div className="member-selection-card-razor">{escapeHtml(persona.razor)}</div>
        <div className="member-selection-card-focus">
          {persona.focus_areas.slice(0, 3).map((area, index) => (
            <span key={`${persona.id}-focus-${index}`} className="focus-tag">
              {escapeHtml(area)}
            </span>
          ))}
        </div>
        <span className={`member-selection-card-badge ${persona.category}`}>
          {escapeHtml(persona.category)}
        </span>
      </div>
    </div>
  );
};

export default MemberSelectionCard;
