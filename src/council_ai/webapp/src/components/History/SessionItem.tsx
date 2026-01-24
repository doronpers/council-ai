/**
 * Session Item Component - Individual session display
 */
import React from 'react';
import type { Session } from './SessionManager';

interface SessionItemProps {
    session: Session;
    isActive: boolean;
    onView: () => void;
    onDelete: () => void;
}

const SessionItem: React.FC<SessionItemProps> = ({ session, isActive, onView, onDelete }) => {
    const formatDate = (dateString: string) => {
        try {
            return new Date(dateString).toLocaleString();
        } catch {
            return dateString;
        }
    };

    const getDurationText = () => {
        try {
            const created = new Date(session.created_at);
            const updated = new Date(session.updated_at);
            const seconds = Math.floor((updated.getTime() - created.getTime()) / 1000);

            if (seconds < 60) return 'Just now';
            if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
            if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
            return `${Math.floor(seconds / 86400)}d ago`;
        } catch {
            return 'Unknown';
        }
    };

    return (
        <div className={`session-item ${isActive ? 'active' : ''}`}>
            <div className="session-item-main" onClick={onView}>
                <div className="session-item-header">
                    <div className="session-item-title">
                        <span className={`session-status ${session.is_active ? 'active' : 'inactive'}`}>
                            {session.is_active ? '●' : '○'}
                        </span>
                        <span className="session-id" title={session.id}>
                            {session.id.slice(0, 8)}...
                        </span>
                        {session.title && <span className="session-title">{session.title}</span>}
                    </div>
                    <div className="session-time">{getDurationText()}</div>
                </div>

                <div className="session-item-meta">
                    <span className="session-count">
                        {session.consultation_count} consultation{session.consultation_count !== 1 ? 's' : ''}
                    </span>
                    <span className="session-created">{formatDate(session.created_at)}</span>
                </div>

                {session.tags && session.tags.length > 0 && (
                    <div className="session-tags">
                        {session.tags.map((tag) => (
                            <span key={tag} className="tag">
                                {tag}
                            </span>
                        ))}
                    </div>
                )}
            </div>

            <div className="session-item-actions">
                <button
                    className="btn-icon"
                    onClick={(e) => {
                        e.stopPropagation();
                        onView();
                    }}
                    title="View details"
                >
                    📋
                </button>
                <button
                    className="btn-icon btn-danger"
                    onClick={(e) => {
                        e.stopPropagation();
                        onDelete();
                    }}
                    title="Delete session"
                >
                    🗑️
                </button>
            </div>
        </div>
    );
};

export default SessionItem;
