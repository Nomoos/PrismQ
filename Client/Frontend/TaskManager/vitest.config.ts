import { fileURLToPath, URL } from 'node:url'
import { defineConfig, configDefaults } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  test: {
    environment: 'jsdom',
    exclude: [...configDefaults.exclude, 'e2e/**', 'tests/e2e/**', '_meta/tests/**'],
    root: fileURLToPath(new URL('./', import.meta.url)),
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.spec.ts',
        '**/*.test.ts',
        'src/vite-env.d.ts',
        'vite.config.ts',
        'vitest.config.ts',
        'playwright.config.ts',
        'postcss.config.js',
        'tailwind.config.js',
        'lighthouserc.js',
        'scripts/**',
        '*.config.js',
        '*.config.ts'
      ],
      include: ['src/**/*.{ts,vue}'],
      statements: 80,
      branches: 80,
      functions: 80,
      lines: 80
    }
  }
})
