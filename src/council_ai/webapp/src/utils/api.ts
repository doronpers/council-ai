/**
 * API Utility Functions
 */
import type { AppConfig, ConsultationRequest, ConsultationResult, HistoryEntry } from '../types';

const API_BASE = '/api';

/**
 * Fetch wrapper with error handling
 */
async function fetchApi<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
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
    const response = await fetch(`${API_BASE}/consult/stream`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response;
}

/**
 * Load consultation history
 */
export async function loadHistory(limit: number = 10): Promise<HistoryEntry[]> {
    return fetchApi<HistoryEntry[]>(`/history?limit=${limit}`);
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
