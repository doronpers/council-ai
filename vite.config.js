import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = fileURLToPath(new URL('.', import.meta.url));

export default defineConfig({
  plugins: [react()],
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
            if (id.includes('react')) {
              return 'react-vendor';
            }
            return 'vendor';
          }
        },
      },
    },
    cssCodeSplit: true,
    minify: 'esbuild',
    sourcemap: false,
    target: 'es2015',
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src/council_ai/webapp/src'),
    },
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
