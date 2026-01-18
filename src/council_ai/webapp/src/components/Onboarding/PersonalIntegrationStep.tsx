/**
 * PersonalIntegrationStep Component - Personal integration step in onboarding
 */
import React, { useState, useEffect } from 'react';
import { useNotifications } from '../Layout/NotificationContainer';

interface PersonalStatus {
  detected: boolean;
  configured: boolean;
  repo_path: string | null;
  available?: {
    configs?: boolean;
    personas?: number;
    scripts?: number;
  };
}

const PersonalIntegrationStep: React.FC = () => {
  const [status, setStatus] = useState<PersonalStatus | null>(null);
  const [isIntegrating, setIsIntegrating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
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

  if (isLoading) {
    return <div className="wizard-loading">Checking for personal integration...</div>;
  }

  if (!status) {
    return (
      <div className="wizard-personal-integration">
        <p>Unable to check personal integration status.</p>
      </div>
    );
  }

  if (!status.detected) {
    return (
      <div className="wizard-personal-integration">
        <p>No council-ai-personal repository detected. This is optional and can be set up later.</p>
        <p className="wizard-hint">
          If you have a council-ai-personal repository, place it in one of these locations:
        </p>
        <ul>
          <li>Sibling directory: ../council-ai-personal</li>
          <li>Home directory: ~/council-ai-personal</li>
          <li>Or set COUNCIL_AI_PERSONAL_PATH environment variable</li>
        </ul>
      </div>
    );
  }

  if (status.configured) {
    return (
      <div className="wizard-personal-integration">
        <div className="wizard-success">
          <span className="success-icon">✅</span>
          <div>
            <strong>Personal integration is active!</strong>
            <p>Your personal configurations and personas are available.</p>
            {status.available && (
              <ul>
                {status.available.configs && <li>Personal configs loaded</li>}
                {status.available.personas && (
                  <li>{status.available.personas} personal personas available</li>
                )}
                {status.available.scripts && (
                  <li>{status.available.scripts} personal scripts available</li>
                )}
              </ul>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="wizard-personal-integration">
      <div className="wizard-detected">
        <span className="detected-icon">📦</span>
        <div>
          <strong>council-ai-personal repository detected!</strong>
          <p>Found at: {status.repo_path}</p>
          {status.available && (
            <div className="wizard-available">
              <p>Available resources:</p>
              <ul>
                {status.available.configs && <li>Personal configurations</li>}
                {status.available.personas && (
                  <li>{status.available.personas} personal personas</li>
                )}
                {status.available.scripts && <li>{status.available.scripts} personal scripts</li>}
              </ul>
            </div>
          )}
          <button
            type="button"
            className="btn btn-primary wizard-integrate-btn"
            onClick={handleIntegrate}
            disabled={isIntegrating}
          >
            {isIntegrating ? 'Integrating...' : 'Integrate Now'}
          </button>
          <p className="wizard-hint">
            This will copy your personal configurations to ~/.config/council-ai/
          </p>
        </div>
      </div>
    </div>
  );
};

export default PersonalIntegrationStep;
