/**
 * MemberStatusCard Component - Status display during consultation
 */
import React from 'react';
import type { MemberStatusInfo } from '../../types';
import { escapeHtml } from '../../utils/helpers';

interface MemberStatusCardProps {
  member: MemberStatusInfo;
}

const MemberStatusCard: React.FC<MemberStatusCardProps> = ({ member }) => {
  const statusClass = `member-status-card member-status-card--${member.status}`;

  const statusText = {
    pending: 'Waiting...',
    responding: 'Responding...',
    completed: 'Complete',
    error: 'Error',
  }[member.status];

  return (
    <div className={statusClass}>
      <span className="member-status-emoji">{escapeHtml(member.emoji)}</span>
      <div className="member-status-info">
        <div className="member-status-name">{escapeHtml(member.name)}</div>
        <div className="member-status-text">{statusText}</div>
      </div>
    </div>
  );
};

export default MemberStatusCard;
