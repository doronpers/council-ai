/**
 * App Context - Global application state
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { AppConfig, Persona, Domain, UserSettings, ModelCapability } from '../types';
import { loadAppInfo } from '../utils/api';
import { logger, createLogContext } from '../utils/logger';

interface AppContextType {
  // Configuration data
  config: AppConfig | null;
  isLoading: boolean;
  error: string | null;

  // Derived data
  personas: Persona[];
  domains: Domain[];
  providers: string[];
  modes: string[];
  models: ModelCapability[];

  // User settings
  settings: UserSettings;
  updateSettings: (updates: Partial<UserSettings>) => void;
  saveSettings: () => void;
  resetSettings: () => void;

  // Selected members
  selectedMembers: string[];
  setSelectedMembers: React.Dispatch<React.SetStateAction<string[]>>;

  // API key (session only, never persisted)
  apiKey: string;
  setApiKey: React.Dispatch<React.SetStateAction<string>>;

  // Session and memory management
  sessionId: string | null;
  setSessionId: React.Dispatch<React.SetStateAction<string | null>>;
  autoRecall: boolean;
  setAutoRecall: React.Dispatch<React.SetStateAction<boolean>>;

  // Refresh config
  refreshConfig: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const SETTINGS_KEY = 'council-ai-settings';
const SESSION_KEY = 'council-ai-session-id';
const AUTORECALL_KEY = 'council-ai-auto-recall';

const defaultSettings: UserSettings = {
  provider: 'openai',
  mode: 'synthesis',
  domain: 'general',
  temperature: 0.7,
  max_tokens: 1000,
  enable_tts: false,
};

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [settings, setSettings] = useState<UserSettings>(() => {
    try {
      const saved = localStorage.getItem(SETTINGS_KEY);
      return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
    } catch {
      return defaultSettings;
    }
  });
  const [selectedMembers, setSelectedMembers] = useState<string[]>([]);
  const [apiKey, setApiKey] = useState('');

  // Session and memory management
  const [sessionId, setSessionId] = useState<string | null>(() => {
    try {
      return localStorage.getItem(SESSION_KEY);
    } catch {
      return null;
    }
  });
  const [autoRecall, setAutoRecall] = useState<boolean>(() => {
    try {
      const stored = localStorage.getItem(AUTORECALL_KEY);
      return stored !== null ? stored === 'true' : true; // Default to true for personal mode
    } catch {
      return true;
    }
  });

  // Load initial configuration
  const refreshConfig = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await loadAppInfo();
      setConfig(data);

      // Apply defaults from config if not set
      setSettings((prev) => ({
        ...prev,
        provider: prev.provider || data.defaults.provider,
        mode: prev.mode || data.defaults.mode,
        domain: prev.domain || data.defaults.domain,
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load configuration');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshConfig();
  }, []);

  // Update settings
  const updateSettings = (updates: Partial<UserSettings>) => {
    setSettings((prev) => ({ ...prev, ...updates }));
  };

  // Save settings to localStorage
  const saveSettings = () => {
    try {
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    } catch (err) {
      logger.storageError('save settings', err, createLogContext('AppContext'));
    }
  };

  // Reset settings to defaults
  const resetSettings = () => {
    setSettings(defaultSettings);
    localStorage.removeItem(SETTINGS_KEY);
  };

  // Persist sessionId and autoRecall changes
  useEffect(() => {
    try {
      if (sessionId) {
        localStorage.setItem(SESSION_KEY, sessionId);
      } else {
        localStorage.removeItem(SESSION_KEY);
      }
    } catch (error) {
      logger.storageError('persist sessionId', error, createLogContext('AppContext'));
    }
  }, [sessionId]);

  useEffect(() => {
    try {
      localStorage.setItem(AUTORECALL_KEY, autoRecall.toString());
    } catch (error) {
      logger.storageError('persist autoRecall', error, createLogContext('AppContext'));
    }
  }, [autoRecall]);

  const value: AppContextType = {
    config,
    isLoading,
    error,
    personas: config?.personas || [],
    domains: config?.domains || [],
    providers: config?.providers || [],
    modes: config?.modes || [],
    models: config?.models || [],
    settings,
    updateSettings,
    saveSettings,
    resetSettings,
    selectedMembers,
    setSelectedMembers,
    apiKey,
    setApiKey,
    sessionId,
    setSessionId,
    autoRecall,
    setAutoRecall,
    refreshConfig,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
