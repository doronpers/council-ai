/**
 * Session Details Component - Modal for viewing full session details
 */
import React, { useState } from 'react';
import Modal from '../Layout/Modal';
import type { ConsultationResult, MemberResponse } from '../../types';

interface SessionDetailsProps {
    session: {
        id: string;
        created_at: string;
        updated_at: string;
        title?: string;
        tags?: string[];
        is_active: boolean;
        consultations?: ConsultationResult[];
    };
    onClose: () => void;
    onDelete: () => void;
}

const SessionDetails: React.FC<SessionDetailsProps> = ({ session, onClose, onDelete }) => {
    const [expandedConsultation, setExpandedConsultation] = useState<number | null>(null);

    const formatDate = (dateString: string) => {
        try {
            return new Date(dateString).toLocaleString();
        } catch {
            return dateString;
        }
    };

    const handleExport = () => {
        const exportData = {
            session_id: session.id,
            title: session.title,
            created_at: session.created_at,
            updated_at: session.updated_at,
            consultations: session.consultations || [],
        };

        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `session-${session.id.slice(0, 8)}-${Date.now()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    const consultations = session.consultations || [];

    return (
        <Modal isOpen onClose={onClose} title="Session Details">
            <div className="session-details">
                {/* Header */}
                <div className="session-details-header">
                    <div className="session-details-info">
                        <h4>{session.title || 'Untitled Session'}</h4>
                        <p className="session-id-full" title={session.id}>
                            ID: {session.id}
                        </p>
                        <p className="session-time">
                            Created: {formatDate(session.created_at)}
                        </p>
                        <p className="session-time">
                            Updated: {formatDate(session.updated_at)}
                        </p>
                        {session.tags && session.tags.length > 0 && (
                            <div className="session-details-tags">
                                {session.tags.map((tag) => (
                                    <span key={tag} className="tag">
                                        {tag}
                                    </span>
                                ))}
                            </div>
                        )}
                        <div className="session-details-status">
                            <span className={`status-badge ${session.is_active ? 'active' : 'inactive'}`}>
                                {session.is_active ? 'Active' : 'Inactive'}
                            </span>
                            <span className="consultation-count">
                                {consultations.length} consultation{consultations.length !== 1 ? 's' : ''}
                            </span>
                        </div>
                    </div>

                    <div className="session-details-actions">
                        <button className="btn btn-secondary" onClick={handleExport} title="Export session">
                            📥 Export
                        </button>
                        <button className="btn btn-danger" onClick={onDelete} title="Delete session">
                            🗑️ Delete
                        </button>
                        <button className="btn btn-secondary" onClick={onClose}>
                            Close
                        </button>
                    </div>
                </div>

                {/* Consultations List */}
                <div className="session-details-consultations">
                    <h5>Consultations ({consultations.length})</h5>
                    {consultations.length === 0 ? (
                        <p className="empty">No consultations in this session</p>
                    ) : (
                        <div className="consultations-list">
                            {consultations.map((consultation, index) => (
                                <ConsultationSummary
                                    key={index}
                                    consultation={consultation}
                                    index={index}
                                    isExpanded={expandedConsultation === index}
                                    onToggleExpand={() =>
                                        setExpandedConsultation(expandedConsultation === index ? null : index)
                                    }
                                />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </Modal>
    );
};

interface ConsultationSummaryProps {
    consultation: ConsultationResult;
    index: number;
    isExpanded: boolean;
    onToggleExpand: () => void;
}

const ConsultationSummary: React.FC<ConsultationSummaryProps> = ({
    consultation,
    index,
    isExpanded,
    onToggleExpand,
}) => {
    const formatDate = (dateString: string) => {
        try {
            return new Date(dateString).toLocaleTimeString();
        } catch {
            return dateString;
        }
    };

    return (
        <div className="consultation-summary" onClick={onToggleExpand}>
            <div className="consultation-header">
                <div className="consultation-query">
                    <span className="consultation-index">#{index + 1}</span>
                    <span className="query-text">{consultation.query.slice(0, 60)}...</span>
                </div>
                <div className="consultation-meta">
                    <span className="consultation-mode">{consultation.mode}</span>
                    <span className="consultation-time">{formatDate(consultation.timestamp)}</span>
                    <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>▶</span>
                </div>
            </div>

            {isExpanded && (
                <div className="consultation-details">
                    {/* Query & Context */}
                    {consultation.query && (
                        <div className="detail-section">
                            <h6>Query</h6>
                            <p className="query-full">{consultation.query}</p>
                        </div>
                    )}

                    {consultation.context && (
                        <div className="detail-section">
                            <h6>Context</h6>
                            <p className="context-text">{consultation.context}</p>
                        </div>
                    )}

                    {/* Responses */}
                    <div className="detail-section">
                        <h6>Responses ({consultation.responses.length})</h6>
                        <div className="responses-list">
                            {consultation.responses.map((response: MemberResponse, idx: number) => (
                                <div key={idx} className="response-item">
                                    <div className="response-header">
                                        <span className="persona-emoji">{response.persona_emoji}</span>
                                        <span className="persona-name">{response.persona_name}</span>
                                        <span className="response-model">{response.model}</span>
                                    </div>
                                    <p className="response-content">{response.content.slice(0, 200)}...</p>
                                    {response.usage && (
                                        <p className="response-usage">
                                            Tokens: {response.usage.total_tokens || 0}
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Synthesis */}
                    {consultation.synthesis && (
                        <div className="detail-section">
                            <h6>Synthesis</h6>
                            <p className="synthesis-text">{consultation.synthesis.slice(0, 300)}...</p>
                        </div>
                    )}

                    {/* Analysis */}
                    {consultation.analysis && (
                        <div className="detail-section">
                            <h6>Analysis</h6>
                            <div className="analysis-scores">
                                <p>
                                    <strong>Consensus Score:</strong> {(consultation.analysis.consensus_score * 100).toFixed(0)}%
                                </p>
                                {consultation.analysis.key_agreements.length > 0 && (
                                    <div>
                                        <strong>Key Agreements:</strong>
                                        <ul>
                                            {consultation.analysis.key_agreements.slice(0, 2).map((item, i) => (
                                                <li key={i}>{item}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Usage Summary */}
                    {consultation.usage_summary && (
                        <div className="detail-section usage-summary">
                            <h6>Token Usage</h6>
                            <p>Input: {consultation.usage_summary.total_input_tokens}</p>
                            <p>Output: {consultation.usage_summary.total_output_tokens}</p>
                            <p className="total">
                                Total: {consultation.usage_summary.total_tokens}
                            </p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default SessionDetails;
