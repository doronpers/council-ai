import js from '@eslint/js';
import globals from 'globals';
import prettier from 'eslint-config-prettier';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import compat from 'eslint-plugin-compat';
import security from 'eslint-plugin-security';

export default [
  {
    ignores: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/.next/**',
      '**/.venv/**',
      '**/venv/**',
      '**/__pycache__/**',
      '**/.git/**',
      '**/.github/**',
      '**/Archive/**',
    ],
  },
  js.configs.recommended,
  jsxA11y.flatConfigs.recommended,
  security.configs.recommended,
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    settings: {
      polyfillWrappers: {
        AbortController: 'AbortController',
      },
    },
    rules: {
      'no-console': ['warn'],
      'no-unused-vars': ['error', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
      'security/detect-object-injection': 'warn',
      ...compat.configs.recommended.rules,
    },
    plugins: {
      compat,
    },
  },
  prettier,
];
