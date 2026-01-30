/**
 * API Utility Functions
 */
import type { AppConfig, ConsultationRequest, ConsultationResult, HistoryEntry } from '../types';
import { classifyError, ErrorInfo } from './errors';

const API_BASE = '/api';

/**
 * Custom error class for API errors with classification
 */
export class ApiError extends Error {
  public readonly info: ErrorInfo;

  constructor(info: ErrorInfo) {
    super(info.message);
    this.name = 'ApiError';
    this.info = info;
  }
}

/**
 * Fetch wrapper with enhanced error handling and classification
 */
async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorData: Record<string, unknown> = {};

      try {
        const responseText = await response.text();

        // Try to parse as JSON first
        try {
          errorData = JSON.parse(responseText) as Record<string, unknown>;

          const raw = errorData.error;
          if (raw && typeof raw === 'object' && raw !== null) {
            const s = raw as Record<string, unknown>;
            const errorInfo: ErrorInfo = {
              category: (s.category as string) || 'unknown',
              message: String(s.message ?? s.detail ?? `HTTP ${response.status}`),
              userMessage: String(s.message ?? 'An error occurred.'),
              suggestions: (Array.isArray(s.suggestions) ? s.suggestions : []) as string[],
              actions: s.actions as ErrorInfo['actions'],
              recoverable: s.recoverable !== false,
              severity: (s.severity as ErrorInfo['severity']) || 'medium',
              code: s.code as string | undefined,
              details: s.details,
            };
            throw new ApiError(errorInfo);
          }
        } catch (parseError) {
          if (parseError instanceof ApiError) throw parseError;
          // Not valid JSON or not a structured error, use as plain text
          errorData = { detail: responseText || 'Request failed' };
        }
      } catch (textError) {
        // Couldn't read response text
        errorData = { detail: 'Request failed', status: response.status };
      }

      // Classify the error based on HTTP status and error data
      const errorInfo = classifyError(errorData, response.status);

      // Throw a structured ApiError
      throw new ApiError(errorInfo);
    }

    return response.json();
  } catch (error) {
    // If it's already an ApiError, re-throw it
    if (error instanceof ApiError) {
      throw error;
    }

    // If it's a network error or other fetch error, classify it
    if (error instanceof TypeError && error.message.includes('fetch')) {
      const errorInfo = classifyError({
        detail: 'Network connection failed',
        message: error.message,
      });
      throw new ApiError(errorInfo);
    }

    // For other unexpected errors, create a generic classified error
    const errorInfo = classifyError({
      detail: error instanceof Error ? error.message : 'Unknown error occurred',
    });
    throw new ApiError(errorInfo);
  }
}

/**
 * Load application info (providers, models, personas, etc.)
 */
export async function loadAppInfo(): Promise<AppConfig> {
  return fetchApi<AppConfig>('/info');
}

/**
 * Submit a consultation (non-streaming)
 */
export async function submitConsultation(
  request: ConsultationRequest
): Promise<ConsultationResult> {
  return fetchApi<ConsultationResult>('/consult', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * Submit a streaming consultation
 * Returns a ReadableStream for SSE processing
 */
export async function submitStreamingConsultation(
  request: ConsultationRequest,
  signal?: AbortSignal
): Promise<Response> {
  try {
    const response = await fetch(`${API_BASE}/consult/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
      signal,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        detail: 'Request failed',
        status: response.status,
      }));

      // Classify the error based on HTTP status and error data
      const errorInfo = classifyError(errorData, response.status);

      // Throw a structured ApiError
      throw new ApiError(errorInfo);
    }

    return response;
  } catch (error) {
    // If it's already an ApiError, re-throw it
    if (error instanceof ApiError) {
      throw error;
    }

    // If it's a network error or other fetch error, classify it
    if (error instanceof TypeError && error.message.includes('fetch')) {
      const errorInfo = classifyError({
        detail: 'Network connection failed during streaming',
        message: error.message,
      });
      throw new ApiError(errorInfo);
    }

    // For AbortError (user cancelled), create appropriate error
    if (error instanceof DOMException && error.name === 'AbortError') {
      const errorInfo = classifyError({
        detail: 'Request was cancelled',
        code: 'USER_CANCELLED',
      });
      throw new ApiError(errorInfo);
    }

    // For other unexpected errors, create a generic classified error
    const errorInfo = classifyError({
      detail: error instanceof Error ? error.message : 'Unknown streaming error occurred',
    });
    throw new ApiError(errorInfo);
  }
}

/**
 * Load consultation history
 */
export async function loadHistory(
  limit: number = 10,
  filters?: {
    dateFrom?: string;
    dateTo?: string;
    domain?: string;
    mode?: string;
  }
): Promise<HistoryEntry[]> {
  const params = new URLSearchParams({ limit: limit.toString() });
  if (filters) {
    if (filters.dateFrom) params.append('date_from', filters.dateFrom);
    if (filters.dateTo) params.append('date_to', filters.dateTo);
    if (filters.domain) params.append('domain', filters.domain);
    if (filters.mode) params.append('mode', filters.mode);
  }
  const response = await fetchApi<{ consultations: HistoryEntry[]; total: number }>(
    `/history?${params.toString()}`
  );
  return response.consultations;
}

/**
 * Search consultation history
 */
export async function loadHistorySearch(query: string, limit?: number): Promise<HistoryEntry[]> {
  const params = new URLSearchParams({ q: query });
  if (limit) params.set('limit', limit.toString());
  const response = await fetchApi<{ consultations: HistoryEntry[]; query: string; count: number }>(
    `/history/search?${params}`
  );
  return response.consultations;
}

/**
 * Delete a history entry
 */
export async function deleteHistoryEntry(id: string): Promise<void> {
  await fetchApi<void>(`/history/${id}`, { method: 'DELETE' });
}

/**
 * Get a specific consultation by ID
 */
export async function getConsultation(id: string): Promise<ConsultationResult> {
  return fetchApi<ConsultationResult>(`/history/${id}`);
}

/**
 * Update tags and notes for a consultation
 */
export async function updateConsultationMetadata(
  id: string,
  tags?: string[],
  notes?: string
): Promise<{ status: string; id: string }> {
  return fetchApi<{ status: string; id: string }>(`/history/${id}/save`, {
    method: 'POST',
    body: JSON.stringify({ tags, notes }),
  });
}

/**
 * Load TTS voices
 */
export async function loadTTSVoices(): Promise<
  Array<{ id: string; name: string; provider: string }>
> {
  return fetchApi('/tts/voices');
}

/**
 * Generate TTS audio
 */
export async function generateTTSAudio(
  text: string,
  voice?: string
): Promise<{ audio_url: string }> {
  return fetchApi('/tts/generate', {
    method: 'POST',
    body: JSON.stringify({ text, voice }),
  });
}

/**
 * Run diagnostics
 */
export async function runDiagnostics(): Promise<{
  python_version: string;
  council_version: string;
  providers: Record<string, boolean>;
  tts: Record<string, boolean>;
}> {
  return fetchApi('/diagnostics');
}
