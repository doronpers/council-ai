/**
 * Query Templates Library - Example queries by domain and use case
 */

export interface QueryTemplate {
  title: string;
  query: string;
  context?: string;
}

export const queryTemplates: Record<string, QueryTemplate[]> = {
  coding: [
    {
      title: 'Code Review',
      query: 'Review this API design: POST /users creates a new user. What issues do you see?',
    },
    {
      title: 'Architecture Decision',
      query: 'Should we use microservices or a monolith for our new feature?',
      context: 'Team: 5 developers, expected to scale to 20+',
    },
    {
      title: 'Refactoring Advice',
      query: 'This function is 200 lines long. How should I refactor it?',
    },
    {
      title: 'Technology Choice',
      query: 'Should we use React or Vue for our new frontend?',
    },
  ],

  business: [
    {
      title: 'Market Strategy',
      query: 'A competitor just raised $50M. Should we raise funding too?',
      context: 'Company: B2B SaaS, $2M ARR, 15 people',
    },
    {
      title: 'Pricing Decision',
      query: 'Should we increase our pricing by 20%?',
    },
    {
      title: 'Expansion Planning',
      query: 'Should we enter the European market?',
      context: 'Currently US-only, considering UK expansion',
    },
  ],

  startup: [
    {
      title: 'Runway Decision',
      query: 'We have 18 months runway. Should we focus on growth or profitability?',
    },
    {
      title: 'Pivot Decision',
      query: "Our current product isn't gaining traction. Should we pivot?",
    },
    {
      title: 'Hiring Strategy',
      query: 'Should we hire a CTO or keep building ourselves?',
    },
  ],

  product: [
    {
      title: 'Feature Prioritization',
      query: 'Users say the app is too complex. How should we simplify?',
    },
    {
      title: 'UX Improvement',
      query: 'Our onboarding has 40% drop-off. What should we change?',
    },
    {
      title: 'Product Strategy',
      query: 'Should we build this feature ourselves or use a third-party solution?',
    },
  ],

  career: [
    {
      title: 'Job Offer Decision',
      query: "I've been offered a CTO role at a startup. Should I take it?",
      context: 'Current: Senior engineer at stable company. Offer: 3x equity, 20% salary cut',
    },
    {
      title: 'Career Path',
      query: 'Should I become a manager or stay technical?',
    },
  ],

  creative: [
    {
      title: 'Design Direction',
      query: "I'm designing a podcast intro. What elements should I include?",
    },
    {
      title: 'Content Strategy',
      query: 'How should I structure this blog post for maximum engagement?',
    },
  ],

  general: [
    {
      title: 'General Advice',
      query: 'I need advice on an important decision. What should I consider?',
    },
    {
      title: 'Problem Solving',
      query: "I'm facing a complex problem. How should I approach it?",
    },
  ],

  useCases: [
    {
      title: 'Code Review',
      query: 'Review this code for quality, security, and best practices: [paste code]',
    },
    {
      title: 'Strategic Planning',
      query: 'Help me think through our Q1 strategy. What should we prioritize?',
    },
    {
      title: 'Risk Assessment',
      query: 'What are the hidden risks in this decision?',
    },
    {
      title: 'Design Review',
      query: 'Review this design. Is it as simple as possible?',
    },
  ],
};
