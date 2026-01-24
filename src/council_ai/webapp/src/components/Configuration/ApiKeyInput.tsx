/**
 * ApiKeyInput Component - Secure API key input with validation
 */
import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { getValidationError } from '../../utils/errorMessages';
import { ValidationRules } from '../../utils/validation';

const ApiKeyInput: React.FC = () => {
  const { apiKey, setApiKey } = useApp();
  const [error, setError] = useState<string | null>(null);
  const [touched, setTouched] = useState(false);

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
      }
    } else if (touched && !apiKey) {
      // API key is optional (can use env var), so clear error if empty
      setError(null);
    }
  }, [apiKey, touched]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setApiKey(newValue);
    if (touched && newValue) {
      const validationError = getValidationError('apiKey', newValue);
      if (validationError) {
        setError(validationError);
      } else {
        const minLengthError = ValidationRules.apiKey.minLength(10).validate(newValue)
          ? null
          : ValidationRules.apiKey.minLength(10).message;
        setError(minLengthError);
      }
    } else if (touched && !newValue) {
      setError(null);
    }
  };

  const handleBlur = () => {
    setTouched(true);
    if (apiKey) {
      const validationError = getValidationError('apiKey', apiKey);
      if (validationError) {
        setError(validationError);
      } else {
        const minLengthError = ValidationRules.apiKey.minLength(10).validate(apiKey)
          ? null
          : ValidationRules.apiKey.minLength(10).message;
        setError(minLengthError);
      }
    }
  };

  return (
    <div>
      <label htmlFor="api_key">API Key</label>
      <form onSubmit={(e) => e.preventDefault()}>
        <input
          type="password"
          id="api_key"
          placeholder="Uses environment variable if empty"
          value={apiKey}
          onChange={handleChange}
          onBlur={handleBlur}
          autoComplete="off"
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? 'api_key-error' : 'api_key-hint'}
          className={error ? 'input-error' : ''}
        />
      </form>
      {error && (
        <p id="api_key-error" className="field-error" role="alert">
          {error}
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
