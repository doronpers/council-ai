/**
 * Helper Utility Functions
 */

/**
 * Escape HTML to prevent XSS
 */
export function escapeHtml(unsafe: string | null | undefined): string {
  if (unsafe == null) return '';
  return String(unsafe)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Format a timestamp for display
 */
export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleString();
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: unknown[]) => void>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Copy text to clipboard
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

/**
 * Parse SSE data line
 */
export function parseSSELine(line: string): unknown | null {
  if (!line.startsWith('data: ')) return null;
  try {
    return JSON.parse(line.slice(6));
  } catch {
    return null;
  }
}

/**
 * Get models for a specific provider
 */
export function getModelsForProvider(
  models: Array<{ provider: string; models: string[] }>,
  provider: string
): string[] {
  const providerModels = models.find((m) => m.provider === provider);
  return providerModels?.models || [];
}

/**
 * Get default personas for a domain
 */
export function getDefaultPersonasForDomain(
  domains: Array<{ id: string; default_personas: string[] }>,
  domainId: string
): string[] {
  const domain = domains.find((d) => d.id === domainId);
  return domain?.default_personas || [];
}
