/**
 * ConfigDiagnostics Component - Display configuration health and recommendations
 */
import React, { useState, useEffect } from 'react';
import { useNotifications } from '../Layout/NotificationContainer';

interface ConfigDiagnosticsData {
  timestamp: string;
  config_sources: Record<
    string,
    {
      value: unknown;
      source: string;
      overridden: boolean;
    }
  >;
  api_keys: Record<
    string,
    {
      configured: boolean;
      placeholder: boolean;
      source: string;
    }
  >;
  providers: Record<
    string,
    {
      available: boolean;
      tested: boolean;
      error?: string;
    }
  >;
  recommendations: Array<{
    type: string;
    message: string;
    action: string;
  }>;
  warnings: Array<{
    type: string;
    message: string;
    action: string;
  }>;
  errors: Array<{
    type: string;
    message: string;
    action: string;
  }>;
}

const ConfigDiagnostics: React.FC = () => {
  const { showNotification } = useNotifications();
  const [diagnostics, setDiagnostics] = useState<ConfigDiagnosticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['issues']));

  const fetchDiagnostics = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetch('/api/config/diagnostics');
      if (!response.ok) {
        throw new Error('Failed to fetch diagnostics');
      }
      const data = await response.json();
      setDiagnostics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      showNotification('Failed to load configuration diagnostics', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDiagnostics();
  }, []);

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const getSourceBadge = (source: string) => {
    const badges = {
      cli: { text: 'CLI', class: 'source-cli' },
      env: { text: 'Env', class: 'source-env' },
      file: { text: 'File', class: 'source-file' },
      default: { text: 'Default', class: 'source-default' },
    };
    const badge = badges[source as keyof typeof badges] || badges.default;
    return <span className={`source-badge ${badge.class}`}>{badge.text}</span>;
  };

  const getStatusIcon = (status: boolean | string) => {
    if (typeof status === 'boolean') {
      return status ? '✅' : '❌';
    }
    return status === 'healthy' ? '✅' : status === 'warning' ? '⚠️' : '❌';
  };

  if (isLoading) {
    return (
      <div className="config-diagnostics">
        <div className="diagnostics-loading">
          <span className="loading"></span> Analyzing configuration...
        </div>
      </div>
    );
  }

  if (error || !diagnostics) {
    return (
      <div className="config-diagnostics">
        <div className="diagnostics-error">
          <p>❌ Failed to load diagnostics: {error}</p>
          <button type="button" className="btn btn-secondary" onClick={fetchDiagnostics}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const hasIssues = diagnostics.warnings.length > 0 || diagnostics.errors.length > 0;
  const hasRecommendations = diagnostics.recommendations.length > 0;

  return (
    <div className="config-diagnostics">
      <div className="diagnostics-header">
        <h3>Configuration Diagnostics</h3>
        <div className="diagnostics-status">
          {hasIssues && <span className="status-warning">⚠️ Issues Found</span>}
          {!hasIssues && <span className="status-healthy">✅ Configuration Healthy</span>}
        </div>
        <button
          type="button"
          className="btn btn-secondary diagnostics-refresh"
          onClick={fetchDiagnostics}
        >
          🔄 Refresh
        </button>
      </div>

      {/* Issues Summary */}
      {(hasIssues || hasRecommendations) && (
        <div className="diagnostics-section">
          <button
            type="button"
            className="section-toggle"
            onClick={() => toggleSection('issues')}
            aria-expanded={expandedSections.has('issues')}
          >
            <h4>Issues & Recommendations</h4>
            <span className="toggle-icon">{expandedSections.has('issues') ? '▼' : '▶'}</span>
          </button>

          {expandedSections.has('issues') && (
            <div className="section-content">
              {/* Errors */}
              {diagnostics.errors.map((err, index) => (
                <div key={`error-${index}`} className="diagnostic-item diagnostic-error">
                  <div className="item-icon">❌</div>
                  <div className="item-content">
                    <div className="item-message">{err.message}</div>
                    <div className="item-action">{err.action}</div>
                  </div>
                </div>
              ))}

              {/* Warnings */}
              {diagnostics.warnings.map((warning, index) => (
                <div key={`warning-${index}`} className="diagnostic-item diagnostic-warning">
                  <div className="item-icon">⚠️</div>
                  <div className="item-content">
                    <div className="item-message">{warning.message}</div>
                    <div className="item-action">{warning.action}</div>
                  </div>
                </div>
              ))}

              {/* Recommendations */}
              {diagnostics.recommendations.map((rec, index) => (
                <div key={`rec-${index}`} className="diagnostic-item diagnostic-recommendation">
                  <div className="item-icon">💡</div>
                  <div className="item-content">
                    <div className="item-message">{rec.message}</div>
                    <div className="item-action">{rec.action}</div>
                  </div>
                </div>
              ))}

              {diagnostics.errors.length === 0 &&
                diagnostics.warnings.length === 0 &&
                diagnostics.recommendations.length === 0 && (
                  <div className="diagnostic-item diagnostic-healthy">
                    <div className="item-icon">✅</div>
                    <div className="item-content">
                      <div className="item-message">
                        No issues found! Your configuration looks good.
                      </div>
                    </div>
                  </div>
                )}
            </div>
          )}
        </div>
      )}

      {/* API Keys Status */}
      <div className="diagnostics-section">
        <button
          type="button"
          className="section-toggle"
          onClick={() => toggleSection('api-keys')}
          aria-expanded={expandedSections.has('api-keys')}
        >
          <h4>API Keys</h4>
          <span className="toggle-icon">{expandedSections.has('api-keys') ? '▼' : '▶'}</span>
        </button>

        {expandedSections.has('api-keys') && (
          <div className="section-content">
            {Object.entries(diagnostics.api_keys).map(([provider, status]) => (
              <div key={provider} className="diagnostic-item">
                <div className="item-icon">
                  {getStatusIcon(status.configured && !status.placeholder)}
                </div>
                <div className="item-content">
                  <div className="item-title">{provider.toUpperCase()}</div>
                  <div className="item-details">
                    {status.configured && !status.placeholder ? (
                      <span className="status-configured">Configured ({status.source})</span>
                    ) : status.placeholder ? (
                      <span className="status-placeholder">Placeholder value</span>
                    ) : (
                      <span className="status-missing">Not configured</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Provider Status */}
      <div className="diagnostics-section">
        <button
          type="button"
          className="section-toggle"
          onClick={() => toggleSection('providers')}
          aria-expanded={expandedSections.has('providers')}
        >
          <h4>Providers</h4>
          <span className="toggle-icon">{expandedSections.has('providers') ? '▼' : '▶'}</span>
        </button>

        {expandedSections.has('providers') && (
          <div className="section-content">
            {Object.entries(diagnostics.providers).map(([provider, status]) => (
              <div key={provider} className="diagnostic-item">
                <div className="item-icon">{getStatusIcon(status.available)}</div>
                <div className="item-content">
                  <div className="item-title">{provider}</div>
                  <div className="item-details">
                    {status.available ? (
                      <span className="status-available">Available</span>
                    ) : status.error ? (
                      <span className="status-error">{status.error}</span>
                    ) : (
                      <span className="status-unavailable">Not available</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Configuration Sources */}
      <div className="diagnostics-section">
        <button
          type="button"
          className="section-toggle"
          onClick={() => toggleSection('sources')}
          aria-expanded={expandedSections.has('sources')}
        >
          <h4>Configuration Sources</h4>
          <span className="toggle-icon">{expandedSections.has('sources') ? '▼' : '▶'}</span>
        </button>

        {expandedSections.has('sources') && (
          <div className="section-content">
            {Object.entries(diagnostics.config_sources).map(([key, info]) => (
              <div key={key} className="diagnostic-item">
                <div className="item-content">
                  <div className="item-title">{key}</div>
                  <div className="item-details">
                    <span className="config-value">{JSON.stringify(info.value)}</span>
                    {getSourceBadge(info.source)}
                    {info.overridden && <span className="override-indicator">Overridden</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ConfigDiagnostics;
