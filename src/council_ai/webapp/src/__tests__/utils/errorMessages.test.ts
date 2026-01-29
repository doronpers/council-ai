/**
 * Tests for error message catalog and helpers
 */
import { describe, it, expect } from 'vitest';
import {
  ERROR_MESSAGES,
  getErrorMessage,
  createErrorInfoFromCatalog,
  getValidationError,
} from '../../utils/errorMessages';
import { ErrorCategory } from '../../utils/errors';

describe('ERROR_MESSAGES', () => {
  it('has network error messages', () => {
    expect(ERROR_MESSAGES.NETWORK_CONNECTION_FAILED).toBeDefined();
    expect(ERROR_MESSAGES.NETWORK_CONNECTION_FAILED.category).toBe(ErrorCategory.NETWORK);
    expect(ERROR_MESSAGES.NETWORK_TIMEOUT).toBeDefined();
  });

  it('has validation error messages', () => {
    expect(ERROR_MESSAGES.QUERY_EMPTY).toBeDefined();
    expect(ERROR_MESSAGES.QUERY_EMPTY.category).toBe(ErrorCategory.VALIDATION);
    expect(ERROR_MESSAGES.QUERY_TOO_LONG).toBeDefined();
  });

  it('has configuration error messages', () => {
    expect(ERROR_MESSAGES.API_KEY_INVALID).toBeDefined();
    expect(ERROR_MESSAGES.API_KEY_MISSING).toBeDefined();
  });

  it('all messages have required fields', () => {
    for (const [key, msg] of Object.entries(ERROR_MESSAGES)) {
      expect(msg.category, `${key} missing category`).toBeDefined();
      expect(msg.userMessage, `${key} missing userMessage`).toBeTruthy();
      expect(msg.technicalMessage, `${key} missing technicalMessage`).toBeTruthy();
      expect(msg.suggestions, `${key} missing suggestions`).toBeInstanceOf(Array);
      expect(msg.recoveryActions, `${key} missing recoveryActions`).toBeInstanceOf(Array);
      expect(msg.severity, `${key} missing severity`).toBeDefined();
      expect(typeof msg.recoverable).toBe('boolean');
    }
  });
});

describe('getErrorMessage', () => {
  it('returns message for known code', () => {
    const msg = getErrorMessage('NETWORK_CONNECTION_FAILED');
    expect(msg).not.toBeNull();
    expect(msg!.category).toBe(ErrorCategory.NETWORK);
  });

  it('handles hyphenated codes', () => {
    const msg = getErrorMessage('network-connection-failed');
    expect(msg).not.toBeNull();
  });

  it('returns null for unknown code', () => {
    expect(getErrorMessage('NONEXISTENT_ERROR')).toBeNull();
  });
});

describe('createErrorInfoFromCatalog', () => {
  it('creates ErrorInfo from known code', () => {
    const info = createErrorInfoFromCatalog('NETWORK_TIMEOUT');
    expect(info.category).toBe(ErrorCategory.NETWORK);
    expect(info.userMessage).toBeTruthy();
    expect(info.suggestions.length).toBeGreaterThan(0);
    expect(info.code).toBe('NETWORK_TIMEOUT');
  });

  it('creates fallback ErrorInfo for unknown code', () => {
    const info = createErrorInfoFromCatalog('UNKNOWN_CODE', 'Some technical detail');
    expect(info.category).toBe(ErrorCategory.UNKNOWN);
    expect(info.message).toBe('Some technical detail');
    expect(info.recoverable).toBe(true);
    expect(info.code).toBe('UNKNOWN_CODE');
  });

  it('uses technical details when provided', () => {
    const info = createErrorInfoFromCatalog('NETWORK_TIMEOUT', 'Custom detail');
    expect(info.message).toBe('Custom detail');
  });
});

describe('getValidationError', () => {
  it('returns error for empty query', () => {
    expect(getValidationError('query', '')).toBe(ERROR_MESSAGES.QUERY_EMPTY.userMessage);
    expect(getValidationError('query', '   ')).toBe(ERROR_MESSAGES.QUERY_EMPTY.userMessage);
  });

  it('returns error for too-long query', () => {
    const longQuery = 'a'.repeat(50001);
    expect(getValidationError('query', longQuery)).toBe(ERROR_MESSAGES.QUERY_TOO_LONG.userMessage);
  });

  it('returns null for valid query', () => {
    expect(getValidationError('query', 'How should we design this?')).toBeNull();
  });

  it('returns error for empty API key', () => {
    expect(getValidationError('apiKey', '')).toBe(ERROR_MESSAGES.API_KEY_MISSING.userMessage);
  });

  it('returns error for placeholder API key', () => {
    expect(getValidationError('apiKey', 'your-api-key-here')).toBe(
      'Please enter your actual API key'
    );
    expect(getValidationError('apiKey', 'placeholder')).toBe(
      'Please enter your actual API key'
    );
  });

  it('returns null for valid API key', () => {
    expect(getValidationError('apiKey', 'sk-ant-valid-key-123')).toBeNull();
  });

  it('returns error for invalid base URL', () => {
    expect(getValidationError('baseUrl', 'not-a-url')).toBe(
      ERROR_MESSAGES.BASE_URL_INVALID.userMessage
    );
  });

  it('returns null for valid base URL', () => {
    expect(getValidationError('baseUrl', 'http://localhost:1234/v1')).toBeNull();
  });

  it('returns null for empty base URL (optional field)', () => {
    expect(getValidationError('baseUrl', '')).toBeNull();
  });

  it('returns null for unknown field', () => {
    expect(getValidationError('unknown', 'value')).toBeNull();
  });
});
