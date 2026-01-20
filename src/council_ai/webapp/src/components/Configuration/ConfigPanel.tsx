/**
 * ConfigPanel Component - Main configuration container
 */
import React, { useMemo, useState, useEffect } from 'react';
import './ConfigPanel.css';
import ProviderSelect from './ProviderSelect';
import ModelSelect from './ModelSelect';
import DomainSelect from './DomainSelect';
import ModeSelect from './ModeSelect';
import TemperatureSlider from './TemperatureSlider';
import MaxTokensSelect from './MaxTokensSelect';
import ApiKeyInput from './ApiKeyInput';
import BaseUrlInput from './BaseUrlInput';
import MemberSelectionGrid from '../Members/MemberSelectionGrid';
import TTSSettings from '../TTS/TTSSettings';
import PersonalIntegrationSection from './PersonalIntegrationSection';
import { useApp } from '../../context/AppContext';
import { useNotifications } from '../Layout/NotificationContainer';
import type { ConfigSourceInfo, ConfigIssue, ConfigDiagnosticsResponse } from '../../types';

const ConfigPanel: React.FC = () => {
  const { saveSettings, resetSettings, settings } = useApp();
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [configSources, setConfigSources] = useState<Record<string, ConfigSourceInfo>>({});
  const [configIssues, setConfigIssues] = useState<ConfigIssue[]>([]);
  const { showNotification } = useNotifications();

  // Fetch configuration diagnostics
  useEffect(() => {
    const fetchDiagnostics = async () => {
      try {
        const response = await fetch('/api/config/diagnostics');
        if (response.ok) {
          const data: ConfigDiagnosticsResponse = await response.json();
          setConfigSources(data.config_sources || {});
          const issues: ConfigIssue[] = [
            ...(data.warnings || []).map((w) => ({ ...w, severity: 'warning' as const })),
            ...(data.errors || []).map((e) => ({ ...e, severity: 'error' as const })),
          ];
          setConfigIssues(issues);
        }
      } catch (error) {
        console.warn('Failed to fetch configuration diagnostics:', error);
      }
    };
    fetchDiagnostics();
  }, []);

  const getSourceBadge = (settingKey: string) => {
    const sourceInfo = configSources[settingKey];
    if (!sourceInfo) return null;

    const badges = {
      cli: {
        text: 'CLI',
        class: 'source-cli',
        title: 'Set via command line arguments (highest priority)',
      },
      env: { text: 'Env', class: 'source-env', title: 'Set via environment variables' },
      file: { text: 'File', class: 'source-file', title: 'Set in configuration file' },
      default: { text: 'Default', class: 'source-default', title: 'Using default value' },
    };

    const badge = badges[sourceInfo.source as keyof typeof badges] || badges.default;
    return (
      <span className={`source-badge ${badge.class}`} title={badge.title}>
        {badge.text}
      </span>
    );
  };

  const baseUrlError = useMemo(() => {
    if (!settings.base_url) return null;
    try {
      // eslint-disable-next-line no-new
      new URL(settings.base_url);
      return null;
    } catch {
      return 'Base URL must be a valid URL';
    }
  }, [settings.base_url]);

  const configStatus = useMemo(() => {
    const errors = configIssues.filter((issue) => issue.severity === 'error');
    const warnings = configIssues.filter((issue) => issue.severity === 'warning');

    if (!settings.provider) {
      return { status: 'error', message: 'Select a provider' };
    }
    if (baseUrlError) {
      return { status: 'error', message: baseUrlError };
    }
    if (errors.length > 0) {
      return { status: 'error', message: `${errors.length} configuration error(s) found` };
    }
    if (warnings.length > 0) {
      return { status: 'warning', message: `${warnings.length} configuration warning(s)` };
    }
    return { status: 'valid', message: 'Configuration looks good' };
  }, [settings.provider, baseUrlError, configIssues]);

  const handleSave = () => {
    saveSettings();
    showNotification('Settings saved', 'success');
  };

  const handleReset = () => {
    resetSettings();
    showNotification('Settings reset to defaults', 'info');
  };

  return (
    <div className="config-panel">
      <div className={`config-status-indicator ${configStatus.status}`}>
        {configStatus.message}
        {configIssues.length > 0 && (
          <button
            type="button"
            className="config-issues-toggle"
            onClick={() => setShowAdvanced(!showAdvanced)}
            title="View configuration issues"
          >
            View Issues
          </button>
        )}
      </div>

      {/* Configuration Issues */}
      {configIssues.length > 0 && (
        <div className="config-issues">
          {configIssues.map((issue, index) => (
            <div key={index} className={`config-issue config-issue-${issue.severity}`}>
              <span className="issue-icon">{issue.severity === 'error' ? '❌' : '⚠️'}</span>
              <span className="issue-message">{issue.message}</span>
            </div>
          ))}
        </div>
      )}

      <div className="config-section">
        <h3>Essentials</h3>
        <p className="config-help">
          Choose a domain and provider. API keys can be set here or via environment variables.
        </p>
        <div className="config-field-group grid">
          <div className="config-field-wrapper">
            <DomainSelect />
            {getSourceBadge('default_domain')}
          </div>
          <div className="config-field-wrapper">
            <ProviderSelect />
            {getSourceBadge('api.provider')}
          </div>
          <div className="config-field-wrapper">
            <ApiKeyInput />
            {/* API key source is handled differently */}
          </div>
        </div>
      </div>

      <div className="config-section">
        <h3>Members</h3>
        <p className="config-help">Select the council members who will respond to your query.</p>
        <MemberSelectionGrid />
      </div>

      <details
        open={showAdvanced}
        onToggle={(e) => setShowAdvanced((e.target as HTMLDetailsElement).open)}
      >
        <summary className="advanced-toggle">⚙️ Advanced Settings</summary>

        <div className="advanced-settings">
          <div className="grid">
            <div className="config-field-wrapper">
              <ModeSelect />
              {getSourceBadge('mode')}
            </div>
            <div className="config-field-wrapper">
              <ModelSelect />
              {getSourceBadge('api.model')}
            </div>
            <div className="config-field-wrapper">
              <TemperatureSlider />
              {getSourceBadge('temperature')}
            </div>
            <div className="config-field-wrapper">
              <MaxTokensSelect />
              {getSourceBadge('max_tokens_per_response')}
            </div>
          </div>

          <div className="config-field-wrapper">
            <BaseUrlInput />
            {getSourceBadge('api.base_url')}
          </div>
          {baseUrlError && (
            <div className="config-field-error" role="alert">
              {baseUrlError}
            </div>
          )}

          <TTSSettings />

          <PersonalIntegrationSection />

          <div className="config-actions">
            <button type="button" className="btn btn-secondary" onClick={handleReset}>
              Reset to Defaults
            </button>
            <button type="button" className="btn btn-primary" onClick={handleSave}>
              Save Settings
            </button>
          </div>
        </div>
      </details>
    </div>
  );
};

export default ConfigPanel;
