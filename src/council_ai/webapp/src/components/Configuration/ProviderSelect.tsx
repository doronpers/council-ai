/**
 * ProviderSelect Component - LLM provider selection
 */
import React from 'react';
import { useApp } from '../../context/AppContext';

// Default base URLs for providers
const PROVIDER_BASE_URLS: Record<string, string> = {
  openai: 'https://api.openai.com/v1',
  anthropic: 'https://api.anthropic.com',
  gemini: 'https://generativelanguage.googleapis.com',
  lmstudio: 'http://localhost:1234/v1',
  local: 'http://localhost:8000/v1',
  ollama: 'http://localhost:11434/v1',
};

const ProviderSelect: React.FC = () => {
  const { providers, settings, updateSettings } = useApp();

  const handleProviderChange = (provider: string) => {
    const previousProvider = settings.provider;
    const previousDefaultBaseUrl = previousProvider
      ? PROVIDER_BASE_URLS[previousProvider]
      : undefined;

    // Auto-prefill base URL for known providers if no custom URL is set.
    // Treat "default URL for previous provider" as non-custom so switching providers updates it.
    const shouldAutoPrefillBaseUrl =
      !settings.base_url ||
      (previousDefaultBaseUrl !== undefined && settings.base_url === previousDefaultBaseUrl);

    updateSettings({
      provider,
      ...(shouldAutoPrefillBaseUrl && PROVIDER_BASE_URLS[provider]
        ? { base_url: PROVIDER_BASE_URLS[provider] }
        : {}),
    });
  };

  const getProviderHint = (provider: string) => {
    if (provider === 'lmstudio') {
      return 'Local LM Studio - default: http://localhost:1234/v1';
    }
    if (provider === 'local' || provider === 'ollama') {
      return 'Local endpoint - configure Base URL in Advanced Settings';
    }
    if (PROVIDER_BASE_URLS[provider]) {
      return `Default: ${PROVIDER_BASE_URLS[provider]}`;
    }
    return 'Configure Base URL in Advanced Settings';
  };

  return (
    <div>
      <label htmlFor="provider">Provider</label>
      <select
        id="provider"
        value={settings.provider || ''}
        onChange={(e) => handleProviderChange(e.target.value)}
      >
        {providers.map((provider) => (
          <option key={provider} value={provider}>
            {provider}
          </option>
        ))}
      </select>
      <p className="field-hint">
        {settings.provider ? getProviderHint(settings.provider) : 'Select a provider'}
      </p>
    </div>
  );
};

export default ProviderSelect;
