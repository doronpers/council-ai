/**
 * SubmitButton Component - Submit and cancel buttons for consultation
 */
import React, { useCallback } from 'react';
import { useApp } from '../../context/AppContext';
import { useConsultation } from '../../context/ConsultationContext';
import { submitStreamingConsultation } from '../../utils/api';
import { parseSSELine, getDefaultPersonasForDomain } from '../../utils/helpers';
import type { ConsultationRequest, StreamEvent, MemberStatusInfo, MemberStatus } from '../../types';

const SubmitButton: React.FC = () => {
  const { personas, domains, settings, selectedMembers, apiKey, sessionId, autoRecall } = useApp();
  const {
    query,
    context,
    isConsulting,
    setIsConsulting,
    abortController,
    setAbortController,
    cancelConsultation,
    clearStreamingState,
    initializeMemberStatuses,
    handleStreamEvent,
    setStatusMessage,
  } = useConsultation();

  const handleSubmit = useCallback(async () => {
    if (!query.trim()) {
      setStatusMessage('Please enter a query.');
      return;
    }

    // Get effective members
    const effectiveMembers =
      selectedMembers.length > 0
        ? selectedMembers
        : getDefaultPersonasForDomain(domains, settings.domain || 'general');

    // Initialize member statuses
    const memberStatuses = effectiveMembers.reduce<MemberStatusInfo[]>((acc, id) => {
      const persona = personas.find((p) => p.id === id);
      if (persona) {
        acc.push({
          id: persona.id,
          name: persona.name,
          emoji: persona.emoji,
          status: 'pending' as MemberStatus,
        });
      }
      return acc;
    }, []);

    clearStreamingState();
    initializeMemberStatuses(memberStatuses);
    setIsConsulting(true);
    setStatusMessage('Assembling council...');

    // Create abort controller
    const controller = new AbortController();
    setAbortController(controller);

    // Build request
    const request: ConsultationRequest = {
      query: query.trim(),
      context: context.trim() || undefined,
      domain: settings.domain || 'general',
      members: effectiveMembers,
      mode: settings.mode || 'synthesis',
      provider: settings.provider || 'openai',
      model: settings.model || undefined,
      base_url: settings.base_url || undefined,
      api_key: apiKey || undefined,
      enable_tts: settings.enable_tts || false,
      temperature: settings.temperature || 0.7,
      max_tokens: settings.max_tokens || 1000,
      session_id: sessionId || undefined,
      auto_recall: autoRecall,
    };

    try {
      const response = await submitStreamingConsultation(request, controller.signal);
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      if (!reader) {
        throw new Error('No response body');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const event = parseSSELine(line) as StreamEvent | null;
          if (event) {
            handleStreamEvent(event);
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        setStatusMessage('Consultation cancelled.');
      } else {
        setStatusMessage(err instanceof Error ? err.message : 'An error occurred.');
      }
      setIsConsulting(false);
    } finally {
      setAbortController(null);
    }
  }, [
    query,
    context,
    settings,
    selectedMembers,
    domains,
    personas,
    apiKey,
    sessionId,
    autoRecall,
    clearStreamingState,
    initializeMemberStatuses,
    setIsConsulting,
    setStatusMessage,
    setAbortController,
    handleStreamEvent,
  ]);

  return (
    <div className="flex-row gap-12 mt-20">
      <button
        type="button"
        id="submit"
        onClick={handleSubmit}
        disabled={isConsulting || !query.trim()}
        className="flex-full"
      >
        {isConsulting ? (
          <>
            <span className="loading"></span> Consulting...
          </>
        ) : (
          '🗣️ Consult the Council'
        )}
      </button>

      {isConsulting && abortController && (
        <button type="button" id="cancel" className="btn-secondary" onClick={cancelConsultation}>
          ✕ Cancel
        </button>
      )}
    </div>
  );
};

export default SubmitButton;
