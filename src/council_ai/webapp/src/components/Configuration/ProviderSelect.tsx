/**
 * ProviderSelect Component - LLM provider selection
 */
import React from 'react';
import { useApp } from '../../context/AppContext';

const ProviderSelect: React.FC = () => {
  const { providers, settings, updateSettings } = useApp();

  return (
    <div>
      <label htmlFor="provider">Provider</label>
      <select
        id="provider"
        value={settings.provider || ''}
        onChange={(e) => updateSettings({ provider: e.target.value })}
      >
        {providers.map((provider) => (
          <option key={provider} value={provider}>
            {provider}
          </option>
        ))}
      </select>
      <p className="field-hint">Saved to browser</p>
    </div>
  );
};

export default ProviderSelect;
