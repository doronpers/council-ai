/**
 * ErrorBoundary Component - Catches React errors and displays fallback UI
 */
import React, { Component, ReactNode } from 'react';
import './ErrorBoundary.css';
import ErrorDisplay from './ErrorDisplay';
import { createError, ErrorCategory } from '../../utils/errors';
import { logError } from '../../utils/errorLogger';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  showDetails?: boolean;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

/**
 * Error Boundary component that catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing the whole React application.
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log the error for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Update state with error info
    this.setState({
      error,
      errorInfo,
    });

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);

    // Send error to logging service (if available)
    this.logError(error, errorInfo);
  }

  private logError = (error: Error, errorInfo: React.ErrorInfo) => {
    // Extract component name from component stack if available
    const componentMatch = errorInfo.componentStack.match(/^\s*at\s+(\w+)/);
    const component = componentMatch ? componentMatch[1] : 'Unknown';

    // Log error with full context
    logError(error, {
      action: 'React component error',
      component,
      additionalData: {
        componentStack: errorInfo.componentStack,
        errorBoundary: true,
      },
    });
  };

  private handleReload = () => {
    // Clear error state and reload the page
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });

    // Optionally reload the page
    window.location.reload();
  };

  private handleReportIssue = () => {
    // Create a GitHub issue or send error report
    const error = this.state.error;
    const errorInfo = this.state.errorInfo;

    if (error && errorInfo) {
      const title = encodeURIComponent(`React Error: ${error.message}`);
      const body = encodeURIComponent(`
## Error Details

**Error:** ${error.message}
**Component Stack:**
${errorInfo.componentStack}

**Stack Trace:**
${error.stack}

**Timestamp:** ${new Date().toISOString()}
**URL:** ${window.location.href}
**User Agent:** ${navigator.userAgent}

## Steps to Reproduce

1. [Describe what you were doing when the error occurred]

## Expected Behavior

[Describe what should have happened]

## Additional Context

[Add any other context about the problem here]
            `);

      const githubUrl = `https://github.com/doronpers/council-ai/issues/new?title=${title}&body=${body}&labels=bug`;
      window.open(githubUrl, '_blank');
    }
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error display
      const errorInfo = createError(
        ErrorCategory.UNKNOWN,
        this.state.error?.message || 'An unexpected error occurred',
        'Something went wrong with this part of the application.',
        ['Try refreshing the page', 'Clear your browser cache', 'Try a different browser'],
        [
          { label: 'Reload Page', action: this.handleReload },
          { label: 'Report Issue', action: this.handleReportIssue },
        ],
        'high',
        true
      );

      return (
        <div className="error-boundary-fallback">
          <ErrorDisplay
            error={errorInfo}
            onRetry={this.handleReload}
            showDetails={this.props.showDetails}
          />

          {/* Show technical details in development */}
          {process.env.NODE_ENV === 'development' && this.props.showDetails && (
            <details className="error-boundary-dev-details">
              <summary>Developer Details</summary>
              <pre className="error-boundary-stack">
                {this.state.error?.stack}
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Higher-order component to wrap components with error boundaries
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;

  return WrappedComponent;
}

export default ErrorBoundary;
