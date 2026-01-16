/**
 * HistoryItem Component - Individual history entry
 */
import React from 'react';
import type { HistoryEntry } from '../../types';
import { formatTimestamp, truncate } from '../../utils/helpers';
import { deleteHistoryEntry } from '../../utils/api';

interface HistoryItemProps {
    entry: HistoryEntry;
    onDeleted: () => void;
}

const HistoryItem: React.FC<HistoryItemProps> = ({ entry, onDeleted }) => {
    const handleDelete = async () => {
        try {
            await deleteHistoryEntry(entry.id);
            onDeleted();
        } catch (err) {
            console.error('Failed to delete history entry:', err);
        }
    };

    return (
        <div className="history-item">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 500, marginBottom: '4px' }}>
                        {truncate(entry.query, 60)}
                    </div>
                    <div className="muted" style={{ fontSize: '12px' }}>
                        {formatTimestamp(entry.timestamp)} · {entry.mode} · {entry.member_count} members
                    </div>
                </div>
                <button
                    type="button"
                    className="response-action-btn"
                    onClick={handleDelete}
                    title="Delete entry"
                    style={{ marginLeft: '12px' }}
                >
                    🗑️
                </button>
            </div>
        </div>
    );
};

export default HistoryItem;
