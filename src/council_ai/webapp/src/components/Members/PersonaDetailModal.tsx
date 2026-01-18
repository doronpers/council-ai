/**
 * PersonaDetailModal Component - Detailed persona information
 */
import React from 'react';
import type { Persona } from '../../types';
import Modal from '../Layout/Modal';
import { escapeHtml } from '../../utils/helpers';

interface PersonaDetailModalProps {
  persona: Persona | null;
  onClose: () => void;
}

const PersonaDetailModal: React.FC<PersonaDetailModalProps> = ({ persona, onClose }) => {
  if (!persona) return null;

  return (
    <Modal
      isOpen={!!persona}
      onClose={onClose}
      title={`${persona.emoji} ${persona.name}`}
      maxWidth="700px"
    >
      <div className="persona-detail">
        <div className="persona-detail-header">
          <div className="persona-detail-title">{escapeHtml(persona.title)}</div>
          <span className={`persona-detail-badge ${persona.category}`}>
            {escapeHtml(persona.category)}
          </span>
        </div>

        <div className="persona-detail-section">
          <span className="detail-label">Core question:</span>
          <div className="detail-content">{escapeHtml(persona.core_question)}</div>
        </div>

        <div className="persona-detail-section">
          <span className="detail-label">Razor:</span>
          <div className="detail-content">{escapeHtml(persona.razor)}</div>
        </div>

        <div className="persona-detail-section">
          <span className="detail-label">Focus areas:</span>
          <div className="persona-detail-tags">
            {persona.focus_areas.map((area, index) => (
              <span key={`${persona.id}-focus-${index}`} className="focus-tag">
                {escapeHtml(area)}
              </span>
            ))}
          </div>
        </div>

        <div className="persona-detail-section">
          <span className="detail-label">Traits:</span>
          <ul className="persona-detail-traits">
            {persona.traits.map((trait, index) => (
              <li key={`${persona.id}-trait-${index}`}>
                <strong>{escapeHtml(trait.name)}:</strong> {escapeHtml(trait.description)}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Modal>
  );
};

export default PersonaDetailModal;
