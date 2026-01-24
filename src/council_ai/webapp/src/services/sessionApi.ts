/**
 * Session API Service
 */

export interface Session {
    id: string;
    title?: string;
    created: string;
    updated: string;
    active: boolean;
    consultation_count: number;
    tags?: string[];
    metadata?: Record<string, unknown>;
}

export interface SessionDetails extends Session {
    consultations: ConsultationSession[];
}

export interface ConsultationSession {
    index: number;
    query: string;
    context?: string;
    mode?: string;
    timestamp: string;
    responses?: PersonaResponse[];
    synthesis?: string;
    analysis?: {
        insights?: string;
        key_points?: string[];
        confidence_score?: number;
    };
    usage?: ConsultationUsage;
}

export interface PersonaResponse {
    persona_name: string;
    persona_emoji?: string;
    response: string;
    model_used?: string;
    response_time?: number;
    tokens_used?: {
        input_tokens?: number;
        output_tokens?: number;
    };
}

export interface ConsultationUsage {
    total_input_tokens?: number;
    total_output_tokens?: number;
    total_requests?: number;
}

const API_BASE = '/api';

/**
 * List all sessions with pagination
 */
export async function listSessions(offset = 0, limit = 10): Promise<{ sessions: Session[]; total: number }> {
    const response = await fetch(`${API_BASE}/sessions?offset=${offset}&limit=${limit}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch sessions: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Get a specific session with all its consultations
 */
export async function getSession(sessionId: string): Promise<SessionDetails> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch session ${sessionId}: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Export a session
 */
export async function exportSession(sessionId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/export`);
    if (!response.ok) {
        throw new Error(`Failed to export session ${sessionId}: ${response.statusText}`);
    }
    return response.blob();
}

/**
 * Delete a session
 */
export async function deleteSession(sessionId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE',
    });
    if (!response.ok) {
        throw new Error(`Failed to delete session ${sessionId}: ${response.statusText}`);
    }
}

/**
 * Load a previous session
 */
export async function loadSession(sessionId: string): Promise<SessionDetails> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/load`, {
        method: 'POST',
    });
    if (!response.ok) {
        throw new Error(`Failed to load session ${sessionId}: ${response.statusText}`);
    }
    return response.json();
}
