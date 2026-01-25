/**
 * ErrorRecovery Component - Recovery actions for errors
 */
import React, { useState, useEffect } from 'react';
import { ErrorInfo, ErrorCategory } from '../../utils/errors';
import './ErrorRecovery.css';

interface ErrorRecoveryProps {
  error: ErrorInfo;
  onRetry?: () => void;
  onAction?: (action: string) => void;
  retryDelay?: number; // Delay in seconds before allowing retry
}

const ErrorRecovery: React.FC<ErrorRecoveryProps> = ({
  error,
  onRetry,
  onAction,
  retryDelay = 0,
}) => {
  const [timeLeft, setTimeLeft] = useState(retryDelay);
  const [canRetry, setCanRetry] = useState(retryDelay === 0);

  // Countdown timer for rate limit errors
  useEffect(() => {
    if (retryDelay === 0 || error.category !== ErrorCategory.RATE_LIMIT) {
      setCanRetry(true);
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          setCanRetry(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [retryDelay, error.category]);

  const handleRetry = () => {
    if (canRetry && onRetry) {
      onRetry();
    }
  };

  const handleAction = (action: string) => {
    if (onAction) {
      onAction(action);
    }

    // Execute common actions
    switch (action) {
      case 'open-settings':
        // Scroll to config section
        const configSection = document.getElementById('config-section');
        if (configSection) {
          configSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
          // Open the details element if it's closed
          if (configSection instanceof HTMLDetailsElement && !configSection.open) {
            configSection.open = true;
          }
        }
        break;
      case 'focus-query':
        const queryInput = document.getElementById('query');
        if (queryInput) {
          queryInput.focus();
          queryInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        break;
      case 'focus-base-url':
        const baseUrlInput = document.getElementById('base_url');
        if (baseUrlInput) {
          baseUrlInput.focus();
          baseUrlInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
          // Open config section if closed
          const configSection = document.getElementById('config-section');
          if (configSection instanceof HTMLDetailsElement && !configSection.open) {
            configSection.open = true;
          }
        }
        break;
      case 'diagnostics':
        // Open diagnostics (if available)
        const diagnosticsButton = document.querySelector('[data-diagnostics]');
        if (diagnosticsButton instanceof HTMLElement) {
          diagnosticsButton.click();
        }
        break;
      case 'switch-provider':
        // Focus provider select
        const providerSelect = document.getElementById('provider');
        if (providerSelect) {
          providerSelect.focus();
          const configSection = document.getElementById('config-section');
          if (configSection instanceof HTMLDetailsElement && !configSection.open) {
            configSection.open = true;
          }
        }
        break;
    }
  };

  if (!error.recoverable && !error.actions?.length) {
    return null;
  }

  return (
    <div className="error-recovery">
      {/* Retry button for recoverable errors */}
      {error.recoverable && onRetry && (
        <button
          type="button"
          className={`btn btn-primary error-recovery-retry ${!canRetry ? 'error-recovery-retry--disabled' : ''}`}
          onClick={handleRetry}
          disabled={!canRetry}
          aria-label="Retry the failed operation"
        >
          {error.category === ErrorCategory.RATE_LIMIT && !canRetry ? (
            <>Wait {timeLeft}s</>
          ) : (
            <>Retry</>
          )}
        </button>
      )}

      {/* Action buttons */}
      {error.actions?.map((action, index) => (
        <button
          key={index}
          type="button"
          className="btn btn-secondary error-recovery-action"
          onClick={() => {
            // Extract action string from the action function name or use label
            const actionString = action.label.toLowerCase().replace(/\s+/g, '-');
            handleAction(actionString);
            action.action();
          }}
        >
          {action.label}
        </button>
      ))}

      {/* Quick fix suggestions */}
      {error.suggestions.length > 0 && error.suggestions.length <= 3 && (
        <div className="error-recovery-quick-fixes">
          <span className="error-recovery-quick-fixes-label">Quick fixes:</span>
          {error.suggestions.slice(0, 2).map((suggestion, index) => (
            <button
              key={index}
              type="button"
              className="error-recovery-quick-fix"
              onClick={() => {
                // Try to infer action from suggestion
                if (suggestion.toLowerCase().includes('settings')) {
                  handleAction('open-settings');
                } else if (suggestion.toLowerCase().includes('query')) {
                  handleAction('focus-query');
                }
              }}
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ErrorRecovery;
