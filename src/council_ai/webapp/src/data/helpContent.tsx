/**
 * Help Content Library - Centralized help content for features
 */
import React from 'react';

export interface HelpContent {
  title: string;
  description: string;
  examples?: string[];
  links?: Array<{ label: string; url: string }>;
}

export const HELP_CONTENT: Record<string, HelpContent> = {
  provider: {
    title: 'LLM Provider Selection',
    description:
      'Choose how you want to run consultations. LM Studio is free and local (no API key needed). Cloud providers (Anthropic, OpenAI, Gemini) require API keys but offer more powerful models.',
    examples: [
      'LM Studio: Free, local, private. Set base URL to http://localhost:1234/v1',
      'Anthropic: Claude models, excellent for reasoning and analysis',
      'OpenAI: GPT-4 models, versatile and widely available',
      'Gemini: Google models, good for general purpose tasks',
    ],
    links: [
      { label: 'LM Studio Download', url: 'https://lmstudio.ai' },
      { label: 'Provider Documentation', url: '/documentation/WEB_SEARCH_AND_REASONING.md' },
    ],
  },

  domain: {
    title: 'Domain Selection',
    description:
      'Domains pre-configure your council with recommended personas and settings for specific use cases. Each domain includes personas best suited for that type of consultation.',
    examples: [
      'coding: Software development, code reviews, architecture decisions',
      'business: Business strategy, market analysis, competitive strategy',
      'startup: Early-stage decisions, fundraising, product-market fit',
      'product: Product management, feature prioritization, UX decisions',
    ],
    links: [{ label: 'Domain Documentation', url: '/documentation/PERSONAS_AND_DOMAINS.md' }],
  },

  baseUrl: {
    title: 'Base URL Configuration',
    description:
      'For local LLMs (LM Studio, Ollama) or custom endpoints. Leave empty to use provider defaults.',
    examples: [
      'LM Studio: http://localhost:1234/v1',
      'Ollama: http://localhost:11434/v1',
      'Custom endpoint: https://your-api.example.com/v1',
    ],
    links: [{ label: 'LM Studio Setup', url: '/CODEX_ENV_SETUP.md#lm-studio-configuration' }],
  },

  mode: {
    title: 'Consultation Mode',
    description:
      'Different modes change how personas interact and respond. Synthesis (default) provides individual responses plus a summary. Other modes offer different interaction patterns.',
    examples: [
      'synthesis: Individual responses + synthesized summary (recommended)',
      'individual: Each persona responds separately, no synthesis',
      'sequential: Personas respond in order, seeing previous responses',
      'debate: Multiple rounds of discussion between personas',
      'vote: Personas vote on a decision',
      'pattern_coach: Enhanced synthesis with software design pattern suggestions',
    ],
    links: [{ label: 'Mode Documentation', url: '/README.md#consultation-modes' }],
  },

  persona: {
    title: 'Persona Selection',
    description:
      'Personas are AI advisors with distinct expertise and perspectives. Each persona has a core question they ask and decision principles they follow.',
    examples: [
      'Dieter Rams: "Is this as simple as possible?" - Design and simplification',
      'Daniel Kahneman: "Does this work with human cognition?" - UX and cognitive load',
      'Pablos Holman: "How would I break this?" - Security and exploits',
      'Nassim Taleb: "What\'s the hidden risk?" - Risk and antifragility',
    ],
    links: [
      { label: 'Persona Documentation', url: '/README.md#built-in-personas' },
      { label: 'Create Custom Persona', url: '/README.md#create-custom-personas' },
    ],
  },

  apiKey: {
    title: 'API Key Configuration',
    description:
      'API keys authenticate with cloud LLM providers. Keys entered here are session-only and never saved. You can also set keys via environment variables or .env file.',
    examples: [
      'Session only: Keys entered here are not persisted',
      'Environment variable: Set ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.',
      '.env file: Create .env in project root with your keys',
    ],
    links: [{ label: 'API Key Setup', url: '/README.md#set-your-api-key' }],
  },

  persona: {
    title: 'Persona Selection',
    description:
      'Personas are AI advisors with distinct expertise and perspectives. Each persona has a core question they ask and decision principles they follow.',
    examples: [
      'Dieter Rams: "Is this as simple as possible?" - Design and simplification',
      'Daniel Kahneman: "Does this work with human cognition?" - UX and cognitive load',
      'Pablos Holman: "How would I break this?" - Security and exploits',
      'Nassim Taleb: "What\'s the hidden risk?" - Risk and antifragility',
    ],
    links: [
      { label: 'Persona Documentation', url: '/README.md#built-in-personas' },
      { label: 'Create Custom Persona', url: '/README.md#create-custom-personas' },
    ],
  },
};

/**
 * Get help content for a feature
 */
export function getHelpContent(feature: string): HelpContent | null {
  return HELP_CONTENT[feature] || null;
}

/**
 * Format help content for display in tooltip
 */
export function formatHelpContent(content: HelpContent): React.ReactNode {
  return (
    <div className="help-content">
      <div className="help-content-title">{content.title}</div>
      <div className="help-content-description">{content.description}</div>
      {content.examples && content.examples.length > 0 && (
        <div className="help-content-examples">
          <strong>Examples:</strong>
          <ul>
            {content.examples.map((example, index) => (
              <li key={index}>{example}</li>
            ))}
          </ul>
        </div>
      )}
      {content.links && content.links.length > 0 && (
        <div className="help-content-links">
          {content.links.map((link, index) => (
            <a key={index} href={link.url} target="_blank" rel="noopener noreferrer">
              {link.label} →
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
