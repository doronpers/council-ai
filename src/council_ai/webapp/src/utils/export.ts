/**
 * Export utility functions
 */
import type { ConsultationResult } from '../types';

export const exportToMarkdown = (result: ConsultationResult): string => {
  const lines: string[] = [];
  lines.push('# Council AI Consultation');
  lines.push('');
  lines.push(`**Query:** ${result.query}`);
  if (result.context) {
    lines.push(`**Context:** ${result.context}`);
  }
  lines.push(`**Mode:** ${result.mode}`);
  lines.push(`**Timestamp:** ${result.timestamp}`);
  lines.push('');
  if (result.synthesis) {
    lines.push('## Synthesis');
    lines.push('');
    lines.push(result.synthesis);
    lines.push('');
  }
  lines.push('## Individual Responses');
  lines.push('');
  result.responses.forEach((response) => {
    lines.push(`### ${response.persona_name} (${response.persona_title})`);
    lines.push('');
    lines.push(response.content);
    lines.push('');
    if (response.provider || response.model) {
      lines.push(`**Model:** ${[response.provider, response.model].filter(Boolean).join('/')}`);
    }
    if (response.usage?.total_tokens !== undefined) {
      lines.push(`**Tokens:** ${response.usage.total_tokens}`);
    }
    lines.push('');
    lines.push('---');
    lines.push('');
  });
  if (result.analysis) {
    lines.push('## Analysis');
    lines.push('');
    lines.push(`**Consensus Score:** ${result.analysis.consensus_score}`);
    lines.push('');
    if (result.analysis.key_agreements.length > 0) {
      lines.push('**Key Agreements:**');
      result.analysis.key_agreements.forEach((item) => lines.push(`- ${item}`));
      lines.push('');
    }
    if (result.analysis.key_tensions.length > 0) {
      lines.push('**Key Tensions:**');
      result.analysis.key_tensions.forEach((item) => lines.push(`- ${item}`));
      lines.push('');
    }
    if (result.analysis.recommendations.length > 0) {
      lines.push('**Recommendations:**');
      result.analysis.recommendations.forEach((item) => lines.push(`- ${item}`));
      lines.push('');
    }
  }
  return lines.join('\n');
};

export const exportToJson = (result: ConsultationResult): string => {
  return JSON.stringify(result, null, 2);
};

export const downloadFile = (content: string, filename: string, mimeType: string) => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
};
