/**
 * HistoryItem Component - Individual history entry
 */
import React, { useState } from 'react';
import type { HistoryEntry, ConsultationResult } from '../../types';
import { formatTimestamp, truncate } from '../../utils/helpers';
import { deleteHistoryEntry, getConsultation, updateConsultationMetadata } from '../../utils/api';

interface HistoryItemProps {
  entry: HistoryEntry;
  onDeleted: () => void;
  onView?: (result: ConsultationResult) => void;
}

const HistoryItem: React.FC<HistoryItemProps> = ({ entry, onDeleted, onView }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [tags, setTags] = useState(entry.tags || []);
  const [notes, setNotes] = useState(entry.notes || '');
  const [isSaving, setIsSaving] = useState(false);
  const [isViewing, setIsViewing] = useState(false);

  const handleDelete = async () => {
    if (!confirm('Delete this consultation?')) return;
    try {
      await deleteHistoryEntry(entry.id);
      onDeleted();
    } catch (err) {
      console.error('Failed to delete history entry:', err);
      alert('Failed to delete entry');
    }
  };

  const handleView = async () => {
    setIsViewing(true);
    try {
      const result = await getConsultation(entry.id);
      if (onView) {
        onView(result);
      } else {
        // Fallback: show in alert if no handler
        alert(
          `Query: ${result.query}\n\nResponses: ${result.responses.length}\nSynthesis: ${result.synthesis || 'N/A'}`
        );
      }
    } catch (err) {
      console.error('Failed to load consultation:', err);
      alert('Failed to load consultation details');
    } finally {
      setIsViewing(false);
    }
  };

  const handleSaveMetadata = async () => {
    setIsSaving(true);
    try {
      await updateConsultationMetadata(entry.id, tags, notes);
      setIsEditing(false);
    } catch (err) {
      console.error('Failed to save metadata:', err);
      alert('Failed to save tags/notes');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancelEdit = () => {
    setTags(entry.tags || []);
    setNotes(entry.notes || '');
    setIsEditing(false);
  };

  return (
    <div className="history-item">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 500, marginBottom: '4px' }}>{truncate(entry.query, 60)}</div>
          <div className="muted" style={{ fontSize: '12px' }}>
            {formatTimestamp(entry.timestamp)} · {entry.mode} · {entry.member_count} members
          </div>
          {entry.tags && entry.tags.length > 0 && (
            <div style={{ marginTop: '4px', fontSize: '11px' }}>
              {entry.tags.map((tag, i) => (
                <span
                  key={i}
                  style={{
                    display: 'inline-block',
                    padding: '2px 6px',
                    marginRight: '4px',
                    backgroundColor: 'var(--accent-blue, #0066cc)',
                    color: 'white',
                    borderRadius: '3px',
                    fontSize: '10px',
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
          {entry.notes && (
            <div
              className="muted"
              style={{ marginTop: '4px', fontSize: '11px', fontStyle: 'italic' }}
            >
              {truncate(entry.notes, 80)}
            </div>
          )}
        </div>
        <div style={{ display: 'flex', gap: '4px', marginLeft: '12px' }}>
          <button
            type="button"
            className="response-action-btn"
            onClick={handleView}
            disabled={isViewing}
            title="View details"
          >
            {isViewing ? '⏳' : '👁️'}
          </button>
          <button
            type="button"
            className="response-action-btn"
            onClick={() => setIsEditing(!isEditing)}
            title="Edit tags/notes"
          >
            ✏️
          </button>
          <button
            type="button"
            className="response-action-btn"
            onClick={handleDelete}
            title="Delete entry"
          >
            🗑️
          </button>
        </div>
      </div>

      {isEditing && (
        <div
          style={{
            marginTop: '12px',
            padding: '12px',
            backgroundColor: 'var(--bg-secondary, #f5f5f5)',
            borderRadius: '4px',
          }}
        >
          <div style={{ marginBottom: '8px' }}>
            <label
              style={{ display: 'block', fontSize: '12px', marginBottom: '4px', fontWeight: 500 }}
            >
              Tags (comma-separated):
            </label>
            <input
              type="text"
              value={tags.join(', ')}
              onChange={(e) =>
                setTags(
                  e.target.value
                    .split(',')
                    .map((t) => t.trim())
                    .filter((t) => t)
                )
              }
              placeholder="tag1, tag2, tag3"
              style={{
                width: '100%',
                padding: '6px',
                fontSize: '12px',
                border: '1px solid var(--border, #ddd)',
                borderRadius: '3px',
              }}
            />
          </div>
          <div style={{ marginBottom: '8px' }}>
            <label
              style={{ display: 'block', fontSize: '12px', marginBottom: '4px', fontWeight: 500 }}
            >
              Notes:
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add notes about this consultation..."
              rows={3}
              style={{
                width: '100%',
                padding: '6px',
                fontSize: '12px',
                border: '1px solid var(--border, #ddd)',
                borderRadius: '3px',
                fontFamily: 'inherit',
              }}
            />
          </div>
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={handleCancelEdit}
              disabled={isSaving}
              style={{
                padding: '6px 12px',
                fontSize: '12px',
                border: '1px solid var(--border, #ddd)',
                borderRadius: '3px',
                backgroundColor: 'white',
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSaveMetadata}
              disabled={isSaving}
              style={{
                padding: '6px 12px',
                fontSize: '12px',
                border: 'none',
                borderRadius: '3px',
                backgroundColor: 'var(--accent-blue, #0066cc)',
                color: 'white',
                cursor: 'pointer',
              }}
            >
              {isSaving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryItem;
