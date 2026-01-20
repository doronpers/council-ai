/**
 * ApiKeyInput Component - Secure API key input
 */
import React from 'react';
import { useApp } from '../../context/AppContext';

const ApiKeyInput: React.FC = () => {
  const { apiKey, setApiKey } = useApp();

  return (
    <div>
      <label htmlFor="api_key">API Key</label>
      <form onSubmit={(e) => e.preventDefault()}>
        <input
          type="password"
          id="api_key"
          placeholder="Uses environment variable if empty"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          autoComplete="off"
        />
      </form>
      <p className="field-hint">Session only - never saved</p>
    </div>
  );
};

export default ApiKeyInput;
