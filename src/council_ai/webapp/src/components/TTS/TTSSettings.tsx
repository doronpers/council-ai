/**
 * TTSSettings Component - Text-to-Speech configuration
 */
import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { loadTTSVoices } from '../../utils/api';
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
        .catch((err) => console.error('Failed to load voices:', err))
        .finally(() => setIsLoadingVoices(false));
    }
  }, [settings.enable_tts, hasKeys, voices.length]);

  if (!config?.tts) {
    return null;
  }

  return (
    <div style={{ marginTop: '20px' }}>
      <h4
        style={{
          fontSize: '13px',
          textTransform: 'uppercase',
          marginBottom: '12px',
          color: 'var(--text-secondary)',
        }}
      >
        🔊 Text-to-Speech
      </h4>

      {/* Enable TTS toggle */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
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
        className={`field-hint ${hasKeys ? 'success' : 'error'}`}
        style={{ marginBottom: '12px' }}
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
        <div id="tts-options" style={{ marginTop: '12px' }}>
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
            <span className="muted" style={{ marginLeft: '8px' }}>
              Loading voices...
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default TTSSettings;
