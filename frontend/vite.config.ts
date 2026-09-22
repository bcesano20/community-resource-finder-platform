import path from 'node:path';

import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@/components': path.resolve(import.meta.dirname, './src/components'),
      '@/pages': path.resolve(import.meta.dirname, './src/pages'),
      '@/hooks': path.resolve(import.meta.dirname, './src/hooks'),
      '@/api': path.resolve(import.meta.dirname, './src/apiCalls'),
      '@/apiParsers': path.resolve(import.meta.dirname, './src/apiParsers'),
      '@/types': path.resolve(import.meta.dirname, './src/types'),
      '@/helpers': path.resolve(import.meta.dirname, './src/helpers'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.ts',
  },
});
