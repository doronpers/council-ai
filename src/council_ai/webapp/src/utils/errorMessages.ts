/**
 * Comprehensive Error Message Catalog
 *
 * Centralized error messages with user-friendly text, recovery actions, and technical details.
 */

import { ErrorCategory, ErrorInfo } from './errors';

/**
 * Error message catalog organized by category
 */
export const ERROR_MESSAGES = {
  // Network Errors
  NETWORK_CONNECTION_FAILED: {
    category: ErrorCategory.NETWORK,
    userMessage: 'Unable to connect to the server.',
    technicalMessage: 'Network connection failed. Please check your internet connection.',
    suggestions: [
      'Check your internet connection',
      'Verify the server is running',
      'Try again in a few moments',
      "Check if you're behind a firewall or proxy",
    ],
    recoveryActions: [
      { label: 'Retry', action: 'retry' },
      { label: 'Check Diagnostics', action: 'diagnostics' },
    ],
    severity: 'high' as const,
    recoverable: true,
  },

  NETWORK_TIMEOUT: {
    category: ErrorCategory.NETWORK,
    userMessage: 'Request timed out. The server may be busy.',
    technicalMessage: 'The request exceeded the timeout limit.',
    suggestions: [
      'Try again in a few moments',
      'Consider using a shorter query',
      'Try during off-peak hours',
      'Check your network connection speed',
    ],
    recoveryActions: [
      { label: 'Retry', action: 'retry' },
      { label: 'Shorten Query', action: 'shorten-query' },
    ],
    severity: 'medium' as const,
    recoverable: true,
  },

  // Validation Errors
  QUERY_EMPTY: {
    category: ErrorCategory.VALIDATION,
    userMessage: 'Query cannot be empty.',
    technicalMessage: 'The consultation query must contain at least one character.',
    suggestions: [
      'Enter a question or topic for the council to discuss',
      'Use the example queries as a starting point',
    ],
    recoveryActions: [{ label: 'Focus Query Input', action: 'focus-query' }],
    severity: 'low' as const,
    recoverable: true,
  },

  QUERY_TOO_LONG: {
    category: ErrorCategory.VALIDATION,
    userMessage: 'Query is too long.',
    technicalMessage: `Query exceeds maximum length of 50,000 characters.`,
    suggestions: [
      'Shorten your query',
      'Move some content to the context field',
      'Break into multiple consultations',
    ],
    recoveryActions: [{ label: 'Focus Query Input', action: 'focus-query' }],
    severity: 'low' as const,
    recoverable: true,
  },

  API_KEY_INVALID: {
    category: ErrorCategory.CONFIGURATION,
    userMessage: 'API key is invalid or expired.',
    technicalMessage: 'The provided API key failed validation or has expired.',
    suggestions: [
      'Verify your API key is correct',
      'Check if your API key has expired',
      'Ensure you have sufficient credits/quota',
      'Try a different API key',
      "Check your provider's dashboard for key status",
    ],
    recoveryActions: [
      { label: 'Open Settings', action: 'open-settings' },
      { label: 'Check Diagnostics', action: 'diagnostics' },
    ],
    severity: 'high' as const,
    recoverable: true,
  },

  API_KEY_MISSING: {
    category: ErrorCategory.CONFIGURATION,
    userMessage: 'API key is required.',
    technicalMessage: 'No API key provided in settings or environment variables.',
    suggestions: [
      'Set an API key in Advanced Settings',
      'Check your environment variables',
      'Verify your .env file contains the correct key',
      'For local LLMs (LM Studio), set the base URL instead',
    ],
    recoveryActions: [{ label: 'Open Settings', action: 'open-settings' }],
    severity: 'high' as const,
    recoverable: true,
  },

  BASE_URL_INVALID: {
    category: ErrorCategory.VALIDATION,
    userMessage: 'Base URL format is invalid.',
    technicalMessage: 'The base URL must be a valid HTTP/HTTPS URL.',
    suggestions: [
      'Ensure the URL starts with http:// or https://',
      'Check for typos in the URL',
      'Verify the URL includes the port if needed (e.g., :1234)',
      'For LM Studio, use: http://localhost:1234/v1',
    ],
    recoveryActions: [{ label: 'Focus Base URL Input', action: 'focus-base-url' }],
    severity: 'medium' as const,
    recoverable: true,
  },

  BASE_URL_UNREACHABLE: {
    category: ErrorCategory.NETWORK,
    userMessage: 'Cannot reach the specified base URL.',
    technicalMessage: 'The server at the base URL is not responding.',
    suggestions: [
      'Verify the server is running',
      'Check the URL is correct',
      'Ensure the server is accessible from your network',
      'For local servers, check if localhost is correct',
    ],
    recoveryActions: [
      { label: 'Retry', action: 'retry' },
      { label: 'Check Diagnostics', action: 'diagnostics' },
    ],
    severity: 'high' as const,
    recoverable: true,
  },

  // Rate Limiting
  RATE_LIMIT_EXCEEDED: {
    category: ErrorCategory.RATE_LIMIT,
    userMessage: 'Too many requests. Please wait before trying again.',
    technicalMessage: 'Rate limit exceeded. Please wait before making more requests.',
    suggestions: [
      'Wait a few minutes before retrying',
      'Consider upgrading your API plan',
      'Space out your requests',
      'Use a different provider if available',
    ],
    recoveryActions: [{ label: 'Wait and Retry', action: 'retry-with-delay' }],
    severity: 'medium' as const,
    recoverable: true,
  },

  // Quota Errors
  QUOTA_EXCEEDED: {
    category: ErrorCategory.QUOTA,
    userMessage: 'API quota has been exceeded.',
    technicalMessage: 'Your API provider quota limit has been reached.',
    suggestions: [
      'Check your API provider dashboard',
      'Upgrade your plan or add credits',
      'Wait for quota reset',
      'Switch to a different provider',
      'Use a local LLM (LM Studio) for unlimited usage',
    ],
    recoveryActions: [{ label: 'Open Settings', action: 'open-settings' }],
    severity: 'high' as const,
    recoverable: true,
  },

  // API Errors
  PROVIDER_ERROR: {
    category: ErrorCategory.API,
    userMessage: 'The AI provider encountered an error.',
    technicalMessage: 'The LLM provider returned an error response.',
    suggestions: [
      'Try again in a few moments',
      'Switch to a different provider',
      'Check provider status page',
      'Verify your API key is valid',
    ],
    recoveryActions: [
      { label: 'Retry', action: 'retry' },
      { label: 'Switch Provider', action: 'switch-provider' },
    ],
    severity: 'medium' as const,
    recoverable: true,
  },

  // Permission Errors
  INSUFFICIENT_PERMISSIONS: {
    category: ErrorCategory.PERMISSION,
    userMessage: 'You do not have permission to perform this action.',
    technicalMessage: 'The API key lacks required permissions.',
    suggestions: [
      'Check your API key permissions',
      'Ensure your account has the required access',
      'Contact your administrator',
      'Try a different API key',
    ],
    recoveryActions: [{ label: 'Open Settings', action: 'open-settings' }],
    severity: 'high' as const,
    recoverable: false,
  },
};

/**
 * Get error message by code
 */
export function getErrorMessage(
  code: string
): (typeof ERROR_MESSAGES)[keyof typeof ERROR_MESSAGES] | null {
  const key = code.toUpperCase().replace(/-/g, '_') as keyof typeof ERROR_MESSAGES;
  return ERROR_MESSAGES[key] || null;
}

/**
 * Create ErrorInfo from error message catalog entry
 */
export function createErrorInfoFromCatalog(code: string, technicalDetails?: string): ErrorInfo {
  const message = getErrorMessage(code);
  if (!message) {
    return {
      category: ErrorCategory.UNKNOWN,
      message: technicalDetails || code,
      userMessage: 'An unexpected error occurred.',
      suggestions: ['Try again', 'Refresh the page', 'Contact support'],
      recoverable: true,
      severity: 'medium',
      code,
    };
  }

  return {
    category: message.category,
    message: technicalDetails || message.technicalMessage,
    userMessage: message.userMessage,
    suggestions: message.suggestions,
    actions: message.recoveryActions.map((action) => ({
      label: action.label,
      action: () => {
        // Action handlers will be implemented in components
        console.log(`Action: ${action.action}`);
      },
    })),
    recoverable: message.recoverable,
    severity: message.severity,
    code,
    details: technicalDetails,
  };
}

/**
 * Get validation error message
 */
export function getValidationError(field: string, value: string): string | null {
  switch (field) {
    case 'query':
      if (!value.trim()) {
        return ERROR_MESSAGES.QUERY_EMPTY.userMessage;
      }
      if (value.length > 50000) {
        return ERROR_MESSAGES.QUERY_TOO_LONG.userMessage;
      }
      break;
    case 'apiKey':
      if (!value.trim()) {
        return ERROR_MESSAGES.API_KEY_MISSING.userMessage;
      }
      if (['your-api-key-here', 'placeholder', 'xxx'].includes(value.toLowerCase())) {
        return 'Please enter your actual API key';
      }
      break;
    case 'baseUrl':
      if (value.trim() && !isValidUrl(value)) {
        return ERROR_MESSAGES.BASE_URL_INVALID.userMessage;
      }
      break;
  }
  return null;
}

/**
 * Validate URL format
 */
function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}
