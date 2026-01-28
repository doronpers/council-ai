/**
 * Error classification and handling system for Council AI web app
 */

// Error categories for different types of failures
export enum ErrorCategory {
  NETWORK = 'network',
  VALIDATION = 'validation',
  API = 'api',
  CONFIGURATION = 'configuration',
  PERMISSION = 'permission',
  RATE_LIMIT = 'rate_limit',
  QUOTA = 'quota',
  UNKNOWN = 'unknown',
}

// Structured error information with recovery guidance
export interface ErrorInfo {
  category: ErrorCategory;
  message: string;
  userMessage: string;
  suggestions: string[];
  actions?: Array<{ label: string; action: () => void }>;
  recoverable: boolean;
  severity: 'low' | 'medium' | 'high' | 'critical';
  code?: string;
  details?: unknown;
}

// HTTP status code to error category mapping
const HTTP_STATUS_TO_CATEGORY: Record<number, ErrorCategory> = {
  400: ErrorCategory.VALIDATION,
  401: ErrorCategory.PERMISSION,
  403: ErrorCategory.PERMISSION,
  404: ErrorCategory.VALIDATION,
  408: ErrorCategory.NETWORK,
  409: ErrorCategory.VALIDATION,
  422: ErrorCategory.VALIDATION,
  429: ErrorCategory.RATE_LIMIT,
  500: ErrorCategory.API,
  502: ErrorCategory.NETWORK,
  503: ErrorCategory.API,
  504: ErrorCategory.NETWORK,
};

// Known error codes and their mappings
const ERROR_CODE_MAPPINGS: Record<string, Partial<ErrorInfo>> = {
  // API key errors
  API_KEY_MISSING: {
    category: ErrorCategory.CONFIGURATION,
    userMessage: 'API key is required to consult the council.',
    suggestions: [
      'Set an API key in Advanced Settings',
      'Check your environment variables',
      'Verify your .env file contains the correct key',
    ],
    actions: [{ label: 'Open Settings', action: () => (window.location.hash = '#config-section') }],
    recoverable: true,
    severity: 'high',
  },
  API_KEY_INVALID: {
    category: ErrorCategory.CONFIGURATION,
    userMessage: 'The API key appears to be invalid or expired.',
    suggestions: [
      'Verify your API key is correct',
      'Check if your API key has expired',
      'Ensure you have sufficient credits/quota',
      'Try a different API key',
    ],
    recoverable: true,
    severity: 'high',
  },
  API_KEY_PLACEHOLDER: {
    category: ErrorCategory.CONFIGURATION,
    userMessage: 'Please replace the placeholder API key with your actual key.',
    suggestions: [
      'Get a real API key from your provider',
      'Update the API key in Advanced Settings',
      'Remove example values from your .env file',
    ],
    actions: [{ label: 'Open Settings', action: () => (window.location.hash = '#config-section') }],
    recoverable: true,
    severity: 'high',
  },

  // Network errors
  NETWORK_ERROR: {
    category: ErrorCategory.NETWORK,
    userMessage: 'Unable to connect to the server. Please check your internet connection.',
    suggestions: [
      'Check your internet connection',
      'Try again in a few moments',
      'Contact support if the problem persists',
    ],
    recoverable: true,
    severity: 'medium',
  },
  TIMEOUT_ERROR: {
    category: ErrorCategory.NETWORK,
    userMessage: 'The request timed out. The server may be overloaded.',
    suggestions: [
      'Try again in a few moments',
      'Consider using a shorter query',
      'Try during off-peak hours',
    ],
    recoverable: true,
    severity: 'medium',
  },

  // Validation errors
  INVALID_QUERY: {
    category: ErrorCategory.VALIDATION,
    userMessage: 'The query is invalid or too long.',
    suggestions: [
      'Ensure your query is not empty',
      'Keep queries under 50,000 characters',
      'Remove any special characters that might cause issues',
    ],
    recoverable: true,
    severity: 'low',
  },
  INVALID_DOMAIN: {
    category: ErrorCategory.VALIDATION,
    userMessage: 'The selected domain is not valid.',
    suggestions: [
      'Choose a different domain',
      'Verify the domain name is spelled correctly',
      'Check if the domain is available',
    ],
    recoverable: true,
    severity: 'low',
  },

  // Rate limiting
  RATE_LIMIT_EXCEEDED: {
    category: ErrorCategory.RATE_LIMIT,
    userMessage: 'Too many requests. Please wait before trying again.',
    suggestions: [
      'Wait a few minutes before retrying',
      'Consider upgrading your API plan',
      'Space out your requests',
    ],
    recoverable: true,
    severity: 'medium',
  },

  // Quota errors
  QUOTA_EXCEEDED: {
    category: ErrorCategory.QUOTA,
    userMessage: 'Your API quota has been exceeded.',
    suggestions: [
      'Check your API provider dashboard',
      'Upgrade your plan or add credits',
      'Wait for quota reset',
      'Switch to a different provider',
    ],
    recoverable: true,
    severity: 'high',
  },

  // Generic API errors
  PROVIDER_ERROR: {
    category: ErrorCategory.API,
    userMessage: 'The AI provider encountered an error.',
    suggestions: [
      'Try again in a few moments',
      'Switch to a different provider',
      'Check provider status page',
    ],
    recoverable: true,
    severity: 'medium',
  },

  // Permission errors
  INSUFFICIENT_PERMISSIONS: {
    category: ErrorCategory.PERMISSION,
    userMessage: 'You do not have permission to perform this action.',
    suggestions: [
      'Check your API key permissions',
      'Ensure your account has the required access',
      'Contact your administrator',
    ],
    recoverable: false,
    severity: 'high',
  },
};

/**
 * Classify an error based on HTTP status, error code, or error message
 */
export function classifyError(error: unknown, httpStatus?: number): ErrorInfo {
  const err = error as Record<string, unknown>;
  // Check for known error codes first
  if (err?.code && typeof err.code === 'string' && ERROR_CODE_MAPPINGS[err.code]) {
    return {
      ...ERROR_CODE_MAPPINGS[err.code],
      message: String(err.detail ?? err.message ?? err.code),
      code: err.code,
      details: err,
    } as ErrorInfo;
  }

  // Check HTTP status
  if (httpStatus && HTTP_STATUS_TO_CATEGORY[httpStatus]) {
    const category = HTTP_STATUS_TO_CATEGORY[httpStatus];
    const baseInfo = getBaseErrorInfo(category);
    return {
      ...baseInfo,
      category,
      message: String(err?.detail ?? err?.message ?? `HTTP ${httpStatus}`),
      details: err,
    } as ErrorInfo;
  }

  // Check error message patterns
  const message = String(err?.message ?? err?.detail ?? error);
  const lowerMessage = message.toLowerCase();

  // Network-related errors
  if (
    lowerMessage.includes('network') ||
    lowerMessage.includes('connection') ||
    lowerMessage.includes('fetch')
  ) {
    return {
      category: ErrorCategory.NETWORK,
      message,
      userMessage: 'Network connection issue. Please check your internet connection.',
      suggestions: [
        'Check your internet connection',
        'Try again in a few moments',
        'Try refreshing the page',
      ],
      recoverable: true,
      severity: 'medium',
      details: err,
    };
  }

  // Timeout errors
  if (lowerMessage.includes('timeout') || lowerMessage.includes('timed out')) {
    return {
      category: ErrorCategory.NETWORK,
      message,
      userMessage: 'Request timed out. The server may be busy.',
      suggestions: [
        'Try again in a few moments',
        'Consider using a shorter query',
        'Try during off-peak hours',
      ],
      recoverable: true,
      severity: 'medium',
      details: err,
    };
  }

  // API key related
  if (
    lowerMessage.includes('api key') ||
    lowerMessage.includes('authentication') ||
    lowerMessage.includes('unauthorized')
  ) {
    return {
      category: ErrorCategory.CONFIGURATION,
      message,
      userMessage: 'API key issue. Please check your configuration.',
      suggestions: [
        'Verify your API key in Advanced Settings',
        'Check your .env file',
        'Ensure your API key is valid and active',
      ],
      actions: [
        { label: 'Open Settings', action: () => (window.location.hash = '#config-section') },
      ],
      recoverable: true,
      severity: 'high',
      details: err,
    };
  }

  // Rate limiting
  if (lowerMessage.includes('rate limit') || lowerMessage.includes('too many requests')) {
    return {
      category: ErrorCategory.RATE_LIMIT,
      message,
      userMessage: 'Rate limit exceeded. Please wait before trying again.',
      suggestions: [
        'Wait a few minutes before retrying',
        'Consider upgrading your API plan',
        'Space out your requests',
      ],
      recoverable: true,
      severity: 'medium',
      details: err,
    };
  }

  // Default fallback
  return {
    category: ErrorCategory.UNKNOWN,
    message,
    userMessage: 'An unexpected error occurred.',
    suggestions: [
      'Try again in a few moments',
      'Refresh the page',
      'Contact support if the problem persists',
    ],
    recoverable: true,
    severity: 'medium',
    details: err,
  };
}

/**
 * Get base error info for a category
 */
function getBaseErrorInfo(category: ErrorCategory): Partial<ErrorInfo> {
  switch (category) {
    case ErrorCategory.NETWORK:
      return {
        userMessage: 'Network connection issue.',
        suggestions: [
          'Check your internet connection',
          'Try again in a few moments',
          'Try refreshing the page',
        ],
        recoverable: true,
        severity: 'medium',
      };

    case ErrorCategory.VALIDATION:
      return {
        userMessage: 'Invalid input or configuration.',
        suggestions: [
          'Check your input values',
          'Verify all required fields are filled',
          'Review error details for specific issues',
        ],
        recoverable: true,
        severity: 'low',
      };

    case ErrorCategory.PERMISSION:
      return {
        userMessage: 'Permission denied.',
        suggestions: [
          'Check your API key permissions',
          'Ensure your account has required access',
          'Contact your administrator',
        ],
        recoverable: false,
        severity: 'high',
      };

    case ErrorCategory.RATE_LIMIT:
      return {
        userMessage: 'Rate limit exceeded.',
        suggestions: [
          'Wait before making more requests',
          'Consider upgrading your plan',
          'Space out your requests',
        ],
        recoverable: true,
        severity: 'medium',
      };

    case ErrorCategory.API:
      return {
        userMessage: 'API service error.',
        suggestions: [
          'Try again in a few moments',
          'Check provider status',
          'Try a different provider',
        ],
        recoverable: true,
        severity: 'medium',
      };

    default:
      return {
        userMessage: 'An error occurred.',
        suggestions: ['Try again', 'Refresh the page', 'Contact support'],
        recoverable: true,
        severity: 'medium',
      };
  }
}

/**
 * Create a custom error with specific guidance
 */
export function createError(
  category: ErrorCategory,
  message: string,
  userMessage: string,
  suggestions: string[] = [],
  actions?: Array<{ label: string; action: () => void }>,
  severity: 'low' | 'medium' | 'high' | 'critical' = 'medium',
  recoverable: boolean = true
): ErrorInfo {
  return {
    category,
    message,
    userMessage,
    suggestions,
    actions,
    recoverable,
    severity,
  };
}

/**
 * Check if an error is recoverable
 */
export function isRecoverable(error: ErrorInfo): boolean {
  return error.recoverable;
}

/**
 * Get severity level for styling
 */
export function getSeverityLevel(error: ErrorInfo): 'low' | 'medium' | 'high' | 'critical' {
  return error.severity;
}

/**
 * Get icon for error category
 */
export function getErrorIcon(category: ErrorCategory): string {
  switch (category) {
    case ErrorCategory.NETWORK:
      return '🌐';
    case ErrorCategory.VALIDATION:
      return '⚠️';
    case ErrorCategory.API:
      return '🔧';
    case ErrorCategory.CONFIGURATION:
      return '⚙️';
    case ErrorCategory.PERMISSION:
      return '🔒';
    case ErrorCategory.RATE_LIMIT:
      return '⏱️';
    case ErrorCategory.QUOTA:
      return '💰';
    default:
      return '❓';
  }
}
