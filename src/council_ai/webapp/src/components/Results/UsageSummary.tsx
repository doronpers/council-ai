/**
 * UsageSummary Component - Display token usage summary
 */
import React from 'react';

interface UsageSummaryProps {
  usageSummary?: {
    total_input_tokens: number;
    total_output_tokens: number;
    total_tokens: number;
    estimated_cost?: number;
  };
}

const UsageSummary: React.FC<UsageSummaryProps> = ({ usageSummary }) => {
  if (!usageSummary) {
    return null;
  }

  const formatNumber = (num: number) => num.toLocaleString();

  return (
    <div className="usage-summary">
      <h3>Token Usage</h3>
      <div className="usage-stats">
        <div className="usage-stat">
          <span className="usage-label">Input:</span>
          <span className="usage-value">{formatNumber(usageSummary.total_input_tokens)}</span>
        </div>
        <div className="usage-stat">
          <span className="usage-label">Output:</span>
          <span className="usage-value">{formatNumber(usageSummary.total_output_tokens)}</span>
        </div>
        <div className="usage-stat total">
          <span className="usage-label">Total:</span>
          <span className="usage-value">{formatNumber(usageSummary.total_tokens)}</span>
        </div>
        {usageSummary.estimated_cost !== undefined && (
          <div className="usage-stat cost">
            <span className="usage-label">Est. Cost:</span>
            <span className="usage-value">${usageSummary.estimated_cost.toFixed(4)}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default UsageSummary;
