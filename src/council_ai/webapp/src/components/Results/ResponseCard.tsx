/**
 * ResponseCard Component - Display individual persona response
 */
import React, { useMemo, useState } from 'react';
import { useApp } from '../../context/AppContext';
import { useNotifications } from '../Layout/NotificationContainer';
import { escapeHtml, copyToClipboard } from '../../utils/helpers';

interface ResponseCardProps {
  personaId: string;
  personaName?: string;
  personaEmoji?: string;
  personaTitle?: string;
  content: string;
  error?: string;
  isStreaming?: boolean;
  provider?: string;
  model?: string;
  usage?: {
    input_tokens?: number;
    output_tokens?: number;
    total_tokens?: number;
  };
  onFollowUp?: (personaId: string, personaName: string) => void;
  onShare?: (personaId: string, content: string) => void;
}

const ResponseCard: React.FC<ResponseCardProps> = ({
  personaId,
  personaName,
  personaEmoji,
  personaTitle,
  content,
  error,
  isStreaming = false,
  provider,
  model,
  usage,
  onFollowUp,
  onShare,
}) => {
  const { personas } = useApp();
  const [showDetails, setShowDetails] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const { showNotification } = useNotifications();

  // Interaction states
  const likeKey = useMemo(() => `like-response-${personaId}`, [personaId]);
  const bookmarkKey = useMemo(() => `bookmark-response-${personaId}`, [personaId]);

  const [isLiked, setIsLiked] = useState(() => {
    try {
      return localStorage.getItem(likeKey) === 'true';
    } catch {
      return false;
    }
  });

  const [isBookmarked, setIsBookmarked] = useState(() => {
    try {
      return localStorage.getItem(bookmarkKey) === 'true';
    } catch {
      return false;
    }
  });

  const contentPreviewLimit = 500;
  const isTruncated = content.length > contentPreviewLimit;

  const contentPreview = useMemo(() => {
    if (!isTruncated) return content;
    return `${content.slice(0, contentPreviewLimit).trim()}…`;
  }, [content, isTruncated]);

  const favoriteKey = useMemo(() => `favorite-response-${personaId}`, [personaId]);
  const [isFavorited, setIsFavorited] = useState(() => {
    try {
      return localStorage.getItem(favoriteKey) === 'true';
    } catch {
      return false;
    }
  });

  // Get persona data from context if not provided
  const persona = personas.find((p) => p.id === personaId);
  const name = personaName || persona?.name || personaId;
  const emoji = personaEmoji || persona?.emoji || '🤖';
  const title = personaTitle || persona?.title || '';
  const focusAreas = persona?.focus_areas || [];

  const handleCopy = async () => {
    const success = await copyToClipboard(content);
    if (success) {
      setCopied(true);
      showNotification('Response copied to clipboard', 'success');
      setTimeout(() => setCopied(false), 2000);
    } else {
      showNotification('Failed to copy response', 'error');
    }
  };

  const handleFavorite = () => {
    const nextValue = !isFavorited;
    setIsFavorited(nextValue);
    try {
      localStorage.setItem(favoriteKey, nextValue ? 'true' : 'false');
    } catch {
      // ignore storage errors
    }
    showNotification(nextValue ? 'Response favorited' : 'Response removed from favorites', 'info');
  };

  const handleLike = () => {
    const nextValue = !isLiked;
    setIsLiked(nextValue);
    try {
      localStorage.setItem(likeKey, nextValue ? 'true' : 'false');
    } catch {
      // ignore storage errors
    }
    showNotification(nextValue ? 'Response liked' : 'Response unliked', 'info');
  };

  const handleBookmark = () => {
    const nextValue = !isBookmarked;
    setIsBookmarked(nextValue);
    try {
      localStorage.setItem(bookmarkKey, nextValue ? 'true' : 'false');
    } catch {
      // ignore storage errors
    }
    showNotification(nextValue ? 'Response bookmarked' : 'Bookmark removed', 'info');
  };

  const handleShare = () => {
    if (onShare) {
      onShare(personaId, content);
    } else {
      // Fallback: copy shareable link to clipboard
      const shareText = `${name}: ${content.slice(0, 200)}${content.length > 200 ? '...' : ''}`;
      copyToClipboard(shareText).then((success) => {
        if (success) {
          showNotification('Response copied for sharing', 'success');
        } else {
          showNotification('Failed to copy response', 'error');
        }
      });
    }
  };

  const handleFollowUp = () => {
    if (onFollowUp) {
      onFollowUp(personaId, name);
    }
  };

  return (
    <div id={`response-${personaId}`} className="response-card-enhanced" data-persona={personaId}>
      {/* Header */}
      <div className="response-header">
        <div className="response-persona-info">
          <span className="response-emoji">{escapeHtml(emoji)}</span>
          <div className="response-persona-details">
            <div className="response-persona-name">{escapeHtml(name)}</div>
            <div className="response-persona-title">{escapeHtml(title)}</div>
          </div>
        </div>
        <div className="response-actions">
          <button
            type="button"
            className={`response-action-btn ${isLiked ? 'liked' : ''}`}
            onClick={handleLike}
            title={isLiked ? 'Unlike' : 'Like response'}
          >
            {isLiked ? '❤️' : '🤍'}
          </button>
          <button
            type="button"
            className={`response-action-btn ${isFavorited ? 'favorited' : ''}`}
            onClick={handleFavorite}
            title={isFavorited ? 'Unfavorite' : 'Favorite response'}
          >
            ★
          </button>
          <button
            type="button"
            className={`response-action-btn ${isBookmarked ? 'bookmarked' : ''}`}
            onClick={handleBookmark}
            title={isBookmarked ? 'Remove bookmark' : 'Bookmark response'}
          >
            📖
          </button>
          <button
            type="button"
            className="response-action-btn"
            onClick={handleCopy}
            title="Copy response"
          >
            {copied ? '✓' : '📋'}
          </button>
          <button
            type="button"
            className="response-action-btn"
            onClick={handleShare}
            title="Share response"
          >
            🔗
          </button>
          {onFollowUp && (
            <button
              type="button"
              className="response-action-btn"
              onClick={handleFollowUp}
              title="Ask follow-up question"
            >
              💬
            </button>
          )}
          <button
            type="button"
            className={`response-action-btn ${showDetails ? 'active' : ''}`}
            onClick={() => setShowDetails(!showDetails)}
            title="Toggle details"
          >
            ℹ️
          </button>
        </div>
      </div>

      {/* Focus areas */}
      {focusAreas.length > 0 && (
        <div className="response-focus-areas">
          {focusAreas.slice(0, 4).map((area, index) => (
            <span key={index} className="response-focus-tag">
              {escapeHtml(area)}
            </span>
          ))}
        </div>
      )}

      {/* Content */}
      <div className="response-content-wrapper">
        {error ? (
          <p className="error">{escapeHtml(error)}</p>
        ) : (
          <p
            className={`${isStreaming ? 'streaming-content' : ''} ${!isExpanded && isTruncated ? 'response-content-truncated' : ''}`}
            style={{ whiteSpace: 'pre-wrap' }}
          >
            {isExpanded ? content : contentPreview}
            {isStreaming && <span className="loading"></span>}
          </p>
        )}
      </div>

      {isTruncated && !error && (
        <div className="response-expand-controls">
          <button
            type="button"
            className="response-expand-btn"
            onClick={() => setIsExpanded((prev) => !prev)}
          >
            {isExpanded ? 'Show less' : 'Show more'}
          </button>
        </div>
      )}

      {/* Details (toggle) */}
      {showDetails && (
        <div id={`response-details-${personaId}`} className="response-details">
          {persona && (
            <>
              <div className="response-category">
                <strong>Category:</strong> {escapeHtml(persona.category)}
              </div>
              <div className="response-all-focus">
                <strong>Focus Areas:</strong> {focusAreas.join(', ')}
              </div>
            </>
          )}
          {(provider || model) && (
            <div className="response-model-info">
              <strong>Model:</strong>{' '}
              {provider && model ? `${provider}/${model}` : provider || model || 'Unknown'}
            </div>
          )}
          {usage && (
            <div className="response-usage">
              <strong>Tokens:</strong>
              {usage.input_tokens !== undefined && ` Input: ${usage.input_tokens}`}
              {usage.output_tokens !== undefined && ` Output: ${usage.output_tokens}`}
              {usage.total_tokens !== undefined && ` Total: ${usage.total_tokens}`}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ResponseCard;
