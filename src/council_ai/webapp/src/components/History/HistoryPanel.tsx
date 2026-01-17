/**
 * HistoryPanel Component - Consultation history display
 */
import React, { useState, useEffect } from 'react';
import { loadHistory } from '../../utils/api';
import HistoryItem from './HistoryItem';
import type { HistoryEntry, ConsultationResult } from '../../types';

const HistoryPanel: React.FC = () => {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewingResult, setViewingResult] = useState<ConsultationResult | null>(null);

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
              onView={setViewingResult}
            />
          ))}
        </div>
      )}

      {viewingResult && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '20px',
          }}
          onClick={() => setViewingResult(null)}
        >
          <div
            style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              padding: '24px',
              maxWidth: '800px',
              maxHeight: '90vh',
              overflow: 'auto',
              boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '16px',
              }}
            >
              <h3 style={{ margin: 0 }}>Consultation Details</h3>
              <button
                onClick={() => setViewingResult(null)}
                style={{
                  border: 'none',
                  background: 'none',
                  fontSize: '24px',
                  cursor: 'pointer',
                  padding: '0 8px',
                }}
              >
                ×
              </button>
            </div>
            <div style={{ marginBottom: '12px' }}>
              <strong>Query:</strong>
              <div
                style={{
                  marginTop: '4px',
                  padding: '8px',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '4px',
                }}
              >
                {viewingResult.query}
              </div>
            </div>
            {viewingResult.context && (
              <div style={{ marginBottom: '12px' }}>
                <strong>Context:</strong>
                <div
                  style={{
                    marginTop: '4px',
                    padding: '8px',
                    backgroundColor: '#f5f5f5',
                    borderRadius: '4px',
                  }}
                >
                  {viewingResult.context}
                </div>
              </div>
            )}
            <div style={{ marginBottom: '12px' }}>
              <strong>Responses ({viewingResult.responses.length}):</strong>
              <div style={{ marginTop: '8px', maxHeight: '300px', overflow: 'auto' }}>
                {viewingResult.responses.map((response, i) => (
                  <div
                    key={i}
                    style={{
                      marginBottom: '12px',
                      padding: '12px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                    }}
                  >
                    <div style={{ fontWeight: 500, marginBottom: '4px' }}>
                      {response.persona_emoji} {response.persona_name} ({response.persona_title})
                    </div>
                    <div style={{ fontSize: '14px', color: '#666' }}>{response.content}</div>
                  </div>
                ))}
              </div>
            </div>
            {viewingResult.synthesis && (
              <div style={{ marginBottom: '12px' }}>
                <strong>Synthesis:</strong>
                <div
                  style={{
                    marginTop: '4px',
                    padding: '8px',
                    backgroundColor: '#e8f4f8',
                    borderRadius: '4px',
                  }}
                >
                  {viewingResult.synthesis}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
};

export default HistoryPanel;
