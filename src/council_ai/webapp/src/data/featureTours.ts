/**
 * Feature Tours Data - Step-by-step tour definitions
 */
import type { TourStep } from '../components/Features/FeatureTour';

export interface FeatureTour {
  id: string;
  name: string;
  description: string;
  steps: TourStep[];
}

export const featureTours: Record<string, FeatureTour> = {
  gettingStarted: {
    id: 'getting-started',
    name: 'Getting Started',
    description: 'Learn the basics of using Council AI',
    steps: [
      {
        target: '#query',
        title: 'Enter Your Question',
        content:
          'Type your question or topic here. The council will provide diverse perspectives and a synthesized summary.',
        position: 'bottom',
      },
      {
        target: '#domain',
        title: 'Choose a Domain',
        content:
          'Select a domain that matches your use case. This pre-selects recommended personas for that type of consultation.',
        position: 'bottom',
      },
      {
        target: '#submit',
        title: 'Consult the Council',
        content:
          "Click here to submit your question. You'll see individual responses from each persona and a synthesized summary.",
        position: 'top',
      },
    ],
  },

  advancedFeatures: {
    id: 'advanced-features',
    name: 'Advanced Features',
    description: 'Discover powerful features like comparison, TTS, and pattern-coach',
    steps: [
      {
        target: '.history-item-compare-btn',
        title: 'Compare Consultations',
        content:
          'Click the compare button on any history item to compare two consultations side-by-side. Select a second item to view the comparison.',
        position: 'left',
      },
      {
        target: '.results-tts-toggle',
        title: 'Text-to-Speech',
        content:
          'Enable TTS to hear the synthesis read aloud. Great for listening while working on other tasks.',
        position: 'bottom',
      },
      {
        target: '#mode',
        title: 'Consultation Modes',
        content:
          'Try different modes: synthesis (default), debate, vote, or pattern-coach for design pattern guidance.',
        position: 'bottom',
      },
    ],
  },

  configuration: {
    id: 'configuration',
    name: 'Configuration Guide',
    description: 'Learn how to configure providers, API keys, and settings',
    steps: [
      {
        target: '#provider',
        title: 'Choose Provider',
        content:
          'Select your LLM provider. LM Studio is free and local. Cloud providers require API keys.',
        position: 'bottom',
      },
      {
        target: '#api_key',
        title: 'API Key (Optional)',
        content:
          'Enter your API key here for cloud providers. Keys are session-only and never saved. You can also use environment variables.',
        position: 'bottom',
      },
      {
        target: '#base_url',
        title: 'Base URL (For Local LLMs)',
        content:
          'For LM Studio or Ollama, set the base URL (e.g., http://localhost:1234/v1). Leave empty for cloud provider defaults.',
        position: 'bottom',
      },
    ],
  },

  historyManagement: {
    id: 'history-management',
    name: 'History Management',
    description: 'Learn how to search, filter, and manage your consultation history',
    steps: [
      {
        target: '.history-search-input',
        title: 'Search History',
        content:
          'Use Ctrl/Cmd+K to focus search, or type here to search across all your consultations.',
        position: 'bottom',
      },
      {
        target: '.history-filters-header',
        title: 'Filter Consultations',
        content:
          'Click here to filter by date range, domain, or consultation mode. Useful for finding specific consultations.',
        position: 'bottom',
      },
      {
        target: '.history-item',
        title: 'Manage Consultations',
        content:
          'Each history item supports viewing details, comparing with others, editing tags/notes, and deleting.',
        position: 'right',
      },
    ],
  },
};

/**
 * Get tour by ID
 */
export function getTour(tourId: string): FeatureTour | null {
  return featureTours[tourId] || null;
}

/**
 * Check if tour has been completed
 */
export function isTourCompleted(tourId: string): boolean {
  try {
    const completedTours = JSON.parse(localStorage.getItem('council-completed-tours') || '[]');
    return completedTours.includes(tourId);
  } catch {
    return false;
  }
}

/**
 * Get available tours
 */
export function getAvailableTours(): FeatureTour[] {
  return Object.values(featureTours);
}
