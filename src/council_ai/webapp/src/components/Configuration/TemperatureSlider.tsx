/**
 * TemperatureSlider Component - Temperature control
 */
import React from 'react';
import { useApp } from '../../context/AppContext';

const TemperatureSlider: React.FC = () => {
  const { settings, updateSettings } = useApp();

  return (
    <div>
      <label htmlFor="temperature">
        Temperature: <span id="temperature-value">{settings.temperature?.toFixed(1) || '0.7'}</span>
      </label>
      <input
        type="range"
        id="temperature"
        min="0"
        max="2"
        step="0.1"
        value={settings.temperature || 0.7}
        onChange={(e) => updateSettings({ temperature: parseFloat(e.target.value) })}
      />
    </div>
  );
};

export default TemperatureSlider;
