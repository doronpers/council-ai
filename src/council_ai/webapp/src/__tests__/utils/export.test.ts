/**
 * Tests for export utility functions
 */
import { describe, it, expect } from 'vitest';
import { exportToMarkdown, exportToJson } from '../../utils/export';
import type { ConsultationResult } from '../../types';

const mockResult: ConsultationResult = {
  query: 'Should we use React or Vue?',
  context: 'Building a new web app',
  mode: 'synthesis',
  timestamp: '2024-01-15T10:00:00.000Z',
  synthesis: 'Both frameworks are viable. React has a larger ecosystem.',
  responses: [
    {
      persona_id: 'DR',
      persona_name: 'Dieter Rams',
      persona_title: 'Design Advisor',
      content: 'Focus on simplicity.',
      provider: 'anthropic',
      model: 'claude-3-sonnet',
      usage: { total_tokens: 150, input_tokens: 50, output_tokens: 100 },
    },
    {
      persona_id: 'DK',
      persona_name: 'Daniel Kahneman',
      persona_title: 'Decision Analyst',
      content: 'Consider cognitive biases in your evaluation.',
      provider: 'openai',
      model: 'gpt-4',
      usage: { total_tokens: 200, input_tokens: 80, output_tokens: 120 },
    },
  ],
  analysis: {
    consensus_score: 0.75,
    key_agreements: ['Both are production-ready'],
    key_tensions: ['Ecosystem size vs simplicity'],
    recommendations: ['Start with React for larger teams'],
  },
} as unknown as ConsultationResult;

describe('exportToMarkdown', () => {
  it('includes header with query', () => {
    const md = exportToMarkdown(mockResult);
    expect(md).toContain('# Council AI Consultation');
    expect(md).toContain('**Query:** Should we use React or Vue?');
  });

  it('includes context when present', () => {
    const md = exportToMarkdown(mockResult);
    expect(md).toContain('**Context:** Building a new web app');
  });

  it('includes synthesis section', () => {
    const md = exportToMarkdown(mockResult);
    expect(md).toContain('## Synthesis');
    expect(md).toContain('Both frameworks are viable');
  });

  it('includes individual responses', () => {
    const md = exportToMarkdown(mockResult);
    expect(md).toContain('### Dieter Rams (Design Advisor)');
    expect(md).toContain('Focus on simplicity.');
    expect(md).toContain('### Daniel Kahneman (Decision Analyst)');
  });

  it('includes model information', () => {
    const md = exportToMarkdown(mockResult);
    expect(md).toContain('**Model:** anthropic/claude-3-sonnet');
  });

  it('includes token counts', () => {
    const md = exportToMarkdown(mockResult);
    expect(md).toContain('**Tokens:** 150');
  });

  it('includes analysis section', () => {
    const md = exportToMarkdown(mockResult);
    expect(md).toContain('## Analysis');
    expect(md).toContain('**Consensus Score:** 0.75');
    expect(md).toContain('Both are production-ready');
    expect(md).toContain('Ecosystem size vs simplicity');
    expect(md).toContain('Start with React for larger teams');
  });

  it('omits context when not present', () => {
    const resultNoContext = { ...mockResult, context: undefined };
    const md = exportToMarkdown(resultNoContext as unknown as ConsultationResult);
    expect(md).not.toContain('**Context:**');
  });

  it('omits synthesis when not present', () => {
    const resultNoSynthesis = { ...mockResult, synthesis: undefined };
    const md = exportToMarkdown(resultNoSynthesis as unknown as ConsultationResult);
    expect(md).not.toContain('## Synthesis');
  });
});

describe('exportToJson', () => {
  it('returns valid JSON', () => {
    const json = exportToJson(mockResult);
    const parsed = JSON.parse(json);
    expect(parsed.query).toBe('Should we use React or Vue?');
  });

  it('is formatted with indentation', () => {
    const json = exportToJson(mockResult);
    expect(json).toContain('\n');
    expect(json).toContain('  ');
  });
});
