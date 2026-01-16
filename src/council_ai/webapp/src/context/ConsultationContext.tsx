/**
 * Consultation Context - Active consultation state
 */
import React, {
    createContext,
    useContext,
    useState,
    useCallback,
    ReactNode,
} from 'react';
import type {
    ConsultationResult,
    MemberStatusInfo,
    MemberStatus,
    StreamEvent,
} from '../types';

interface ConsultationContextType {
    // Consultation state
    isConsulting: boolean;
    setIsConsulting: React.Dispatch<React.SetStateAction<boolean>>;

    // Query state
    query: string;
    setQuery: React.Dispatch<React.SetStateAction<string>>;
    context: string;
    setContext: React.Dispatch<React.SetStateAction<string>>;

    // Results
    result: ConsultationResult | null;
    setResult: React.Dispatch<React.SetStateAction<ConsultationResult | null>>;

    // Streaming state
    streamingSynthesis: string;
    setStreamingSynthesis: React.Dispatch<React.SetStateAction<string>>;
    streamingResponses: Map<string, string>;
    updateStreamingResponse: (personaId: string, content: string) => void;
    clearStreamingState: () => void;

    // Member status tracking
    memberStatuses: MemberStatusInfo[];
    initializeMemberStatuses: (members: MemberStatusInfo[]) => void;
    updateMemberStatus: (personaId: string, status: MemberStatus) => void;

    // Abort controller for cancellation
    abortController: AbortController | null;
    setAbortController: React.Dispatch<React.SetStateAction<AbortController | null>>;

    // Cancel consultation
    cancelConsultation: () => void;

    // Handle stream event
    handleStreamEvent: (event: StreamEvent) => void;

    // Status message
    statusMessage: string;
    setStatusMessage: React.Dispatch<React.SetStateAction<string>>;
}

const ConsultationContext = createContext<ConsultationContextType | undefined>(undefined);

export const ConsultationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [isConsulting, setIsConsulting] = useState(false);
    const [query, setQuery] = useState('');
    const [context, setContext] = useState('');
    const [result, setResult] = useState<ConsultationResult | null>(null);
    const [streamingSynthesis, setStreamingSynthesis] = useState('');
    const [streamingResponses, setStreamingResponses] = useState<Map<string, string>>(new Map());
    const [memberStatuses, setMemberStatuses] = useState<MemberStatusInfo[]>([]);
    const [abortController, setAbortController] = useState<AbortController | null>(null);
    const [statusMessage, setStatusMessage] = useState('');

    const updateStreamingResponse = useCallback((personaId: string, content: string) => {
        setStreamingResponses((prev) => {
            const next = new Map(prev);
            next.set(personaId, (prev.get(personaId) || '') + content);
            return next;
        });
    }, []);

    const clearStreamingState = useCallback(() => {
        setStreamingSynthesis('');
        setStreamingResponses(new Map());
        setMemberStatuses([]);
        setStatusMessage('');
    }, []);

    const initializeMemberStatuses = useCallback((members: MemberStatusInfo[]) => {
        setMemberStatuses(members);
    }, []);

    const updateMemberStatus = useCallback((personaId: string, status: MemberStatus) => {
        setMemberStatuses((prev) =>
            prev.map((m) => (m.id === personaId ? { ...m, status } : m))
        );
    }, []);

    const cancelConsultation = useCallback(() => {
        if (abortController) {
            abortController.abort();
            setAbortController(null);
        }
        setIsConsulting(false);
        setStatusMessage('Consultation cancelled.');
    }, [abortController]);

    const handleStreamEvent = useCallback((event: StreamEvent) => {
        switch (event.type) {
            case 'progress':
                setStatusMessage(event.message || '');
                break;
            case 'response_start':
                if (event.persona_id) {
                    updateMemberStatus(event.persona_id, 'responding');
                }
                break;
            case 'response_chunk':
                if (event.persona_id && event.chunk) {
                    updateStreamingResponse(event.persona_id, event.chunk);
                }
                break;
            case 'response_complete':
                if (event.persona_id) {
                    updateMemberStatus(event.persona_id, 'completed');
                }
                break;
            case 'synthesis_start':
                setStatusMessage('Synthesizing responses...');
                break;
            case 'synthesis_chunk':
                if (event.chunk) {
                    setStreamingSynthesis((prev) => prev + event.chunk);
                }
                break;
            case 'synthesis_complete':
                setStatusMessage('Synthesis complete.');
                break;
            case 'complete':
                if (event.result) {
                    setResult(event.result);
                }
                setIsConsulting(false);
                setStatusMessage('Consultation complete.');
                break;
            case 'error':
                setStatusMessage(event.error || 'An error occurred.');
                setIsConsulting(false);
                break;
        }
    }, [updateMemberStatus, updateStreamingResponse]);

    const value: ConsultationContextType = {
        isConsulting,
        setIsConsulting,
        query,
        setQuery,
        context,
        setContext,
        result,
        setResult,
        streamingSynthesis,
        setStreamingSynthesis,
        streamingResponses,
        updateStreamingResponse,
        clearStreamingState,
        memberStatuses,
        initializeMemberStatuses,
        updateMemberStatus,
        abortController,
        setAbortController,
        cancelConsultation,
        handleStreamEvent,
        statusMessage,
        setStatusMessage,
    };

    return (
        <ConsultationContext.Provider value={value}>
            {children}
        </ConsultationContext.Provider>
    );
};

export const useConsultation = (): ConsultationContextType => {
    const context = useContext(ConsultationContext);
    if (context === undefined) {
        throw new Error('useConsultation must be used within a ConsultationProvider');
    }
    return context;
};
