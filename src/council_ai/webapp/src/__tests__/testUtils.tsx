/**
 * Test utilities and mock providers for React component testing
 */
import React, { ReactNode } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import type { AppConfig, UserSettings, MemberStatusInfo, ConsultationResult } from '../types';

// Mock App Context
interface MockAppContextValue {
  config: AppConfig | null;
  isLoading: boolean;
  error: string | null;
  personas: AppConfig['personas'];
  domains: AppConfig['domains'];
  providers: string[];
  modes: string[];
  models: AppConfig['models'];
  settings: UserSettings;
  updateSettings: (updates: Partial<UserSettings>) => void;
  saveSettings: () => void;
  resetSettings: () => void;
  selectedMembers: string[];
  setSelectedMembers: React.Dispatch<React.SetStateAction<string[]>>;
  apiKey: string;
  setApiKey: React.Dispatch<React.SetStateAction<string>>;
  sessionId: string | null;
  setSessionId: React.Dispatch<React.SetStateAction<string | null>>;
  autoRecall: boolean;
  setAutoRecall: React.Dispatch<React.SetStateAction<boolean>>;
  refreshConfig: () => Promise<void>;
}

// Mock Consultation Context
interface MockConsultationContextValue {
  isConsulting: boolean;
  setIsConsulting: React.Dispatch<React.SetStateAction<boolean>>;
  query: string;
  setQuery: React.Dispatch<React.SetStateAction<string>>;
  context: string;
  setContext: React.Dispatch<React.SetStateAction<string>>;
  result: ConsultationResult | null;
  setResult: React.Dispatch<React.SetStateAction<ConsultationResult | null>>;
  streamingSynthesis: string;
  setStreamingSynthesis: React.Dispatch<React.SetStateAction<string>>;
  streamingResponses: Map<string, string>;
  streamingThinking: Map<string, string>;
  updateStreamingResponse: (personaId: string, content: string) => void;
  updateStreamingThinking: (personaId: string, content: string) => void;
  clearStreamingState: () => void;
  memberStatuses: MemberStatusInfo[];
  initializeMemberStatuses: (members: MemberStatusInfo[]) => void;
  updateMemberStatus: (personaId: string, status: string) => void;
  abortController: AbortController | null;
  setAbortController: React.Dispatch<React.SetStateAction<AbortController | null>>;
  cancelConsultation: () => void;
  handleStreamEvent: (event: unknown) => void;
  updateSessionFromResult: (result: ConsultationResult) => void;
  statusMessage: string;
  setStatusMessage: React.Dispatch<React.SetStateAction<string>>;
}

// Default mock values
export const defaultMockAppContext: MockAppContextValue = {
  config: {
    personas: [
      { id: 'analyst', name: 'Analyst', emoji: '📊', description: 'Data analyst', background: '' },
      { id: 'critic', name: 'Critic', emoji: '🔍', description: 'Critical reviewer', background: '' },
    ],
    domains: [
      { id: 'general', name: 'General', description: 'General purpose' },
      { id: 'tech', name: 'Technology', description: 'Tech domain' },
    ],
    providers: ['openai', 'anthropic'],
    modes: ['individual', 'synthesis', 'debate'],
    models: [
      { provider: 'openai', model: 'gpt-4', display_name: 'GPT-4', supports_thinking: false },
    ],
    defaults: { provider: 'openai', mode: 'synthesis', domain: 'general' },
    version: '1.0.0',
  },
  isLoading: false,
  error: null,
  personas: [
    { id: 'analyst', name: 'Analyst', emoji: '📊', description: 'Data analyst', background: '' },
    { id: 'critic', name: 'Critic', emoji: '🔍', description: 'Critical reviewer', background: '' },
  ],
  domains: [
    { id: 'general', name: 'General', description: 'General purpose' },
    { id: 'tech', name: 'Technology', description: 'Tech domain' },
  ],
  providers: ['openai', 'anthropic'],
  modes: ['individual', 'synthesis', 'debate'],
  models: [
    { provider: 'openai', model: 'gpt-4', display_name: 'GPT-4', supports_thinking: false },
  ],
  settings: {
    provider: 'openai',
    mode: 'synthesis',
    domain: 'general',
    temperature: 0.7,
    max_tokens: 1000,
    enable_tts: false,
  },
  updateSettings: vi.fn(),
  saveSettings: vi.fn(),
  resetSettings: vi.fn(),
  selectedMembers: [],
  setSelectedMembers: vi.fn(),
  apiKey: '',
  setApiKey: vi.fn(),
  sessionId: null,
  setSessionId: vi.fn(),
  autoRecall: true,
  setAutoRecall: vi.fn(),
  refreshConfig: vi.fn().mockResolvedValue(undefined),
};

export const defaultMockConsultationContext: MockConsultationContextValue = {
  isConsulting: false,
  setIsConsulting: vi.fn(),
  query: '',
  setQuery: vi.fn(),
  context: '',
  setContext: vi.fn(),
  result: null,
  setResult: vi.fn(),
  streamingSynthesis: '',
  setStreamingSynthesis: vi.fn(),
  streamingResponses: new Map(),
  streamingThinking: new Map(),
  updateStreamingResponse: vi.fn(),
  updateStreamingThinking: vi.fn(),
  clearStreamingState: vi.fn(),
  memberStatuses: [],
  initializeMemberStatuses: vi.fn(),
  updateMemberStatus: vi.fn(),
  abortController: null,
  setAbortController: vi.fn(),
  cancelConsultation: vi.fn(),
  handleStreamEvent: vi.fn(),
  updateSessionFromResult: vi.fn(),
  statusMessage: '',
  setStatusMessage: vi.fn(),
};

// Create mock context
const MockAppContext = React.createContext<MockAppContextValue>(defaultMockAppContext);
const MockConsultationContext = React.createContext<MockConsultationContextValue>(defaultMockConsultationContext);

// Mock providers
interface MockProvidersProps {
  children: ReactNode;
  appContext?: Partial<MockAppContextValue>;
  consultationContext?: Partial<MockConsultationContextValue>;
}

export const MockProviders: React.FC<MockProvidersProps> = ({
  children,
  appContext = {},
  consultationContext = {},
}) => {
  const appValue = { ...defaultMockAppContext, ...appContext };
  const consultationValue = { ...defaultMockConsultationContext, ...consultationContext };

  return (
    <MockAppContext.Provider value={appValue}>
      <MockConsultationContext.Provider value={consultationValue}>
        {children}
      </MockConsultationContext.Provider>
    </MockAppContext.Provider>
  );
};

// Custom render function
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  appContext?: Partial<MockAppContextValue>;
  consultationContext?: Partial<MockConsultationContextValue>;
}

export const renderWithProviders = (
  ui: React.ReactElement,
  options: CustomRenderOptions = {}
) => {
  const { appContext, consultationContext, ...renderOptions } = options;

  const Wrapper: React.FC<{ children: ReactNode }> = ({ children }) => (
    <MockProviders appContext={appContext} consultationContext={consultationContext}>
      {children}
    </MockProviders>
  );

  return render(ui, { wrapper: Wrapper, ...renderOptions });
};

// Hook mocks for module mocking
export const createMockUseApp = (overrides: Partial<MockAppContextValue> = {}) => {
  return () => ({ ...defaultMockAppContext, ...overrides });
};

export const createMockUseConsultation = (overrides: Partial<MockConsultationContextValue> = {}) => {
  return () => ({ ...defaultMockConsultationContext, ...overrides });
};

// Export for use in tests
export { MockAppContext, MockConsultationContext };
