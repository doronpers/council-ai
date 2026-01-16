/**
 * MemberSelectionGrid Component - Checkbox grid for selecting council members
 */
import React from 'react';
import { useApp } from '../../context/AppContext';
import { escapeHtml } from '../../utils/helpers';

const MemberSelectionGrid: React.FC = () => {
    const { personas, selectedMembers, setSelectedMembers } = useApp();

    const handleToggle = (personaId: string) => {
        setSelectedMembers((prev) =>
            prev.includes(personaId)
                ? prev.filter((id) => id !== personaId)
                : [...prev, personaId]
        );
    };

    return (
        <div id="members-container" className="members-selection-grid">
            {personas.map((persona) => (
                <label key={persona.id} className="member-selection-item">
                    <input
                        type="checkbox"
                        className="member-checkbox"
                        checked={selectedMembers.includes(persona.id)}
                        onChange={() => handleToggle(persona.id)}
                    />
                    <div className="member-selection-card">
                        <span className="member-emoji">{escapeHtml(persona.emoji)}</span>
                        <span className="member-name-small">{escapeHtml(persona.name)}</span>
                    </div>
                </label>
            ))}
        </div>
    );
};

export default MemberSelectionGrid;
