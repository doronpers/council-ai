/**
 * TTSSettings Component - Text-to-Speech configuration
 */
import React, { useState, useEffect } from 'react';
import './TTSSettings.css';
import { useApp } from '../../context/AppContext';
import { loadTTSVoices } from '../../utils/api';
import { logger, createLogContext } from '../../utils/logger';
import type { TTSVoice } from '../../types';

const TTSSettings: React.FC = () => {
  const { config, settings, updateSettings } = useApp();
  const [voices, setVoices] = useState<TTSVoice[]>([]);
  const [isLoadingVoices, setIsLoadingVoices] = useState(false);

  // Check if TTS is available
  const hasKeys = config?.tts?.has_elevenlabs_key || config?.tts?.has_openai_key;

  // Load voices when TTS is enabled
  useEffect(() => {
    if (settings.enable_tts && hasKeys && voices.length === 0) {
      setIsLoadingVoices(true);
      loadTTSVoices()
        .then(setVoices)
        .catch((err) => logger.error('Failed to load voices', err instanceof Error ? err : undefined, createLogContext('TTSSettings')))
        .finally(() => setIsLoadingVoices(false));
    }
  }, [settings.enable_tts, hasKeys, voices.length]);

  if (!config?.tts) {
    return null;
  }

  return (
    <div className="tts-settings">
      <h4 className="tts-settings-title">🔊 Text-to-Speech</h4>

      {/* Enable TTS toggle */}
      <div className="tts-toggle-wrapper">
        <label className="tts-toggle-label">
          <input
            type="checkbox"
            id="enable_tts"
            checked={settings.enable_tts || false}
            onChange={(e) => updateSettings({ enable_tts: e.target.checked })}
            disabled={!hasKeys}
          />
          Enable voice responses
        </label>
      </div>

      {/* Provider status */}
      <div
        id="tts-provider-status"
        className={`field-hint tts-provider-status ${hasKeys ? 'success' : 'error'}`}
      >
        {hasKeys
          ? `Available providers: ${[
              config.tts.has_elevenlabs_key && 'ElevenLabs',
              config.tts.has_openai_key && 'OpenAI',
            ]
              .filter(Boolean)
              .join(', ')}`
          : 'No TTS API keys configured'}
      </div>

      {/* Voice selection (shown when TTS is enabled) */}
      {settings.enable_tts && hasKeys && (
        <div id="tts-options" className="tts-options">
          <label htmlFor="tts_voice">Voice</label>
          <select
            id="tts_voice"
            value={settings.tts_voice || ''}
            onChange={(e) => updateSettings({ tts_voice: e.target.value })}
            disabled={isLoadingVoices}
          >
            <option value="">Default</option>
            {voices.map((voice) => (
              <option key={voice.id} value={voice.id}>
                {voice.name} ({voice.provider})
              </option>
            ))}
          </select>
          {isLoadingVoices && (
            <span className="muted tts-loading-indicator">Loading voices...</span>
          )}
        </div>
      )}
    </div>
  );
};

export default TTSSettings;
