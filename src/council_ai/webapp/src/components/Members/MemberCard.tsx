/**
 * MemberCard Component - Display a single council member
 */
import React from 'react';
import type { Persona } from '../../types';
import { escapeHtml } from '../../utils/helpers';

interface MemberCardProps {
    persona: Persona;
    isSelected?: boolean;
}

const MemberCard: React.FC<MemberCardProps> = ({ persona, isSelected = false }) => {
    return (
        <div className={`member-card ${isSelected ? 'member-card--selected' : ''}`}>
            <div className="member-card-header">
                <span className="member-emoji">{escapeHtml(persona.emoji)}</span>
                <div className="member-info">
                    <div className="member-name">{escapeHtml(persona.name)}</div>
                    <div className="member-title">{escapeHtml(persona.title)}</div>
                </div>
            </div>
            <div className="member-focus-areas">
                {persona.focus_areas.slice(0, 3).map((area, index) => (
                    <span key={index} className="focus-tag">
                        {escapeHtml(area)}
                    </span>
                ))}
            </div>
        </div>
    );
};

export default MemberCard;
