import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { visualizer } from 'rollup-plugin-visualizer'
import { sentryVitePlugin } from '@sentry/vite-plugin'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')
  
  // Check if Sentry is enabled
  const sentryEnabled = env.VITE_SENTRY_ENABLED !== 'false' && !!env.VITE_SENTRY_DSN
  const enableSourceMaps = sentryEnabled || mode !== 'production'
  
  return {
    plugins: [
      vue(),
      // Bundle analysis - generates stats.html when ANALYZE env var is set
      ...(process.env.ANALYZE ? [visualizer({
        open: false,
        filename: 'dist/stats.html',
        gzipSize: true,
        brotliSize: true,
        template: 'treemap' // Use treemap for better visualization
      })] : []),
      // Sentry plugin for source map upload (production builds only)
      ...(sentryEnabled && mode === 'production' && env.SENTRY_AUTH_TOKEN ? [sentryVitePlugin({
        org: env.VITE_SENTRY_ORG,
        project: env.VITE_SENTRY_PROJECT,
        authToken: env.SENTRY_AUTH_TOKEN,
        // Automatically inject release information
        release: {
          name: env.VITE_SENTRY_RELEASE || 'frontend-taskmanager@unknown',
        },
        sourcemaps: {
          assets: './dist/assets/**',
          ignore: ['node_modules'],
        },
        // Only upload source maps, don't include them in the build
        telemetry: false,
      })] : [])
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    build: {
      target: 'es2015',
      // Performance budgets
      chunkSizeWarningLimit: 500,
      // Minification settings for better tree shaking
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: mode === 'production', // Remove console.log in production
          drop_debugger: true,
          pure_funcs: mode === 'production' ? ['console.log', 'console.info'] : [], // Remove specific console methods
        },
        format: {
          comments: false // Remove comments
        }
      },
      // CSS code splitting
      cssCodeSplit: true,
      // Generate source maps for debugging (enabled for Sentry)
      sourcemap: enableSourceMaps ? 'hidden' : false,
      rollupOptions: {
        output: {
          manualChunks(id) {
            // Split vendor chunks
            if (id.includes('node_modules')) {
              if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
                return 'vue-vendor';
              }
              if (id.includes('axios')) {
                return 'axios-vendor';
              }
              if (id.includes('@sentry')) {
                return 'sentry-vendor';
              }
            }
          },
          // Optimize chunk file names
          chunkFileNames: 'assets/[name]-[hash].js',
          entryFileNames: 'assets/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash].[ext]'
        }
      }
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true
        }
      }
    }
  }
})
