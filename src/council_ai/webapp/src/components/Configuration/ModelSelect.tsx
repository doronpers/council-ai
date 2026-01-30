/**
 * ModelSelect Component - Model selection dropdown
 */
import React from 'react';
import { useApp } from '../../context/AppContext';
import { getModelsForProvider } from '../../utils/helpers';

const ModelSelect: React.FC = () => {
  const { models, settings, updateSettings } = useApp();

  const availableModels = getModelsForProvider(models, settings.provider || '');

  return (
    <div>
      <label htmlFor="model">Model</label>
      <select
        id="model"
        value={settings.model || ''}
        onChange={(e) => updateSettings({ model: e.target.value })}
      >
        <option value="">Default</option>
        {availableModels.map((model) => (
          <option key={model} value={model}>
            {model}
          </option>
        ))}
      </select>
      <p className="field-hint">Saved to browser</p>
    </div>
  );
};

export default ModelSelect;
