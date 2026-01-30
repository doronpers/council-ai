/**
 * MemberSelectionCard Component - Rich selection card for personas
 */
import React from 'react';
import type { Persona } from '../../types';
import { escapeHtml } from '../../utils/helpers';
import HelpIcon from '../Help/HelpIcon';
import { getHelpContent, formatHelpContent } from '../../data/helpContent';

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
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onToggle(persona.id);
    }
  };

  return (
    <div
      className={`member-selection-card-enhanced ${isSelected ? 'selected' : ''}`}
      onClick={() => onToggle(persona.id)}
      onKeyDown={handleKeyDown}
      role="button"
      aria-pressed={isSelected}
      aria-label={`${isSelected ? 'Deselect' : 'Select'} ${persona.name}, ${persona.title}`}
      tabIndex={0}
    >
      <div className="member-selection-card-header">
        <span className="member-emoji" aria-hidden="true">
          {escapeHtml(persona.emoji)}
        </span>
        <div className="member-selection-card-info">
          <div className="member-selection-card-name">{escapeHtml(persona.name)}</div>
          <div className="member-selection-card-title">{escapeHtml(persona.title)}</div>
        </div>

        <div className="member-selection-card-actions">
          <HelpIcon
            content={
              <div className="help-content">
                <div className="help-content-title">{persona.name}</div>
                <div className="help-content-description">{persona.razor}</div>
                <div className="help-content-description">
                  <strong>Core Question:</strong> {persona.core_question}
                </div>
                {persona.focus_areas && persona.focus_areas.length > 0 && (
                  <div className="help-content-examples">
                    <strong>Focus Areas:</strong>
                    <ul>
                      {persona.focus_areas.slice(0, 5).map((area, idx) => (
                        <li key={idx}>{area}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            }
            position="left"
          />
          <button
            type="button"
            className="member-info-button"
            onClick={(e) => {
              e.stopPropagation();
              onViewDetails(persona);
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.stopPropagation();
              }
            }}
            aria-label={`Learn more about ${persona.name}`}
          >
            ℹ️
          </button>
        </div>
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
