/**
 * Types for the LLM Response Reviewer
 */
export interface ReviewerJusticeInfo {
  id: string;
  name: string;
  title: string;
  emoji: string;
  core_question: string;
  is_default?: boolean;
  is_sonotheia_expert?: boolean;
}

export interface ReviewerInfoResponse {
  version: string;
  default_justices: string[];
  sonotheia_experts: string[];
  available_justices: ReviewerJusticeInfo[];
  default_chair: string;
  default_vice_chair: string;
}

export interface ReviewerResponseInput {
  id: number;
  content: string;
  source?: string | null;
}

export interface ReviewerRequest {
  question: string;
  responses: ReviewerResponseInput[];
  justices: string[];
  chair: string;
  vice_chair: string;
  include_sonotheia_experts: boolean;
  provider?: string | null;
  model?: string | null;
  base_url?: string | null;
  api_key?: string | null;
  temperature: number;
  max_tokens: number;
}

export interface ReviewerJusticeOpinion {
  justice_id: string;
  justice_name: string;
  justice_emoji: string;
  role: 'chair' | 'vice_chair' | 'associate';
  opinion: string;
  vote: 'approve' | 'approve_with_reservations' | 'dissent';
}

export interface ReviewerResponseAssessment {
  response_id: number;
  source?: string | null;
  scores: Record<string, number>;
  overall_score: number;
  justifications: Record<string, string>;
  strengths: string[];
  weaknesses: string[];
  justice_opinions: ReviewerJusticeOpinion[];
}

export interface ReviewerGroupDecision {
  ranking: number[];
  winner: number;
  winner_score: number;
  majority_opinion: string;
  dissenting_opinions: string[];
  vote_breakdown: Record<string, number>;
}

export interface ReviewerSynthesizedResponse {
  combined_best: string;
  refined_final: string;
}

export interface ReviewerResult {
  review_id: string;
  question: string;
  responses_reviewed: number;
  timestamp: string;
  council_composition: { total_justices: number };
  individual_assessments: ReviewerResponseAssessment[];
  group_decision: ReviewerGroupDecision;
  synthesized_response: ReviewerSynthesizedResponse;
  warnings: string[];
}

export interface ReviewerStreamEvent {
  type: string;
  phase?: string;
  result?: ReviewerResult;
  error?: string;
}

export interface GoogleDocsImportRequest {
  url?: string | null;
  content?: string | null;
}

export interface GoogleDocsImportResponse {
  question: string;
  responses: ReviewerResponseInput[];
  success: boolean;
  message?: string | null;
}
