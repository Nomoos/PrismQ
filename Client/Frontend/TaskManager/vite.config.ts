import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // Bundle analysis - generates stats.html when ANALYZE env var is set
    ...(process.env.ANALYZE ? [visualizer({
      open: false,
      filename: 'dist/stats.html',
      gzipSize: true,
      brotliSize: true,
      template: 'treemap' // Use treemap for better visualization
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
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info'], // Remove specific console methods
      },
      format: {
        comments: false // Remove comments
      }
    },
    // CSS code splitting
    cssCodeSplit: true,
    // Generate source maps for debugging (can be disabled for production)
    sourcemap: false,
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
})
