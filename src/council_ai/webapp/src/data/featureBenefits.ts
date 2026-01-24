/**
 * Feature Benefits Library - Document benefits of each feature
 */

export interface FeatureBenefit {
  id: string;
  name: string;
  icon: string;
  description: string;
  useCases: string[];
  documentationUrl?: string;
  badge?: 'new' | 'popular';
}

export const featureBenefits: Record<string, FeatureBenefit> = {
  comparison: {
    id: 'comparison',
    name: 'Consultation Comparison',
    icon: '⚖️',
    description:
      'Compare two consultations side-by-side to see how different approaches, personas, or contexts affect the advice you receive.',
    useCases: [
      'Compare advice from different consultation modes (synthesis vs debate)',
      'See how different persona combinations affect outcomes',
      'Evaluate how context changes influence recommendations',
      'Track how your questions evolve over time',
    ],
    documentationUrl: '/README.md#consultation-modes',
  },

  tts: {
    id: 'tts',
    name: 'Text-to-Speech',
    icon: '🔊',
    description:
      'Hear your consultation synthesis read aloud. Perfect for listening while working on other tasks or for accessibility.',
    useCases: [
      'Listen to consultations while multitasking',
      'Accessibility for users with visual impairments',
      'Review consultations during commutes or walks',
      'Share audio versions with team members',
    ],
    documentationUrl: '/README.md#text-to-speech-tts-integration',
  },

  patternCoach: {
    id: 'pattern-coach',
    name: 'Pattern Coach Mode',
    icon: '🎯',
    description:
      'Get advice enhanced with relevant software design patterns from the pattern library. Automatically suggests patterns based on your question.',
    useCases: [
      'Code reviews with pattern-based recommendations',
      'Architecture decisions informed by design patterns',
      'Refactoring guidance using proven patterns',
      'Learning design patterns through practical application',
    ],
    documentationUrl:
      'https://github.com/doronpers/shared-ai-utils/blob/main/README.md#pattern-library',
    badge: 'new',
  },

  webSearch: {
    id: 'web-search',
    name: 'Web Search Integration',
    icon: '🌐',
    description:
      'Enable web search to get current information during consultations. Perfect for questions about recent events, news, or up-to-date facts.',
    useCases: [
      'Questions about current events or news',
      'Research on recent developments',
      'Fact-checking and verification',
      'Getting latest information on topics',
    ],
    documentationUrl: '/documentation/WEB_SEARCH_AND_REASONING.md',
  },

  reasoning: {
    id: 'reasoning',
    name: 'Extended Reasoning Modes',
    icon: '🧠',
    description:
      'Enable deeper analysis with extended thinking modes. Chain-of-thought, tree-of-thought, and analytical reasoning for complex problems.',
    useCases: [
      'Complex problem-solving requiring deep analysis',
      'Strategic planning with multiple considerations',
      'Technical decisions with trade-offs',
      'Creative problem-solving with multiple approaches',
    ],
    documentationUrl: '/documentation/WEB_SEARCH_AND_REASONING.md#reasoning-modes',
  },

  history: {
    id: 'history',
    name: 'Consultation History',
    icon: '📚',
    description:
      'Search, filter, and manage your consultation history. Tag consultations, add notes, and export results for documentation.',
    useCases: [
      'Track consultation history over time',
      'Search past consultations by keyword',
      'Filter by domain, mode, or date range',
      'Export consultations for documentation or sharing',
    ],
    documentationUrl: '/README.md#session--history-management',
  },

  sessions: {
    id: 'sessions',
    name: 'Session Management',
    icon: '💬',
    description:
      'Organize consultations into sessions for better context and continuity. Sessions maintain conversation history across multiple consultations.',
    useCases: [
      'Multi-part consultations on related topics',
      'Maintaining context across related questions',
      'Organizing consultations by project or topic',
      'Tracking conversation threads',
    ],
    documentationUrl: '/README.md#session--history-management',
  },
};

/**
 * Get feature benefit by ID
 */
export function getFeatureBenefit(featureId: string): FeatureBenefit | null {
  return featureBenefits[featureId] || null;
}

/**
 * Get all feature benefits
 */
export function getAllFeatureBenefits(): FeatureBenefit[] {
  return Object.values(featureBenefits);
}

/**
 * Get features by category
 */
export function getFeaturesByCategory(category: 'new' | 'popular'): FeatureBenefit[] {
  return Object.values(featureBenefits).filter((feature) => feature.badge === category);
}
