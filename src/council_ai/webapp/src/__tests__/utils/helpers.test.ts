/**
 * Tests for utility helper functions
 */
import { describe, it, expect, vi } from 'vitest';
import {
  escapeHtml,
  formatTimestamp,
  truncate,
  debounce,
  parseSSELine,
  getModelsForProvider,
  getDefaultPersonasForDomain,
} from '../../utils/helpers';

describe('escapeHtml', () => {
  it('escapes HTML special characters', () => {
    expect(escapeHtml('<script>alert("xss")</script>')).toBe(
      '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'
    );
  });

  it('escapes ampersands', () => {
    expect(escapeHtml('a & b')).toBe('a &amp; b');
  });

  it('escapes single quotes', () => {
    expect(escapeHtml("it's")).toBe('it&#039;s');
  });

  it('returns empty string for null', () => {
    expect(escapeHtml(null)).toBe('');
  });

  it('returns empty string for undefined', () => {
    expect(escapeHtml(undefined)).toBe('');
  });

  it('passes through safe strings unchanged', () => {
    expect(escapeHtml('Hello World')).toBe('Hello World');
  });
});

describe('formatTimestamp', () => {
  it('formats an ISO timestamp to locale string', () => {
    const result = formatTimestamp('2024-01-15T10:30:00.000Z');
    // Result will vary by locale, just verify it returns a non-empty string
    expect(result).toBeTruthy();
    expect(typeof result).toBe('string');
  });
});

describe('truncate', () => {
  it('returns short text unchanged', () => {
    expect(truncate('hello', 10)).toBe('hello');
  });

  it('truncates long text with ellipsis', () => {
    expect(truncate('hello world, this is a long string', 10)).toBe('hello w...');
  });

  it('handles exact length', () => {
    expect(truncate('hello', 5)).toBe('hello');
  });
});

describe('debounce', () => {
  it('delays execution', async () => {
    vi.useFakeTimers();
    const fn = vi.fn();
    const debounced = debounce(fn, 100);

    debounced();
    expect(fn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(100);
    expect(fn).toHaveBeenCalledTimes(1);

    vi.useRealTimers();
  });

  it('resets timer on subsequent calls', () => {
    vi.useFakeTimers();
    const fn = vi.fn();
    const debounced = debounce(fn, 100);

    debounced();
    vi.advanceTimersByTime(50);
    debounced(); // Reset timer
    vi.advanceTimersByTime(50);
    expect(fn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(50);
    expect(fn).toHaveBeenCalledTimes(1);

    vi.useRealTimers();
  });
});

describe('parseSSELine', () => {
  it('parses valid SSE data line', () => {
    const result = parseSSELine('data: {"type":"progress","content":"hello"}');
    expect(result).toEqual({ type: 'progress', content: 'hello' });
  });

  it('returns null for non-data lines', () => {
    expect(parseSSELine('event: message')).toBeNull();
    expect(parseSSELine(': comment')).toBeNull();
    expect(parseSSELine('')).toBeNull();
  });

  it('returns null for invalid JSON', () => {
    expect(parseSSELine('data: {invalid}')).toBeNull();
  });
});

describe('getModelsForProvider', () => {
  const models = [
    { provider: 'anthropic', models: ['claude-3-sonnet', 'claude-3-opus'] },
    { provider: 'openai', models: ['gpt-4', 'gpt-3.5-turbo'] },
  ];

  it('returns models for known provider', () => {
    expect(getModelsForProvider(models, 'anthropic')).toEqual([
      'claude-3-sonnet',
      'claude-3-opus',
    ]);
  });

  it('returns empty array for unknown provider', () => {
    expect(getModelsForProvider(models, 'gemini')).toEqual([]);
  });
});

describe('getDefaultPersonasForDomain', () => {
  const domains = [
    { id: 'tech', default_personas: ['DR', 'MD'] },
    { id: 'business', default_personas: ['DK', 'PH'] },
  ];

  it('returns personas for known domain', () => {
    expect(getDefaultPersonasForDomain(domains, 'tech')).toEqual(['DR', 'MD']);
  });

  it('returns empty array for unknown domain', () => {
    expect(getDefaultPersonasForDomain(domains, 'creative')).toEqual([]);
  });
});
