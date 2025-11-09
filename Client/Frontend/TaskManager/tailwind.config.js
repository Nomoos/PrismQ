/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Enable dark mode via class strategy
  theme: {
    extend: {
      // Mobile-first breakpoints
      screens: {
        'xs': '360px',
        'sm': '428px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
      },
      // Touch-friendly spacing
      spacing: {
        'touch': '44px',  // Minimum touch target
      },
      // Mobile-optimized colors (Light mode)
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#b9e6fe',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
        },
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
        },
        info: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        // Dark mode colors (GitHub-inspired)
        dark: {
          canvas: {
            default: '#0d1117',
            overlay: '#161b22',
            inset: '#010409',
            subtle: '#161b22',
          },
          surface: {
            default: '#161b22',
            overlay: '#1c2128',
            inset: '#0d1117',
          },
          border: {
            default: '#30363d',
            muted: '#21262d',
            subtle: '#1c2128',
            strong: '#6e7681',
          },
          text: {
            primary: '#e6edf3',
            secondary: '#8d96a0',
            tertiary: '#6e7681',
            placeholder: '#484f58',
            disabled: '#484f58',
            inverse: '#0d1117',
            link: '#58a6ff',
          },
          primary: {
            text: '#58a6ff',
            bg: '#1f6feb',
            border: '#388bfd',
            hover: '#388bfd',
            active: '#1f6feb',
            subtle: '#0d419d',
          },
          success: {
            text: '#3fb950',
            bg: '#238636',
            border: '#2ea043',
            subtle: '#0d3818',
            muted: '#1a7f37',
          },
          warning: {
            text: '#d29922',
            bg: '#9e6a03',
            border: '#bb8009',
            subtle: '#341a03',
            muted: '#7d5a05',
          },
          error: {
            text: '#ff7b72',
            bg: '#da3633',
            border: '#f85149',
            subtle: '#490b08',
            muted: '#b62324',
          },
          info: {
            text: '#58a6ff',
            bg: '#1f6feb',
            border: '#388bfd',
            subtle: '#0d419d',
            muted: '#1158c7',
          },
          accent: {
            text: '#d2a8ff',
            bg: '#8957e5',
            border: '#a371f7',
            subtle: '#271052',
          },
          neutral: {
            text: '#8d96a0',
            bg: '#21262d',
            border: '#30363d',
            subtle: '#161b22',
          },
        },
        // AMOLED mode (optional true black)
        amoled: {
          canvas: '#000000',
          surface: '#0a0a0a',
          border: '#1a1a1a',
        },
      },
    },
  },
  plugins: [],
}
