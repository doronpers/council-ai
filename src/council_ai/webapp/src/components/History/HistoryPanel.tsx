/**
 * HistoryPanel Component - Consultation history display
 */
import React, { useState, useEffect } from 'react';
import { loadHistory } from '../../utils/api';
import HistoryItem from './HistoryItem';
import type { HistoryEntry } from '../../types';

const HistoryPanel: React.FC = () => {
    const [history, setHistory] = useState<HistoryEntry[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchHistory = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await loadHistory(10);
            setHistory(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load history');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    return (
        <section className="panel" id="history-section">
            <h2>Recent Consultations</h2>

            {isLoading && (
                <div className="empty-state">
                    <span className="loading"></span> Loading history...
                </div>
            )}

            {error && (
                <div className="empty-state">
                    <p className="error">{error}</p>
                </div>
            )}

            {!isLoading && !error && history.length === 0 && (
                <div className="empty-state">
                    <p>No recent consultations</p>
                    <p className="hint">Your consultation history will appear here.</p>
                </div>
            )}

            {!isLoading && !error && history.length > 0 && (
                <div id="history-list">
                    {history.map((entry) => (
                        <HistoryItem
                            key={entry.id}
                            entry={entry}
                            onDeleted={fetchHistory}
                        />
                    ))}
                </div>
            )}
        </section>
    );
};

export default HistoryPanel;
