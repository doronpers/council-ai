import { defineConfig } from 'vite';
import { resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = fileURLToPath(new URL('.', import.meta.url));

export default defineConfig({
  root: resolve(__dirname, 'src/council_ai/webapp'),
  build: {
    outDir: resolve(__dirname, 'src/council_ai/webapp/static'),
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(__dirname, 'src/council_ai/webapp/index.html'),
      output: {
        manualChunks: (id) => {
          // Split vendor chunks
          if (id.includes('node_modules')) {
            return 'vendor';
          }
          // Split core utilities
          if (id.includes('/core/')) {
            return 'core';
          }
          // Split UI components
          if (id.includes('/ui/')) {
            return 'ui';
          }
          // Split lazy-loaded modules
          if (id.includes('/lazy/')) {
            return 'lazy';
          }
        },
      },
    },
    cssCodeSplit: true,
    minify: 'esbuild', // Use esbuild (included with Vite) instead of terser
    sourcemap: false,
    target: 'es2015',
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/manifest.json': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
