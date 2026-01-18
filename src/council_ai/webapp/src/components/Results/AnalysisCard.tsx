/**
 * AnalysisCard Component - Display consultation analysis
 */
import React from 'react';
import type { ConsultationAnalysis } from '../../types';

interface AnalysisCardProps {
  analysis: ConsultationAnalysis;
}

const AnalysisCard: React.FC<AnalysisCardProps> = ({ analysis }) => {
  const consensusPercent = Math.round(analysis.consensus_score * 100);

  return (
    <div className="analysis-card" style={{ marginTop: '24px' }}>
      <h3>📊 Analysis</h3>

      {/* Consensus Meter */}
      <div className="consensus-meter">
        <div className="consensus-title">
          <span>Consensus Level</span>
          <span>{consensusPercent}%</span>
        </div>
        <div className="consensus-track">
          <div className="consensus-bar" style={{ width: `${consensusPercent}%` }} />
        </div>
      </div>

      {/* Key Agreements */}
      {analysis.key_agreements.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <h4 style={{ fontSize: '14px', marginBottom: '8px' }}>
            <span className="highlight-agreement">Key Agreements</span>
          </h4>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {analysis.key_agreements.map((point, index) => (
              <li key={index} style={{ marginBottom: '4px' }}>
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Key Tensions */}
      {analysis.key_tensions.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <h4 style={{ fontSize: '14px', marginBottom: '8px' }}>
            <span className="highlight-tension">Key Tensions</span>
          </h4>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {analysis.key_tensions.map((point, index) => (
              <li key={index} style={{ marginBottom: '4px' }}>
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <h4 style={{ fontSize: '14px', marginBottom: '8px' }}>💡 Recommendations</h4>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {analysis.recommendations.map((rec, index) => (
              <li key={index} style={{ marginBottom: '4px' }}>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default AnalysisCard;
