/**
 * BaseUrlInput Component - Base URL input for custom endpoints with validation and provider guidance
 */
import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { getValidationError } from '../../utils/errorMessages';
import { ValidationRules } from '../../utils/validation';

// Provider-specific URL hints
const PROVIDER_URL_HINTS: Record<string, { label: string; defaultUrl: string; example: string }> = {
  lmstudio: {
    label: 'LM Studio',
    defaultUrl: 'http://localhost:1234/v1',
    example: 'Download from https://lmstudio.ai and start the local server',
  },
  ollama: {
    label: 'Ollama',
    defaultUrl: 'http://localhost:11434/v1',
    example: 'Ollama API endpoint - make sure Ollama server is running',
  },
  local: {
    label: 'Local',
    defaultUrl: 'http://localhost:8000/v1',
    example: 'Your custom local API endpoint',
  },
  openai: {
    label: 'OpenAI',
    defaultUrl: 'https://api.openai.com/v1',
    example: 'Default OpenAI endpoint (or use compatible provider)',
  },
  anthropic: {
    label: 'Anthropic',
    defaultUrl: 'https://api.anthropic.com',
    example: 'Default Anthropic endpoint',
  },
  gemini: {
    label: 'Google Gemini',
    defaultUrl: 'https://generativelanguage.googleapis.com',
    example: 'Default Gemini endpoint',
  },
};

const BaseUrlInput: React.FC = () => {
  const { settings, updateSettings } = useApp();
  const [error, setError] = useState<string | null>(null);
  const [touched, setTouched] = useState(false);
  const [showHint, setShowHint] = useState(false);

  const value = settings.base_url || '';
  const providerHint = settings.provider ? PROVIDER_URL_HINTS[settings.provider] : null;

  // Validate on change if touched
  useEffect(() => {
    if (touched && value) {
      const validationError = getValidationError('baseUrl', value);
      if (validationError) {
        setError(validationError);
      } else {
        // Additional URL format validation
        const urlError = ValidationRules.url.valid.validate(value)
          ? null
          : ValidationRules.url.valid.message;
        setError(urlError);
      }
    } else if (touched && !value) {
      // Clear error if field is empty (it's optional)
      setError(null);
    }
  }, [value, touched]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    updateSettings({ base_url: newValue || undefined });
    if (touched) {
      const validationError = getValidationError('baseUrl', newValue);
      if (validationError) {
        setError(validationError);
      } else if (newValue) {
        const urlError = ValidationRules.url.valid.validate(newValue)
          ? null
          : ValidationRules.url.valid.message;
        setError(urlError);
      } else {
        setError(null);
      }
    }
  };

  const handleBlur = () => {
    setTouched(true);
    if (value) {
      const validationError = getValidationError('baseUrl', value);
      if (validationError) {
        setError(validationError);
      } else {
        const urlError = ValidationRules.url.valid.validate(value)
          ? null
          : ValidationRules.url.valid.message;
        setError(urlError);
      }
    }
  };

  const handleUseDefault = () => {
    if (providerHint) {
      updateSettings({ base_url: providerHint.defaultUrl });
      setError(null);
      setShowHint(false);
    }
  };

  return (
    <div>
      <label htmlFor="base_url">
        Base URL {providerHint && <span className="field-label-hint">({providerHint.label})</span>}
      </label>
      <div className="base-url-input-wrapper">
        <input
          type="url"
          id="base_url"
          placeholder={providerHint?.defaultUrl || 'https://api.example.com/v1'}
          value={value}
          onChange={handleChange}
          onBlur={handleBlur}
          onFocus={() => setShowHint(true)}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? 'base_url-error' : 'base_url-hint'}
          className={error ? 'input-error' : ''}
        />
        {providerHint && value !== providerHint.defaultUrl && (
          <button
            type="button"
            className="btn-minimal btn-small base-url-reset"
            onClick={handleUseDefault}
            title="Use default URL for this provider"
          >
            Use default
          </button>
        )}
      </div>
      {error && (
        <p id="base_url-error" className="field-error" role="alert">
          {error}
        </p>
      )}
      <div id="base_url-hint" className="field-hint">
        {providerHint ? (
          <>
            <p>
              <strong>{providerHint.label}:</strong> {providerHint.example}
            </p>
            {providerHint.defaultUrl && (
              <p className="field-hint-code">
                Default: <code>{providerHint.defaultUrl}</code>
              </p>
            )}
          </>
        ) : (
          <p>Leave empty to use provider defaults. Or enter a custom API endpoint.</p>
        )}
        {value && !error && <p className="field-hint-success">✓ Valid URL format</p>}
      </div>
    </div>
  );
};

export default BaseUrlInput;
