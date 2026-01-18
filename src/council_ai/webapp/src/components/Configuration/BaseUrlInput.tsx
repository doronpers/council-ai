/**
 * BaseUrlInput Component - Base URL input for custom endpoints
 */
import React from 'react';
import { useApp } from '../../context/AppContext';

const BaseUrlInput: React.FC = () => {
  const { settings, updateSettings } = useApp();

  return (
    <div>
      <label htmlFor="base_url">Base URL</label>
      <input
        type="url"
        id="base_url"
        placeholder="https://api.openai.com/v1"
        value={settings.base_url || ''}
        onChange={(e) => updateSettings({ base_url: e.target.value || undefined })}
      />
      <p className="field-hint">
        For local or custom endpoints. Leave empty for provider defaults.
      </p>
    </div>
  );
};

export default BaseUrlInput;
