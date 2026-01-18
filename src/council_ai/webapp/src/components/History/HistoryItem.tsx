/**
 * HistoryItem Component - Individual history entry
 */
import React, { useState } from 'react';
import type { HistoryEntry, ConsultationResult } from '../../types';
import { formatTimestamp, truncate } from '../../utils/helpers';
import { deleteHistoryEntry, getConsultation, updateConsultationMetadata } from '../../utils/api';
import TagInput from './TagInput';
import { useNotifications } from '../Layout/NotificationContainer';

interface HistoryItemProps {
  entry: HistoryEntry;
  onDeleted: () => void;
  onView?: (result: ConsultationResult) => void;
  onCompare?: (entry: HistoryEntry, result: ConsultationResult) => void;
}

const HistoryItem: React.FC<HistoryItemProps> = ({ entry, onDeleted, onView, onCompare }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [tags, setTags] = useState(entry.tags || []);
  const [notes, setNotes] = useState(entry.notes || '');
  const [isSaving, setIsSaving] = useState(false);
  const [isViewing, setIsViewing] = useState(false);
  const [isComparing, setIsComparing] = useState(false);
  const { showNotification } = useNotifications();

  const handleDelete = async () => {
    // Use confirm for now, but could be replaced with a proper modal component
    if (!window.confirm('Delete this consultation? This action cannot be undone.')) {
      return;
    }
    try {
      await deleteHistoryEntry(entry.id);
      onDeleted();
      showNotification('Consultation deleted successfully', 'success');
    } catch (err) {
      console.error('Failed to delete history entry:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete entry';
      showNotification(`Error: ${errorMessage}`, 'error');
    }
  };

  const handleView = async () => {
    setIsViewing(true);
    try {
      const result = await getConsultation(entry.id);
      if (onView) {
        onView(result);
      } else {
        // Fallback: show notification if no handler
        // This should rarely happen as onView is typically provided
        showNotification('Consultation details loaded', 'info');
      }
    } catch (err) {
      console.error('Failed to load consultation:', err);
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to load consultation details';
      showNotification(`Error: ${errorMessage}`, 'error');
    } finally {
      setIsViewing(false);
    }
  };

  const handleCompare = async () => {
    if (!onCompare) {
      showNotification('Comparison unavailable', 'info');
      return;
    }
    setIsComparing(true);
    try {
      const result = await getConsultation(entry.id);
      onCompare(entry, result);
    } catch (err) {
      console.error('Failed to load consultation for comparison:', err);
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to load consultation details';
      showNotification(`Error: ${errorMessage}`, 'error');
    } finally {
      setIsComparing(false);
    }
  };

  const handleSaveMetadata = async () => {
    setIsSaving(true);
    try {
      await updateConsultationMetadata(entry.id, tags, notes);
      setIsEditing(false);
      showNotification('Tags and notes saved successfully', 'success');
    } catch (err) {
      console.error('Failed to save metadata:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to save tags/notes';
      showNotification(`Error: ${errorMessage}`, 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancelEdit = () => {
    // Check if there are unsaved changes
    const hasTagChanges = JSON.stringify(tags) !== JSON.stringify(entry.tags || []);
    const hasNoteChanges = notes !== (entry.notes || '');

    if (hasTagChanges || hasNoteChanges) {
      if (!window.confirm('You have unsaved changes. Discard them?')) {
        return;
      }
    }

    setTags(entry.tags || []);
    setNotes(entry.notes || '');
    setIsEditing(false);
  };

  return (
    <div className="history-item">
      <div className="history-item-header">
        <div className="history-item-content">
          <div className="history-item-query">{truncate(entry.query, 60)}</div>
          <div className="history-item-meta muted">
            {formatTimestamp(entry.timestamp)} · {entry.mode} · {entry.member_count} members
          </div>
          {entry.tags && entry.tags.length > 0 && (
            <div className="history-item-tags">
              {entry.tags.map((tag, i) => (
                <span key={`${entry.id}-tag-${i}-${tag}`} className="history-item-tag">
                  {tag}
                </span>
              ))}
            </div>
          )}
          {entry.notes && (
            <div className="history-item-notes muted">{truncate(entry.notes, 80)}</div>
          )}
        </div>
        <div className="history-item-actions">
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
            onClick={handleCompare}
            disabled={isComparing}
            title="Compare consultation"
          >
            {isComparing ? '⏳' : '⚖️'}
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
        <div className="history-edit-form">
          <div className="history-edit-form-field">
            <label className="history-edit-form-label">Tags:</label>
            <TagInput
              tags={tags}
              onChange={setTags}
              placeholder="Add tags..."
              disabled={isSaving}
            />
          </div>
          <div className="history-edit-form-field">
            <label className="history-edit-form-label">Notes:</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add notes about this consultation..."
              rows={3}
              className="history-edit-form-textarea"
              disabled={isSaving}
            />
          </div>
          <div className="history-edit-form-actions">
            <button
              type="button"
              onClick={handleCancelEdit}
              disabled={isSaving}
              className="history-edit-form-btn history-edit-form-btn--cancel"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSaveMetadata}
              disabled={isSaving}
              className="history-edit-form-btn history-edit-form-btn--save"
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
