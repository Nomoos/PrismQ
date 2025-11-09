import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig, configDefaults } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
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
          'vitest.config.ts'
        ],
        statements: 80,
        branches: 80,
        functions: 80,
        lines: 80
      }
    }
  })
)
