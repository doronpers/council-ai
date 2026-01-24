/**
 * BaseUrlInput Component - Base URL input for custom endpoints with validation
 */
import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { getValidationError } from '../../utils/errorMessages';
import { ValidationRules } from '../../utils/validation';

const BaseUrlInput: React.FC = () => {
  const { settings, updateSettings } = useApp();
  const [error, setError] = useState<string | null>(null);
  const [touched, setTouched] = useState(false);

  const value = settings.base_url || '';

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

  return (
    <div>
      <label htmlFor="base_url">Base URL</label>
      <input
        type="url"
        id="base_url"
        placeholder="https://api.openai.com/v1 or http://localhost:1234/v1"
        value={value}
        onChange={handleChange}
        onBlur={handleBlur}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? 'base_url-error' : 'base_url-hint'}
        className={error ? 'input-error' : ''}
      />
      {error && (
        <p id="base_url-error" className="field-error" role="alert">
          {error}
        </p>
      )}
      <p id="base_url-hint" className="field-hint">
        For local or custom endpoints. Leave empty for provider defaults.
        {value && !error && <span className="field-hint-success"> ✓ Valid URL format</span>}
      </p>
    </div>
  );
};

export default BaseUrlInput;
