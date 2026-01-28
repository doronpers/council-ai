/**
 * Error Logger - Client-side error logging with context and sanitization
 */

interface ErrorContext {
  timestamp: string;
  userAgent: string;
  url: string;
  action?: string;
  component?: string;
  errorType: string;
  errorMessage: string;
  stack?: string;
  additionalData?: Record<string, unknown>;
}

/**
 * Sanitize data to remove sensitive information
 */
function sanitizeData(data: unknown): unknown {
  if (typeof data !== 'object' || data === null) {
    return data;
  }

  if (Array.isArray(data)) {
    return data.map(sanitizeData);
  }

  const sanitized: Record<string, unknown> = {};
  const sensitiveKeys = [
    'api_key',
    'apiKey',
    'api-key',
    'password',
    'token',
    'secret',
    'authorization',
    'auth',
    'credential',
    'private',
  ];

  const obj = data as Record<string, unknown>;
  for (const [key, value] of Object.entries(obj)) {
    const lowerKey = key.toLowerCase();
    const isSensitive = sensitiveKeys.some((sensitive) => lowerKey.includes(sensitive));

    if (isSensitive) {
      sanitized[key] = '[REDACTED]';
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizeData(value);
    } else {
      sanitized[key] = value;
    }
  }

  return sanitized;
}

/**
 * Log error with full context
 */
export function logError(
  error: Error | unknown,
  context?: {
    action?: string;
    component?: string;
    additionalData?: Record<string, unknown>;
  }
): void {
  const errorContext: ErrorContext = {
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    url: window.location.href,
    action: context?.action,
    component: context?.component,
    errorType: error instanceof Error ? error.constructor.name : typeof error,
    errorMessage: error instanceof Error ? error.message : String(error),
    stack: error instanceof Error ? error.stack : undefined,
    additionalData: context?.additionalData
      ? (sanitizeData(context.additionalData) as Record<string, unknown>)
      : undefined,
  };

  // Log to console; avoid leaking raw error (stack/serialized state) in production-style logging
  const safeError =
    error instanceof Error
      ? { name: error.name, message: error.message }
      : typeof error === 'object' && error !== null
        ? '[Object]'
        : String(error);
  console.error('Error logged:', { ...errorContext, originalError: safeError });

  // In production, you could send this to an error tracking service
  // Example: sendToErrorTrackingService(sanitizeData(errorContext));

  // Store in localStorage for debugging (limited to last 10 errors)
  try {
    const errorLogKey = 'council-ai-error-log';
    const existingLogs = JSON.parse(localStorage.getItem(errorLogKey) || '[]');
    const newLogs = [errorContext, ...existingLogs].slice(0, 10);
    localStorage.setItem(errorLogKey, JSON.stringify(newLogs));
  } catch (e) {
    // If localStorage fails, just log to console
    console.warn('Failed to store error log:', e);
  }
}

/**
 * Log user action for error context
 */
export function logUserAction(action: string, details?: Record<string, unknown>): void {
  try {
    const actionLogKey = 'council-ai-action-log';
    const existingActions = JSON.parse(localStorage.getItem(actionLogKey) || '[]');
    const actionEntry = {
      timestamp: new Date().toISOString(),
      action,
      details: details ? sanitizeData(details) : undefined,
    };
    const newActions = [actionEntry, ...existingActions].slice(0, 20); // Keep last 20 actions
    localStorage.setItem(actionLogKey, JSON.stringify(newActions));
  } catch (e) {
    // Silently fail - action logging is not critical
  }
}

/**
 * Get recent error logs (for debugging)
 */
export function getRecentErrors(limit: number = 5): ErrorContext[] {
  try {
    const errorLogKey = 'council-ai-error-log';
    const logs = JSON.parse(localStorage.getItem(errorLogKey) || '[]');
    return logs.slice(0, limit);
  } catch {
    return [];
  }
}

/**
 * Clear error logs
 */
export function clearErrorLogs(): void {
  try {
    localStorage.removeItem('council-ai-error-log');
    localStorage.removeItem('council-ai-action-log');
  } catch {
    // Silently fail
  }
}
