/**
 * ConfigPanel Component - Main configuration container
 */
import React, { useState } from 'react';
import ProviderSelect from './ProviderSelect';
import ModelSelect from './ModelSelect';
import DomainSelect from './DomainSelect';
import ModeSelect from './ModeSelect';
import TemperatureSlider from './TemperatureSlider';
import MaxTokensSelect from './MaxTokensSelect';
import ApiKeyInput from './ApiKeyInput';
import MemberSelectionGrid from '../Members/MemberSelectionGrid';
import TTSSettings from '../TTS/TTSSettings';
import { useApp } from '../../context/AppContext';

const ConfigPanel: React.FC = () => {
    const { saveSettings, resetSettings } = useApp();
    const [showAdvanced, setShowAdvanced] = useState(false);

    return (
        <div className="config-panel">
            {/* Basic Configuration Grid */}
            <div className="grid">
                <DomainSelect />
                <ModeSelect />
                <ProviderSelect />
                <ModelSelect />
            </div>

            {/* Member Selection */}
            <div style={{ marginTop: '20px' }}>
                <label htmlFor="members-container">Custom Members</label>
                <MemberSelectionGrid />
            </div>

            {/* Advanced Settings Toggle */}
            <details
                open={showAdvanced}
                onToggle={(e) => setShowAdvanced((e.target as HTMLDetailsElement).open)}
            >
                <summary className="advanced-toggle">
                    ⚙️ Advanced Settings
                </summary>

                <div className="advanced-settings" style={{ marginTop: '16px' }}>
                    <div className="grid">
                        <TemperatureSlider />
                        <MaxTokensSelect />
                    </div>

                    <ApiKeyInput />

                    {/* TTS Settings */}
                    <TTSSettings />

                    {/* Save/Reset Buttons */}
                    <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
                        <button
                            type="button"
                            className="btn-secondary"
                            onClick={saveSettings}
                            style={{ flex: 1 }}
                        >
                            💾 Save Settings
                        </button>
                        <button
                            type="button"
                            className="btn-secondary"
                            onClick={resetSettings}
                            style={{ flex: 1 }}
                        >
                            🔄 Reset to Defaults
                        </button>
                    </div>
                </div>
            </details>
        </div>
    );
};

export default ConfigPanel;
