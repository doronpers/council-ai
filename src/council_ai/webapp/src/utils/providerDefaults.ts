import { logger } from '../utils/logger';

/**
 * Detect which providers have API keys configured
 * Checks environment variables and localStorage
 */
export const detectAvailableProviders = (): {
  openai: boolean;
  anthropic: boolean;
  google: boolean;
  huggingface: boolean;
  groq: boolean;
} => {
  const providers = {
    openai: false,
    anthropic: false,
    google: false,
    huggingface: false,
    groq: false,
  };

  try {
    // Check environment variables (available during build/server)
    if (import.meta.env.VITE_OPENAI_API_KEY) {
      providers.openai = true;
    }
    if (import.meta.env.VITE_ANTHROPIC_API_KEY) {
      providers.anthropic = true;
    }
    if (import.meta.env.VITE_GOOGLE_API_KEY) {
      providers.google = true;
    }
    if (import.meta.env.VITE_HUGGINGFACE_API_KEY) {
      providers.huggingface = true;
    }
    if (import.meta.env.VITE_GROQ_API_KEY) {
      providers.groq = true;
    }

    // Check localStorage for user-configured keys
    const keys = ['openai_key', 'anthropic_key', 'google_key', 'huggingface_key', 'groq_key'];
    keys.forEach((key) => {
      try {
        const stored = localStorage.getItem(key);
        if (stored && stored.trim() && stored !== 'your-api-key-here') {
          const providerName = key.split('_')[0] as keyof typeof providers;
          if (providerName in providers) {
            providers[providerName] = true;
          }
        }
      } catch (err) {
        logger.warn(
          `Error checking localStorage key ${key}`,
          err instanceof Error ? err : undefined
        );
      }
    });

    logger.info('Available providers detected', {
      providers: Object.entries(providers)
        .filter(([, available]) => available)
        .map(([name]) => name),
    });

    return providers;
  } catch (error) {
    logger.warn('Error detecting available providers', error instanceof Error ? error : undefined);
    return providers;
  }
};

/**
 * Get smart default provider based on availability
 * Preference order: OpenAI > Anthropic > Google > Groq > HuggingFace
 */
export const getSmartDefaultProvider = (): string => {
  const available = detectAvailableProviders();

  const preferenceOrder = ['openai', 'anthropic', 'google', 'groq', 'huggingface'] as const;
  for (const provider of preferenceOrder) {
    if (available[provider]) {
      logger.info(`Smart default provider selected: ${provider}`);
      return provider;
    }
  }

  logger.warn('No providers detected - defaulting to openai');
  return 'openai';
};

/**
 * Get available provider list for UI dropdown
 */
export const getAvailableProvidersForUI = (): Array<{
  id: string;
  label: string;
  available: boolean;
}> => {
  const available = detectAvailableProviders();

  return [
    { id: 'openai', label: 'OpenAI', available: available.openai },
    { id: 'anthropic', label: 'Anthropic', available: available.anthropic },
    { id: 'google', label: 'Google', available: available.google },
    { id: 'groq', label: 'Groq', available: available.groq },
    { id: 'huggingface', label: 'HuggingFace', available: available.huggingface },
  ];
};
