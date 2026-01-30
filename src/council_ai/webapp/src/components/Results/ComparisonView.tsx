/**
 * ComparisonView Component - Side-by-side consultation comparison
 */
import React, { useMemo } from 'react';
import type { ConsultationResult, MemberResponse } from '../../types';
import { escapeHtml, formatTimestamp } from '../../utils/helpers';

interface ComparisonViewProps {
  leftResult: ConsultationResult | null;
  rightResult: ConsultationResult | null;
  leftLabel?: string;
  rightLabel?: string;
  onSwap?: () => void;
}

interface ResponsePair {
  key: string;
  personaName: string;
  personaEmoji: string;
  personaTitle: string;
  left?: MemberResponse;
  right?: MemberResponse;
}

const ComparisonView: React.FC<ComparisonViewProps> = ({
  leftResult,
  rightResult,
  leftLabel = 'Consultation A',
  rightLabel = 'Consultation B',
  onSwap,
}) => {
  const responsePairs = useMemo(() => {
    const pairMap = new Map<string, ResponsePair>();

    const addResponse = (response: MemberResponse, side: 'left' | 'right') => {
      const key = response.persona_id || response.persona_name || response.persona_title;
      if (!key) {
        return;
      }
      const existing = pairMap.get(key) || {
        key,
        personaName: response.persona_name,
        personaEmoji: response.persona_emoji,
        personaTitle: response.persona_title,
      };
      pairMap.set(key, {
        ...existing,
        [side]: response,
        personaName: existing.personaName || response.persona_name,
        personaEmoji: existing.personaEmoji || response.persona_emoji,
        personaTitle: existing.personaTitle || response.persona_title,
      });
    };

    leftResult?.responses.forEach((response) => addResponse(response, 'left'));
    rightResult?.responses.forEach((response) => addResponse(response, 'right'));

    return Array.from(pairMap.values()).sort((a, b) => a.personaName.localeCompare(b.personaName));
  }, [leftResult, rightResult]);

  const renderMeta = (result: ConsultationResult | null) => {
    if (!result) {
      return (
        <div className="comparison-meta comparison-meta--empty">No consultation selected.</div>
      );
    }
    return (
      <div className="comparison-meta">
        <div className="comparison-meta-row">
          <span className="comparison-meta-label">Query</span>
          <span className="comparison-meta-value">{escapeHtml(result.query)}</span>
        </div>
        {result.context && (
          <div className="comparison-meta-row">
            <span className="comparison-meta-label">Context</span>
            <span className="comparison-meta-value">{escapeHtml(result.context)}</span>
          </div>
        )}
        <div className="comparison-meta-row">
          <span className="comparison-meta-label">Mode</span>
          <span className="comparison-meta-value">{escapeHtml(result.mode)}</span>
        </div>
        <div className="comparison-meta-row">
          <span className="comparison-meta-label">Timestamp</span>
          <span className="comparison-meta-value">{formatTimestamp(result.timestamp)}</span>
        </div>
        <div className="comparison-meta-row">
          <span className="comparison-meta-label">Responses</span>
          <span className="comparison-meta-value">{result.responses.length}</span>
        </div>
      </div>
    );
  };

  return (
    <section className="comparison-view">
      <div className="comparison-header">
        <div>
          <h3>Side-by-side Comparison</h3>
          <p className="comparison-subtitle">
            Review queries, synthesis, and persona responses in parallel.
          </p>
        </div>
        {onSwap && (
          <button
            type="button"
            className="btn btn-secondary btn-sm comparison-swap"
            onClick={onSwap}
          >
            Swap
          </button>
        )}
      </div>

      <div className="comparison-grid">
        <div className="comparison-column">
          <div className="comparison-column-header">{escapeHtml(leftLabel)}</div>
          {renderMeta(leftResult)}
          {leftResult?.synthesis && (
            <div className="comparison-synthesis">
              <span className="comparison-meta-label">Synthesis</span>
              <p>{escapeHtml(leftResult.synthesis)}</p>
            </div>
          )}
        </div>
        <div className="comparison-column">
          <div className="comparison-column-header">{escapeHtml(rightLabel)}</div>
          {renderMeta(rightResult)}
          {rightResult?.synthesis && (
            <div className="comparison-synthesis">
              <span className="comparison-meta-label">Synthesis</span>
              <p>{escapeHtml(rightResult.synthesis)}</p>
            </div>
          )}
        </div>
      </div>

      <div className="comparison-responses">
        <div className="comparison-response-row comparison-response-row--header">
          <div className="comparison-response-cell comparison-response-cell--persona">Persona</div>
          <div className="comparison-response-cell">{escapeHtml(leftLabel)}</div>
          <div className="comparison-response-cell">{escapeHtml(rightLabel)}</div>
        </div>

        {responsePairs.length === 0 && (
          <div className="comparison-empty-state">
            Select two consultations to compare responses.
          </div>
        )}

        {responsePairs.map((pair) => (
          <div key={pair.key} className="comparison-response-row">
            <div className="comparison-response-cell comparison-response-cell--persona">
              <span className="comparison-persona-emoji">
                {escapeHtml(pair.personaEmoji || '🤖')}
              </span>
              <div className="comparison-persona-details">
                <div className="comparison-persona-name">
                  {escapeHtml(pair.personaName || pair.key)}
                </div>
                <div className="comparison-persona-title">
                  {escapeHtml(pair.personaTitle || '')}
                </div>
              </div>
            </div>
            <div
              className={`comparison-response-cell ${pair.left ? '' : 'comparison-response-cell--empty'}`}
            >
              {pair.left ? (
                <p className="text-wrap-pre">{escapeHtml(pair.left.content)}</p>
              ) : (
                <span className="comparison-response-placeholder">No response</span>
              )}
            </div>
            <div
              className={`comparison-response-cell ${pair.right ? '' : 'comparison-response-cell--empty'}`}
            >
              {pair.right ? (
                <p className="text-wrap-pre">{escapeHtml(pair.right.content)}</p>
              ) : (
                <span className="comparison-response-placeholder">No response</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default ComparisonView;
