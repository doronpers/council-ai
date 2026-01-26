/**
 * Tests for validation utilities
 */
import { describe, it, expect } from 'vitest';
import {
  ValidationRules,
  validateField,
  validateFields,
} from '../../utils/validation';

describe('ValidationRules', () => {
  describe('query validation', () => {
    it('notEmpty: validates non-empty string', () => {
      expect(ValidationRules.query.notEmpty.validate('hello')).toBe(true);
      expect(ValidationRules.query.notEmpty.validate('  hello  ')).toBe(true);
    });

    it('notEmpty: rejects empty string', () => {
      expect(ValidationRules.query.notEmpty.validate('')).toBe(false);
      expect(ValidationRules.query.notEmpty.validate('   ')).toBe(false);
    });

    it('maxLength: validates string within limit', () => {
      const rule = ValidationRules.query.maxLength(10);
      expect(rule.validate('short')).toBe(true);
      expect(rule.validate('exactly 10')).toBe(true);
    });

    it('maxLength: rejects string exceeding limit', () => {
      const rule = ValidationRules.query.maxLength(10);
      expect(rule.validate('this is too long')).toBe(false);
    });

    it('minLength: validates string meeting minimum', () => {
      const rule = ValidationRules.query.minLength(5);
      expect(rule.validate('hello')).toBe(true);
      expect(rule.validate('hello world')).toBe(true);
    });

    it('minLength: rejects string below minimum', () => {
      const rule = ValidationRules.query.minLength(5);
      expect(rule.validate('hi')).toBe(false);
      expect(rule.validate('   ')).toBe(false);
    });
  });

  describe('apiKey validation', () => {
    it('notEmpty: validates non-empty API key', () => {
      expect(ValidationRules.apiKey.notEmpty.validate('sk-abc123')).toBe(true);
    });

    it('notEmpty: rejects empty API key', () => {
      expect(ValidationRules.apiKey.notEmpty.validate('')).toBe(false);
      expect(ValidationRules.apiKey.notEmpty.validate('   ')).toBe(false);
    });

    it('notPlaceholder: accepts real API keys', () => {
      expect(ValidationRules.apiKey.notPlaceholder.validate('sk-abc123')).toBe(true);
      expect(ValidationRules.apiKey.notPlaceholder.validate('real-api-key')).toBe(true);
    });

    it('notPlaceholder: rejects placeholder values', () => {
      expect(ValidationRules.apiKey.notPlaceholder.validate('your-api-key-here')).toBe(false);
      expect(ValidationRules.apiKey.notPlaceholder.validate('placeholder')).toBe(false);
      expect(ValidationRules.apiKey.notPlaceholder.validate('xxx')).toBe(false);
    });

    it('minLength: validates API key meeting minimum', () => {
      const rule = ValidationRules.apiKey.minLength(10);
      expect(rule.validate('sk-abc123xyz')).toBe(true);
    });

    it('minLength: rejects short API key', () => {
      const rule = ValidationRules.apiKey.minLength(10);
      expect(rule.validate('short')).toBe(false);
    });
  });

  describe('url validation', () => {
    it('valid: accepts valid URLs', () => {
      expect(ValidationRules.url.valid.validate('https://example.com')).toBe(true);
      expect(ValidationRules.url.valid.validate('http://localhost:8000')).toBe(true);
      expect(ValidationRules.url.valid.validate('https://api.example.com/v1')).toBe(true);
    });

    it('valid: accepts empty string (optional field)', () => {
      expect(ValidationRules.url.valid.validate('')).toBe(true);
      expect(ValidationRules.url.valid.validate('   ')).toBe(true);
    });

    it('valid: rejects invalid URLs', () => {
      expect(ValidationRules.url.valid.validate('not-a-url')).toBe(false);
      expect(ValidationRules.url.valid.validate('example.com')).toBe(false);
    });
  });

  describe('email validation', () => {
    it('valid: accepts valid emails', () => {
      expect(ValidationRules.email.valid.validate('test@example.com')).toBe(true);
      expect(ValidationRules.email.valid.validate('user.name@domain.org')).toBe(true);
    });

    it('valid: accepts empty string (optional field)', () => {
      expect(ValidationRules.email.valid.validate('')).toBe(true);
    });

    it('valid: rejects invalid emails', () => {
      expect(ValidationRules.email.valid.validate('not-an-email')).toBe(false);
      expect(ValidationRules.email.valid.validate('missing@domain')).toBe(false);
    });
  });

  describe('number validation', () => {
    it('valid: accepts valid numbers', () => {
      expect(ValidationRules.number.valid.validate('123')).toBe(true);
      expect(ValidationRules.number.valid.validate('0')).toBe(true);
      expect(ValidationRules.number.valid.validate('-5')).toBe(true);
      expect(ValidationRules.number.valid.validate('3.14')).toBe(true);
    });

    it('valid: rejects non-numeric strings', () => {
      expect(ValidationRules.number.valid.validate('abc')).toBe(false);
      expect(ValidationRules.number.valid.validate('')).toBe(false);
    });

    it('min: validates number meeting minimum', () => {
      const rule = ValidationRules.number.min(5);
      expect(rule.validate('5')).toBe(true);
      expect(rule.validate('10')).toBe(true);
    });

    it('min: rejects number below minimum', () => {
      const rule = ValidationRules.number.min(5);
      expect(rule.validate('3')).toBe(false);
    });

    it('max: validates number within maximum', () => {
      const rule = ValidationRules.number.max(10);
      expect(rule.validate('5')).toBe(true);
      expect(rule.validate('10')).toBe(true);
    });

    it('max: rejects number exceeding maximum', () => {
      const rule = ValidationRules.number.max(10);
      expect(rule.validate('15')).toBe(false);
    });
  });
});

describe('validateField', () => {
  it('returns null when all rules pass', () => {
    const rules = [
      ValidationRules.query.notEmpty,
      ValidationRules.query.minLength(3),
    ];
    expect(validateField('hello', rules)).toBeNull();
  });

  it('returns first error message when validation fails', () => {
    const rules = [
      ValidationRules.query.notEmpty,
      ValidationRules.query.minLength(10),
    ];
    expect(validateField('hi', rules)).toBe('Query must be at least 10 characters');
  });

  it('returns empty validation error first', () => {
    const rules = [
      ValidationRules.query.notEmpty,
      ValidationRules.query.minLength(3),
    ];
    expect(validateField('', rules)).toBe('Query cannot be empty');
  });
});

describe('validateFields', () => {
  it('returns empty object when all fields are valid', () => {
    const fields = {
      query: 'What is the meaning of life?',
      apiKey: 'sk-abc123xyz',
    };
    const rules = {
      query: [ValidationRules.query.notEmpty, ValidationRules.query.minLength(5)],
      apiKey: [ValidationRules.apiKey.notEmpty, ValidationRules.apiKey.minLength(10)],
    };
    expect(validateFields(fields, rules)).toEqual({});
  });

  it('returns errors for invalid fields', () => {
    const fields = {
      query: '',
      apiKey: 'short',
    };
    const rules = {
      query: [ValidationRules.query.notEmpty],
      apiKey: [ValidationRules.apiKey.minLength(10)],
    };
    const errors = validateFields(fields, rules);
    expect(errors.query).toBe('Query cannot be empty');
    expect(errors.apiKey).toBe('API key must be at least 10 characters');
  });

  it('skips fields without rules', () => {
    const fields = {
      query: 'hello',
      other: '',
    };
    const rules = {
      query: [ValidationRules.query.notEmpty],
    };
    expect(validateFields(fields, rules)).toEqual({});
  });
});
