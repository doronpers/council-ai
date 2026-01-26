/**
 * Tests for ErrorBoundary component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ErrorBoundary, { withErrorBoundary } from '../../components/Layout/ErrorBoundary';

// Mock the error logger
vi.mock('../../utils/errorLogger', () => ({
  logError: vi.fn(),
}));

// Mock the errors utility
vi.mock('../../utils/errors', () => ({
  createError: vi.fn((category, message, description, suggestions, actions, severity, recoverable) => ({
    category,
    message,
    description,
    suggestions,
    actions,
    severity,
    recoverable,
  })),
  ErrorCategory: {
    UNKNOWN: 'unknown',
    NETWORK: 'network',
    VALIDATION: 'validation',
  },
}));

// Mock ErrorDisplay component
vi.mock('../../components/Layout/ErrorDisplay', () => ({
  default: ({ error, onRetry }: { error: { message: string }; onRetry: () => void }) => (
    <div data-testid="error-display">
      <p>{error.message}</p>
      <button onClick={onRetry}>Retry</button>
    </div>
  ),
}));

// Component that throws an error
const ThrowError: React.FC<{ shouldThrow?: boolean }> = ({ shouldThrow = true }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

// Suppress console.error for cleaner test output
const originalConsoleError = console.error;
beforeEach(() => {
  console.error = vi.fn();
});

afterEach(() => {
  console.error = originalConsoleError;
});

describe('ErrorBoundary', () => {
  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    );

    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('renders fallback UI when there is an error', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByTestId('error-display')).toBeInTheDocument();
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('renders custom fallback when provided', () => {
    const customFallback = <div data-testid="custom-fallback">Custom error UI</div>;

    render(
      <ErrorBoundary fallback={customFallback}>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
    expect(screen.getByText('Custom error UI')).toBeInTheDocument();
  });

  it('calls onError callback when error occurs', () => {
    const onError = vi.fn();

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(onError).toHaveBeenCalledTimes(1);
    expect(onError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String),
      })
    );
  });

  it('provides reload functionality', () => {
    // Mock window.location.reload
    const reloadMock = vi.fn();
    Object.defineProperty(window, 'location', {
      value: { reload: reloadMock },
      writable: true,
    });

    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    const retryButton = screen.getByText('Retry');
    fireEvent.click(retryButton);

    expect(reloadMock).toHaveBeenCalled();
  });

  it('catches errors in nested children', () => {
    const NestedComponent: React.FC = () => (
      <div>
        <div>
          <ThrowError />
        </div>
      </div>
    );

    render(
      <ErrorBoundary>
        <NestedComponent />
      </ErrorBoundary>
    );

    expect(screen.getByTestId('error-display')).toBeInTheDocument();
  });

  it('only catches errors in its subtree', () => {
    render(
      <div>
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
        <div data-testid="sibling">Sibling content</div>
      </div>
    );

    expect(screen.getByTestId('error-display')).toBeInTheDocument();
    expect(screen.getByTestId('sibling')).toBeInTheDocument();
    expect(screen.getByText('Sibling content')).toBeInTheDocument();
  });
});

describe('withErrorBoundary HOC', () => {
  it('wraps component with error boundary', () => {
    const TestComponent: React.FC<{ message: string }> = ({ message }) => (
      <div>{message}</div>
    );

    const WrappedComponent = withErrorBoundary(TestComponent);

    render(<WrappedComponent message="Hello world" />);

    expect(screen.getByText('Hello world')).toBeInTheDocument();
  });

  it('catches errors in wrapped component', () => {
    const WrappedThrowError = withErrorBoundary(ThrowError);

    render(<WrappedThrowError />);

    expect(screen.getByTestId('error-display')).toBeInTheDocument();
  });

  it('passes error boundary props', () => {
    const onError = vi.fn();
    const TestComponent: React.FC = () => {
      throw new Error('HOC test error');
    };

    const WrappedComponent = withErrorBoundary(TestComponent, { onError });

    render(<WrappedComponent />);

    expect(onError).toHaveBeenCalled();
  });

  it('sets correct displayName', () => {
    const TestComponent: React.FC = () => null;
    TestComponent.displayName = 'TestComponent';

    const WrappedComponent = withErrorBoundary(TestComponent);

    expect(WrappedComponent.displayName).toBe('withErrorBoundary(TestComponent)');
  });

  it('uses component name if displayName is not set', () => {
    function NamedComponent() {
      return null;
    }

    const WrappedComponent = withErrorBoundary(NamedComponent);

    expect(WrappedComponent.displayName).toBe('withErrorBoundary(NamedComponent)');
  });
});
