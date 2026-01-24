/**
 * Recommendation Utilities - Smart recommendations for domains and personas
 */
import type { Domain, Persona } from '../types';

/**
 * Recommend personas based on query content
 */
export function recommendPersonasForQuery(
  query: string,
  domains: Domain[],
  personas: Persona[]
): Persona[] {
  const queryLower = query.toLowerCase();

  // Keyword-based recommendations
  const keywordMap: Record<string, string[]> = {
    code: ['rams', 'kahneman', 'holman'],
    security: ['holman', 'taleb'],
    design: ['rams', 'kahneman'],
    business: ['grove', 'taleb', 'dempsey'],
    risk: ['taleb', 'grove'],
    strategy: ['grove', 'taleb', 'dempsey'],
    user: ['kahneman', 'treasure'],
    audio: ['treasure'],
    communication: ['treasure'],
  };

  const recommendedIds = new Set<string>();

  // Check for keywords
  for (const [keyword, personaIds] of Object.entries(keywordMap)) {
    if (queryLower.includes(keyword)) {
      personaIds.forEach((id) => recommendedIds.add(id));
    }
  }

  // Domain-based recommendations
  const domain = domains.find((d) => {
    const domainKeywords = d.id.toLowerCase();
    return queryLower.includes(domainKeywords) || queryLower.includes(domain.name.toLowerCase());
  });

  if (domain && domain.default_personas) {
    domain.default_personas.forEach((id) => recommendedIds.add(id));
  }

  // Return recommended personas
  return personas.filter((p) => recommendedIds.has(p.id));
}

/**
 * Recommend personas for a domain
 */
export function recommendPersonasForDomain(domain: Domain, personas: Persona[]): Persona[] {
  if (!domain.default_personas) {
    return [];
  }

  return personas.filter((p) => domain.default_personas.includes(p.id));
}

/**
 * Recommend domain based on query (alias for recommendDomainForQuery)
 */
export function recommendDomain(query: string, domains: Domain[]): Domain | null {
  return recommendDomainForQuery(query, domains);
}

/**
 * Recommend domain based on query
 */
export function recommendDomainForQuery(query: string, domains: Domain[]): Domain | null {
  const queryLower = query.toLowerCase();

  // Keyword-based domain matching
  const domainKeywords: Record<string, string[]> = {
    coding: [
      'code',
      'api',
      'function',
      'class',
      'refactor',
      'bug',
      'test',
      'programming',
      'software',
    ],
    business: [
      'business',
      'revenue',
      'profit',
      'market',
      'customer',
      'sales',
      'strategy',
      'company',
    ],
    startup: ['startup', 'funding', 'runway', 'pivot', 'mvp', 'founder', 'venture'],
    product: ['product', 'feature', 'user', 'ux', 'onboarding', 'retention', 'interface'],
    career: ['job', 'career', 'offer', 'salary', 'promotion', 'resume', 'interview'],
    creative: ['design', 'creative', 'content', 'writing', 'podcast', 'video', 'art'],
  };

  // Find best matching domain
  let bestMatch: Domain | null = null;
  let bestScore = 0;

  for (const domain of domains) {
    const keywords = domainKeywords[domain.id] || [];
    const score = keywords.filter((keyword) => queryLower.includes(keyword)).length;

    if (score > bestScore) {
      bestScore = score;
      bestMatch = domain;
    }
  }

  return bestMatch;
}

/**
 * Get explanation for domain recommendation
 */
export function getRecommendationExplanation(domain: Domain, query: string): string {
  const queryLower = query.toLowerCase();
  const domainKeywords: Record<string, string[]> = {
    coding: ['code', 'api', 'function', 'class', 'refactor', 'bug', 'test'],
    business: ['business', 'revenue', 'profit', 'market', 'customer'],
    startup: ['startup', 'funding', 'runway', 'pivot', 'mvp'],
    product: ['product', 'feature', 'user', 'ux', 'onboarding'],
    career: ['job', 'career', 'offer', 'salary', 'promotion'],
    creative: ['design', 'creative', 'content', 'writing', 'podcast'],
  };

  const keywords = domainKeywords[domain.id] || [];
  const matchedKeywords = keywords.filter((keyword) => queryLower.includes(keyword));

  if (matchedKeywords.length > 0) {
    return `Your query mentions "${matchedKeywords[0]}", which matches the ${domain.name} domain.`;
  }

  return `The ${domain.name} domain is recommended based on your query.`;
}
