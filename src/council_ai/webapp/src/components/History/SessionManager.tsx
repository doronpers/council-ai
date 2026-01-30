/**
 * Session Manager Component - Manage consultation sessions
 */
import React, { useState, useEffect, useCallback } from 'react';
import SessionItem from './SessionItem';
import SessionDetails from './SessionDetails';
import ConfirmDialog from '../Layout/ConfirmDialog';
import { useNotifications } from '../Layout/NotificationContainer';

export interface Session {
    id: string;
    created_at: string;
    updated_at: string;
    consultation_count: number;
    title?: string;
    tags?: string[];
    is_active: boolean;
}

const SessionManager: React.FC = () => {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [viewingSession, setViewingSession] = useState<string | null>(null);
    const [sessionDetails, setSessionDetails] = useState<any>(null);
    const [displayLimit, setDisplayLimit] = useState(10);
    const [hasMore, setHasMore] = useState(false);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);
    const { showNotification } = useNotifications();

    const fetchSessions = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(`/api/sessions?limit=${displayLimit}`);
            if (!response.ok) {
                throw new Error('Failed to fetch sessions');
            }
            const data = await response.json();
            setSessions(data.sessions || []);
            setHasMore((data.sessions || []).length >= displayLimit);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load sessions');
            showNotification('Failed to load sessions', 'error');
        } finally {
            setIsLoading(false);
        }
    }, [displayLimit, showNotification]);

    useEffect(() => {
        fetchSessions();
    }, [fetchSessions]);

    const handleViewDetails = async (sessionId: string) => {
        try {
            const response = await fetch(`/api/sessions/${sessionId}`);
            if (!response.ok) {
                throw new Error('Failed to fetch session details');
            }
            const data = await response.json();
            setSessionDetails(data);
            setViewingSession(sessionId);
        } catch (err) {
            showNotification(
                err instanceof Error ? err.message : 'Failed to load session',
                'error'
            );
        }
    };

    const handleDeleteClick = (sessionId: string) => {
        setSessionToDelete(sessionId);
        setShowDeleteConfirm(true);
    };

    const handleDeleteConfirm = async () => {
        if (!sessionToDelete) return;

        try {
            const response = await fetch(`/api/sessions/${sessionToDelete}`, {
                method: 'DELETE',
            });
            if (!response.ok) {
                throw new Error('Failed to delete session');
            }
            setSessions((prev) => prev.filter((s) => s.id !== sessionToDelete));
            if (viewingSession === sessionToDelete) {
                setViewingSession(null);
                setSessionDetails(null);
            }
            showNotification('Session deleted successfully', 'success');
        } catch (err) {
            showNotification(
                err instanceof Error ? err.message : 'Failed to delete session',
                'error'
            );
        } finally {
            setSessionToDelete(null);
        }
    };

    const handleLoadMore = () => {
        setDisplayLimit((prev) => prev + 10);
    };

    const handleRefresh = () => {
        fetchSessions();
    };

    if (isLoading && sessions.length === 0) {
        return <div className="session-manager loading">Loading sessions...</div>;
    }

    return (
        <div className="session-manager">
            <div className="session-header">
                <h3>Sessions ({sessions.length})</h3>
                <div className="session-controls">
                    <button onClick={handleRefresh} className="btn-icon" title="Refresh">
                        🔄
                    </button>
                </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="session-list">
                {sessions.length === 0 ? (
                    <div className="empty-state">No sessions found. Start a consultation to create one.</div>
                ) : (
                    sessions.map((session) => (
                        <SessionItem
                            key={session.id}
                            session={session}
                            isActive={viewingSession === session.id}
                            onView={() => handleViewDetails(session.id)}
                            onDelete={() => handleDeleteClick(session.id)}
                        />
                    ))
                )}
            </div>

            {hasMore && (
                <button className="btn-load-more" onClick={handleLoadMore}>
                    Load More Sessions
                </button>
            )}

            {viewingSession && sessionDetails && (
                <SessionDetails
                    session={sessionDetails}
                    onClose={() => {
                        setViewingSession(null);
                        setSessionDetails(null);
                    }}
                    onDelete={() => handleDeleteClick(viewingSession)}
                />
            )}

            <ConfirmDialog
                isOpen={showDeleteConfirm}
                onConfirm={handleDeleteConfirm}
                onCancel={() => {
                    setShowDeleteConfirm(false);
                    setSessionToDelete(null);
                }}
                title="Delete Session"
                message="Are you sure you want to delete this session and all its consultations? This action cannot be undone."
                confirmLabel="Delete"
                cancelLabel="Cancel"
                danger
            />
        </div>
    );
};

export default SessionManager;
