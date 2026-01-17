/**
 * ResponseCard Component - Display individual persona response
 */
import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { escapeHtml, copyToClipboard } from '../../utils/helpers';

interface ResponseCardProps {
    personaId: string;
    personaName?: string;
    personaEmoji?: string;
    personaTitle?: string;
    content: string;
    error?: string;
    isStreaming?: boolean;
}

const ResponseCard: React.FC<ResponseCardProps> = ({
    personaId,
    personaName,
    personaEmoji,
    personaTitle,
    content,
    error,
    isStreaming = false,
}) => {
    const { personas } = useApp();
    const [showDetails, setShowDetails] = useState(false);
    const [copied, setCopied] = useState(false);

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
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div
            id={`response-${personaId}`}
            className="response-card-enhanced"
            data-persona={personaId}
        >
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
                        className="response-action-btn"
                        onClick={handleCopy}
                        title="Copy response"
                    >
                        {copied ? '✓' : '📋'}
                    </button>
                    <button
                        className="response-action-btn"
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
                        className={isStreaming ? 'streaming-content' : ''}
                        style={{ whiteSpace: 'pre-wrap' }}
                    >
                        {content}
                        {isStreaming && <span className="loading"></span>}
                    </p>
                )}
            </div>

            {/* Details (toggle) */}
            {showDetails && persona && (
                <div
                    id={`response-details-${personaId}`}
                    className="response-details"
                >
                    <div className="response-category">
                        <strong>Category:</strong> {escapeHtml(persona.category)}
                    </div>
                    <div className="response-all-focus">
                        <strong>Focus Areas:</strong> {focusAreas.join(', ')}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ResponseCard;
