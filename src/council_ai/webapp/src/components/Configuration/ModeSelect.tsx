/**
 * ModeSelect Component - Consultation mode selection
 */
import React from 'react';
import { useApp } from '../../context/AppContext';

const ModeSelect: React.FC = () => {
  const { modes, settings, updateSettings } = useApp();

  return (
    <div>
      <label htmlFor="mode">Mode</label>
      <select
        id="mode"
        value={settings.mode || ''}
        onChange={(e) => updateSettings({ mode: e.target.value })}
      >
        {modes.map((mode) => (
          <option key={mode} value={mode}>
            {mode}
          </option>
        ))}
      </select>
      <p className="field-hint">Saved to browser</p>
    </div>
  );
};

export default ModeSelect;
