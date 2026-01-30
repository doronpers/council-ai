/**
 * ApiKeyInput Component - Secure API key input with validation and provider awareness
 */
import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { getValidationError } from '../../utils/errorMessages';
import { ValidationRules } from '../../utils/validation';

const ApiKeyInput: React.FC = () => {
  const { apiKey, setApiKey, settings } = useApp();
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [touched, setTouched] = useState(false);

  // Determine if API key is required for the selected provider
  const isKeyRequiredForProvider = (provider: string) => {
    return !['lmstudio', 'local', 'ollama'].includes(provider);
  };

  const isLocalProvider =
    settings.provider && ['lmstudio', 'local', 'ollama'].includes(settings.provider);

  // Validate on change if touched
  useEffect(() => {
    if (touched && apiKey) {
      const validationError = getValidationError('apiKey', apiKey);
      if (validationError) {
        setError(validationError);
      } else {
        // Additional format validation
        const minLengthError = ValidationRules.apiKey.minLength(10).validate(apiKey)
          ? null
          : ValidationRules.apiKey.minLength(10).message;
        setError(minLengthError);
        setWarning(null);
      }
    } else if (touched && !apiKey && isKeyRequiredForProvider(settings.provider || '')) {
      // Warning if key is required but empty
      setWarning(
        `${settings.provider?.toUpperCase() || 'Cloud provider'} typically requires an API key. Check if an environment variable is set.`
      );
      setError(null);
    } else if (touched && !apiKey) {
      // Clear error if field is empty and provider doesn't require key
      setError(null);
      setWarning(null);
    }
  }, [apiKey, touched, settings.provider]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setApiKey(newValue);
    if (touched && newValue) {
      const validationError = getValidationError('apiKey', newValue);
      if (validationError) {
        setError(validationError);
        setWarning(null);
      } else {
        const minLengthError = ValidationRules.apiKey.minLength(10).validate(newValue)
          ? null
          : ValidationRules.apiKey.minLength(10).message;
        setError(minLengthError);
        setWarning(null);
      }
    } else if (touched && !newValue && isKeyRequiredForProvider(settings.provider || '')) {
      setWarning(
        `${settings.provider?.toUpperCase() || 'Cloud provider'} typically requires an API key. Check if an environment variable is set.`
      );
      setError(null);
    } else if (touched && !newValue) {
      setError(null);
      setWarning(null);
    }
  };

  const handleBlur = () => {
    setTouched(true);
    if (apiKey) {
      const validationError = getValidationError('apiKey', apiKey);
      if (validationError) {
        setError(validationError);
        setWarning(null);
      } else {
        const minLengthError = ValidationRules.apiKey.minLength(10).validate(apiKey)
          ? null
          : ValidationRules.apiKey.minLength(10).message;
        setError(minLengthError);
        setWarning(null);
      }
    } else if (isKeyRequiredForProvider(settings.provider || '')) {
      setWarning(
        `${settings.provider?.toUpperCase() || 'Cloud provider'} typically requires an API key. Check if an environment variable is set.`
      );
      setError(null);
    }
  };

  return (
    <div>
      <label htmlFor="api_key">
        API Key{isLocalProvider && <span className="field-optional"> (optional for local)</span>}
      </label>
      <form onSubmit={(e) => e.preventDefault()}>
        <input
          type="password"
          id="api_key"
          placeholder={
            isLocalProvider ? 'Optional for local providers' : 'Uses environment variable if empty'
          }
          value={apiKey}
          onChange={handleChange}
          onBlur={handleBlur}
          autoComplete="off"
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? 'api_key-error' : warning ? 'api_key-warning' : 'api_key-hint'}
          className={error ? 'input-error' : warning ? 'input-warning' : ''}
        />
      </form>
      {error && (
        <p id="api_key-error" className="field-error" role="alert">
          {error}
        </p>
      )}
      {warning && !error && (
        <p id="api_key-warning" className="field-warning" role="alert">
          ⚠️ {warning}
        </p>
      )}
      <p id="api_key-hint" className="field-hint">
        Session only - never saved
        {apiKey && !error && <span className="field-hint-success"> ✓ Valid format</span>}
      </p>
    </div>
  );
};

export default ApiKeyInput;
