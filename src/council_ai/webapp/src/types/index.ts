/**
 * Council AI - Type Definitions
 */

// Persona types
export interface PersonaTrait {
  name: string;
  description: string;
  weight: number;
}

export interface Persona {
  id: string;
  name: string;
  title: string;
  emoji: string;
  category:
    | 'advisory'
    | 'adversarial'
    | 'creative'
    | 'analytical'
    | 'strategic'
    | 'operational'
    | 'specialist'
    | 'red_team'
    | 'custom';
  core_question: string;
  razor: string;
  traits: PersonaTrait[];
  focus_areas: string[];
  weight: number;
  enabled: boolean;
  model?: string;
  model_params?: {
    temperature?: number;
    max_tokens?: number;
  };
}

// Domain types
export interface Domain {
  id: string;
  name: string;
  description?: string;
  default_personas: string[];
}

// Configuration types
export interface AppConfig {
  providers: string[];
  modes: string[];
  domains: Domain[];
  personas: Persona[];
  models: ModelCapability[];
  defaults: {
    provider: string;
    mode: string;
    domain: string;
    base_url?: string;
  };
  tts?: {
    enabled: boolean;
    has_elevenlabs_key: boolean;
    has_openai_key: boolean;
  };
}

export interface ModelCapability {
  provider: string;
  models: string[];
}

// Token usage types
export interface TokenUsage {
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
}

// Settings types (localStorage)
export interface UserSettings {
  provider?: string;
  model?: string;
  base_url?: string;
  domain?: string;
  mode?: string;
  temperature?: number;
  max_tokens?: number;
  enable_tts?: boolean;
  tts_voice?: string;
  members?: string[];
  api_key?: string;
  query?: string;
}

// Consultation types
export interface ConsultationRequest {
  query: string;
  context?: string;
  domain: string;
  members: string[];
  mode: string;
  provider: string;
  model?: string;
  base_url?: string;
  api_key?: string;
  enable_tts: boolean;
  temperature: number;
  max_tokens: number;
  session_id?: string;
  auto_recall?: boolean;
}

export interface MemberResponse {
  persona_id: string;
  persona_name: string;
  persona_emoji: string;
  persona_title: string;
  content: string;
  timestamp: string;
  error?: string;
  provider?: string;
  model?: string;
  usage?: TokenUsage;
}

export interface ConsultationResult {
  query: string;
  context?: string;
  synthesis?: string;
  responses: MemberResponse[];
  mode: string;
  timestamp: string;
  analysis?: ConsultationAnalysis;
  usage_summary?: {
    total_input_tokens: number;
    total_output_tokens: number;
    total_tokens: number;
    estimated_cost?: number;
  };
  tags?: string[];
  session_id?: string;
}

export interface ConsultationAnalysis {
  consensus_score: number;
  key_agreements: string[];
  key_tensions: string[];
  recommendations: string[];
}

// Streaming event types
export type StreamEventType =
  | 'progress'
  | 'response_start'
  | 'thinking_chunk'
  | 'response_chunk'
  | 'response_complete'
  | 'synthesis_start'
  | 'synthesis_chunk'
  | 'synthesis_complete'
  | 'analysis'
  | 'complete'
  | 'error';

export interface StreamEvent {
  type: StreamEventType;
  message?: string;
  persona_id?: string;
  persona_name?: string;
  persona_emoji?: string;
  chunk?: string;
  content?: string;
  synthesis?: string;
  result?: ConsultationResult;
  data?: ConsultationAnalysis;
  error?: string;
  provider?: string;
  model?: string;
  usage?: TokenUsage;
}

// History types
export interface HistoryEntry {
  id: string;
  query: string;
  timestamp: string;
  mode: string;
  member_count: number;
  tags?: string[];
  notes?: string;
  metadata?: Record<string, unknown>;
}

// TTS types
export interface TTSVoice {
  id: string;
  name: string;
  provider: string;
}

// Member status during consultation
export type MemberStatus = 'pending' | 'responding' | 'completed' | 'error';

// Configuration Diagnostics types
export interface ConfigSourceInfo {
  value: unknown;
  source: 'cli' | 'env' | 'file' | 'default';
  overridden: boolean;
}

export interface ConfigIssue {
  type: string;
  message: string;
  severity: 'warning' | 'error';
}

export interface ConfigDiagnosticsResponse {
  config_sources: Record<string, ConfigSourceInfo>;
  warnings: ConfigIssue[];
  errors: ConfigIssue[];
}

export interface MemberStatusInfo {
  id: string;
  name: string;
  emoji: string;
  status: MemberStatus;
}
