import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import path from 'node:path'

const frontendDir = fileURLToPath(new URL('.', import.meta.url))

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      // Explicitly alias test utilities to ensure they can be resolved from _meta directory
      '@vue/test-utils': path.resolve(frontendDir, 'node_modules/@vue/test-utils'),
      'pinia': path.resolve(frontendDir, 'node_modules/pinia')
    }
  },
  server: {
    fs: {
      allow: ['..']
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    include: ['_meta/tests/unit/**/*.spec.ts'],
    exclude: ['_meta/tests/e2e/**/*'],
    root: frontendDir,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        '_meta/tests/',
        '*.config.{js,ts}',
        'dist/'
      ]
    }
  }
})
