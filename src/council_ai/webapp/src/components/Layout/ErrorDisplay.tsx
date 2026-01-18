/**
 * ErrorDisplay Component - Enhanced error display with recovery guidance
 */
import React, { useState, useEffect } from 'react';
import { ErrorInfo, getErrorIcon, getSeverityLevel, isRecoverable } from '../../utils/errors';

interface ErrorDisplayProps {
  error: ErrorInfo;
  onRetry?: () => void;
  onDismiss?: () => void;
  onAction?: (action: () => void) => void;
  autoDismiss?: boolean;
  autoDismissDelay?: number;
  className?: string;
  showDetails?: boolean;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  onRetry,
  onDismiss,
  onAction,
  autoDismiss = true,
  autoDismissDelay = 5000,
  className = '',
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [timeLeft, setTimeLeft] = useState(autoDismissDelay / 1000);

  // Auto-dismiss timer for low severity errors
  useEffect(() => {
    if (!autoDismiss || error.severity === 'high' || error.severity === 'critical') {
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          setIsVisible(false);
          onDismiss?.();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [autoDismiss, error.severity, onDismiss]);

  // Handle action button clicks
  const handleAction = (action: () => void) => {
    onAction?.(action);
    action();
  };

  // Handle retry
  const handleRetry = () => {
    onRetry?.();
    setIsVisible(false);
  };

  // Handle dismiss
  const handleDismiss = () => {
    setIsVisible(false);
    onDismiss?.();
  };

  if (!isVisible) {
    return null;
  }

  const severity = getSeverityLevel(error);
  const recoverable = isRecoverable(error);
  const icon = getErrorIcon(error.category);

  // Severity-based styling
  const severityClasses = {
    low: 'error-display--low',
    medium: 'error-display--medium',
    high: 'error-display--high',
    critical: 'error-display--critical',
  };

  return (
    <div
      className={`error-display ${severityClasses[severity]} ${className}`}
      role="alert"
      aria-live="assertive"
    >
      {/* Header */}
      <div className="error-display-header">
        <div className="error-display-icon">
          <span role="img" aria-label={`${error.category} error`}>
            {icon}
          </span>
        </div>

        <div className="error-display-content">
          <h4 className="error-display-title">{error.userMessage}</h4>

          {/* Auto-dismiss countdown for low severity */}
          {autoDismiss && severity === 'low' && timeLeft > 0 && (
            <div className="error-display-countdown">Auto-dismissing in {timeLeft}s</div>
          )}
        </div>

        <div className="error-display-actions">
          {/* Expand/collapse details */}
          <button
            type="button"
            className="error-display-toggle"
            onClick={() => setIsExpanded(!isExpanded)}
            aria-expanded={isExpanded}
            aria-label="Toggle error details"
          >
            {isExpanded ? '▼' : '▶'}
          </button>

          {/* Dismiss button */}
          <button
            type="button"
            className="error-display-dismiss"
            onClick={handleDismiss}
            aria-label="Dismiss error"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Suggestions */}
      {error.suggestions.length > 0 && (
        <div className="error-display-suggestions">
          <h5>Suggestions:</h5>
          <ul>
            {error.suggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Action buttons */}
      {(recoverable || error.actions) && (
        <div className="error-display-action-buttons">
          {/* Retry button for recoverable errors */}
          {recoverable && onRetry && (
            <button
              type="button"
              className="btn btn-secondary error-display-retry"
              onClick={handleRetry}
            >
              Try Again
            </button>
          )}

          {/* Custom action buttons */}
          {error.actions?.map((action, index) => (
            <button
              key={index}
              type="button"
              className="btn btn-secondary error-display-action"
              onClick={() => handleAction(action.action)}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}

      {/* Expandable details */}
      {isExpanded && (
        <div className="error-display-details">
          <h5>Technical Details:</h5>
          <div className="error-display-details-content">
            <div className="error-detail-row">
              <strong>Category:</strong> {error.category}
            </div>
            <div className="error-detail-row">
              <strong>Severity:</strong> {error.severity}
            </div>
            <div className="error-detail-row">
              <strong>Recoverable:</strong> {recoverable ? 'Yes' : 'No'}
            </div>
            {error.code && (
              <div className="error-detail-row">
                <strong>Code:</strong> {error.code}
              </div>
            )}
            <div className="error-detail-row">
              <strong>Message:</strong>
              <pre className="error-message">{error.message}</pre>
            </div>
            {error.details && (
              <div className="error-detail-row">
                <strong>Additional Info:</strong>
                <pre className="error-details">{JSON.stringify(error.details, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ErrorDisplay;
