/**
 * Reviewer API utilities
 */
import type {
  ReviewerInfoResponse,
  ReviewerRequest,
  ReviewerStreamEvent,
  GoogleDocsImportRequest,
  GoogleDocsImportResponse,
} from '../types/reviewer';

const REVIEWER_BASE = '/api/reviewer';

export const loadReviewerInfo = async (): Promise<ReviewerInfoResponse> => {
  const response = await fetch(`${REVIEWER_BASE}/info`);
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Failed to load reviewer info' }));
    throw new Error(err.detail || 'Failed to load reviewer info');
  }
  return response.json();
};

export const importGoogleDocs = async (
  request: GoogleDocsImportRequest
): Promise<GoogleDocsImportResponse> => {
  const response = await fetch(`${REVIEWER_BASE}/import/googledocs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.message || data.detail || 'Import failed');
  }
  return data as GoogleDocsImportResponse;
};

export const streamReview = async (
  request: ReviewerRequest,
  onEvent: (event: ReviewerStreamEvent) => void,
  signal?: AbortSignal
): Promise<void> => {
  const response = await fetch(`${REVIEWER_BASE}/review/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    signal,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Review failed' }));
    throw new Error(err.detail || 'Review failed');
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('Failed to start streaming response');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      try {
        const data = JSON.parse(line.slice(6)) as ReviewerStreamEvent;
        onEvent(data);
      } catch (err) {
        // ignore malformed lines
        continue;
      }
    }
  }
};
