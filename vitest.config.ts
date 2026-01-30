import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = fileURLToPath(new URL('.', import.meta.url));

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/council_ai/webapp/src/__tests__/setup.ts'],
    include: ['src/council_ai/webapp/src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/council_ai/webapp/src/**/*.{ts,tsx}'],
      exclude: [
        'src/council_ai/webapp/src/**/*.test.{ts,tsx}',
        'src/council_ai/webapp/src/**/*.spec.{ts,tsx}',
        'src/council_ai/webapp/src/__tests__/**',
        'src/council_ai/webapp/src/main.tsx',
      ],
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src/council_ai/webapp/src'),
    },
  },
});
