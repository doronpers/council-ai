/**
 * AudioPlayer Component - TTS audio playback
 */
import React, { useState, useRef } from 'react';
import { useApp } from '../../context/AppContext';
import { generateTTSAudio } from '../../utils/api';

interface AudioPlayerProps {
  synthesisText: string;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ synthesisText }) => {
  const { settings, config } = useApp();
  const audioRef = useRef<HTMLAudioElement>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if TTS is enabled and available
  const ttsEnabled = settings.enable_tts && config?.tts;
  const hasKeys = config?.tts?.has_elevenlabs_key || config?.tts?.has_openai_key;

  if (!ttsEnabled || !hasKeys) {
    return null;
  }

  const handleGenerateAudio = async () => {
    if (isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await generateTTSAudio(synthesisText, settings.tts_voice);
      setAudioUrl(result.audio_url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate audio');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="audio-player" style={{ marginTop: '16px' }}>
      {!audioUrl && (
        <button
          type="button"
          className="btn-secondary"
          onClick={handleGenerateAudio}
          disabled={isLoading}
          style={{ width: 'auto' }}
        >
          {isLoading ? (
            <>
              <span className="loading"></span> Generating audio...
            </>
          ) : (
            '🔊 Listen to Synthesis'
          )}
        </button>
      )}

      {error && (
        <p className="error" style={{ marginTop: '8px' }}>
          {error}
        </p>
      )}

      {audioUrl && (
        <div style={{ marginTop: '8px' }}>
          <audio ref={audioRef} controls src={audioUrl} style={{ width: '100%' }}>
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </div>
  );
};

export default AudioPlayer;
