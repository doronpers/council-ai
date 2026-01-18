/**
 * PersonalIntegrationSection Component - Personal integration status and controls
 */
import React, { useState, useEffect } from 'react';
import { useNotifications } from '../Layout/NotificationContainer';

interface PersonalStatus {
  detected: boolean;
  configured: boolean;
  repo_path: string | null;
  config_dir: string | null;
  available?: {
    configs?: boolean;
    personas?: number;
    scripts?: number;
  };
}

const PersonalIntegrationSection: React.FC = () => {
  const [status, setStatus] = useState<PersonalStatus | null>(null);
  const [isIntegrating, setIsIntegrating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verification, setVerification] = useState<any>(null);
  const { showNotification } = useNotifications();

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/personal/status');
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch personal status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleIntegrate = async () => {
    setIsIntegrating(true);
    try {
      const response = await fetch('/api/personal/integrate', {
        method: 'POST',
      });

      if (response.ok) {
        showNotification('Personal integration completed successfully!', 'success');
        await fetchStatus(); // Refresh status
      } else {
        const error = await response.json();
        showNotification(`Integration failed: ${error.detail || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      showNotification('Integration failed: Network error', 'error');
    } finally {
      setIsIntegrating(false);
    }
  };

  const handleVerify = async () => {
    setIsVerifying(true);
    try {
      const response = await fetch('/api/personal/verify');
      if (response.ok) {
        const data = await response.json();
        setVerification(data);
        const issues = data.issues || [];
        if (issues.length === 0) {
          showNotification('All verification checks passed!', 'success');
        } else {
          showNotification(`Verification found ${issues.length} issue(s)`, 'info');
        }
      }
    } catch (error) {
      showNotification('Verification failed: Network error', 'error');
    } finally {
      setIsVerifying(false);
    }
  };

  if (isLoading) {
    return (
      <div className="config-section">
        <h3>Personal Integration</h3>
        <p>Loading status...</p>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="config-section">
        <h3>Personal Integration</h3>
        <p className="config-hint">Unable to check personal integration status.</p>
      </div>
    );
  }

  return (
    <div className="config-section">
      <h3>Personal Integration</h3>
      <div className="personal-integration-status">
        <div className="status-row">
          <span className="status-label">Repository Detected:</span>
          <span className={`status-value ${status.detected ? 'status-yes' : 'status-no'}`}>
            {status.detected ? '✅ Yes' : '❌ No'}
          </span>
        </div>
        {status.detected && status.repo_path && (
          <div className="status-row">
            <span className="status-label">Repository Path:</span>
            <span className="status-value status-path">{status.repo_path}</span>
          </div>
        )}
        <div className="status-row">
          <span className="status-label">Configured:</span>
          <span className={`status-value ${status.configured ? 'status-yes' : 'status-no'}`}>
            {status.configured ? '✅ Yes' : '❌ No'}
          </span>
        </div>
        {status.config_dir && (
          <div className="status-row">
            <span className="status-label">Config Directory:</span>
            <span className="status-value status-path">{status.config_dir}</span>
          </div>
        )}

        {status.available && (
          <div className="status-available">
            <strong>Available Resources:</strong>
            <ul>
              {status.available.configs && <li>Personal configurations</li>}
              {status.available.personas && <li>{status.available.personas} personal personas</li>}
              {status.available.scripts && <li>{status.available.scripts} personal scripts</li>}
            </ul>
          </div>
        )}

        {status.detected && !status.configured && (
          <div className="personal-integration-actions">
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleIntegrate}
              disabled={isIntegrating}
            >
              {isIntegrating ? 'Integrating...' : 'Integrate Now'}
            </button>
            <p className="config-hint">
              This will copy your personal configurations to the config directory.
            </p>
          </div>
        )}

        {status.configured && (
          <div className="personal-integration-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleVerify}
              disabled={isVerifying}
            >
              {isVerifying ? 'Verifying...' : 'Verify Integration'}
            </button>
          </div>
        )}

        {verification && (
          <div className="verification-results">
            <strong>Verification Results:</strong>
            <ul>
              {verification.issues && verification.issues.length > 0 ? (
                verification.issues.map((issue: string, index: number) => (
                  <li key={index} className="verification-issue">
                    ⚠️ {issue}
                  </li>
                ))
              ) : (
                <li className="verification-success">✅ All checks passed!</li>
              )}
            </ul>
          </div>
        )}

        {!status.detected && (
          <div className="personal-integration-help">
            <p className="config-hint">
              No council-ai-personal repository detected. This is optional.
            </p>
            <p className="config-hint">
              To set it up, place council-ai-personal in one of these locations:
            </p>
            <ul className="config-hint-list">
              <li>Sibling directory: ../council-ai-personal</li>
              <li>Home directory: ~/council-ai-personal</li>
              <li>Or set COUNCIL_AI_PERSONAL_PATH environment variable</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonalIntegrationSection;
