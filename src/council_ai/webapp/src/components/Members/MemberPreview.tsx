/**
 * MemberPreview Component - Preview of selected council members
 */
import React from 'react';
import { useApp } from '../../context/AppContext';
import MemberCard from './MemberCard';
import { getDefaultPersonasForDomain } from '../../utils/helpers';

const MemberPreview: React.FC = () => {
  const { personas, domains, settings, selectedMembers } = useApp();

  // Get effective member IDs (custom selection or domain defaults)
  const effectiveMembers =
    selectedMembers.length > 0
      ? selectedMembers
      : getDefaultPersonasForDomain(domains, settings.domain || 'general');

  // Get persona objects for display
  const displayedPersonas = personas.filter((p) => effectiveMembers.includes(p.id));

  return (
    <div className="member-preview">
      <div className="flex-between mb-12">
        <span className="muted">
          {selectedMembers.length > 0 ? 'Custom Selection' : 'Domain Defaults'}
        </span>
        <span id="member-count" className="muted">
          {displayedPersonas.length} member{displayedPersonas.length !== 1 ? 's' : ''}
        </span>
      </div>

      {displayedPersonas.length === 0 ? (
        <div className="empty-state">
          <p>No members selected</p>
          <p className="hint">Select members above or choose a domain with defaults.</p>
        </div>
      ) : (
        <div id="member-cards" className="member-cards-grid">
          {displayedPersonas.map((persona) => (
            <MemberCard
              key={persona.id}
              persona={persona}
              isSelected={selectedMembers.includes(persona.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default MemberPreview;
