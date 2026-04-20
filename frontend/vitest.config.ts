import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '#imports': fileURLToPath(new URL('./tests/mocks/nuxt-imports.ts', import.meta.url)),
      '@shared': fileURLToPath(new URL('./app/shared', import.meta.url)),
      '@features': fileURLToPath(new URL('./app/features', import.meta.url)),
      '@widgets': fileURLToPath(new URL('./app/widgets', import.meta.url)),
    },
  },
  test: {
    environment: 'happy-dom',
    globals: true,
    include: ['tests/**/*.test.ts'],
    exclude: ['**/node_modules/**', 'tests/e2e/**'],
  },
});
