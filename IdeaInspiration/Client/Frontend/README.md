# PrismQ Web Client - Frontend

Vue 3 web interface for the PrismQ Web Client control panel.

## Overview

The frontend provides an intuitive web interface for discovering, configuring, and running PrismQ modules. It features a modern single-page application (SPA) with real-time log streaming and module management.

## Quick Start

### Prerequisites

- Node.js 18 or higher
- npm 8 or higher

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` to point to your backend:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

### Running the Application

**Development mode (with hot reload):**
```bash
npm run dev
```

The application will start on http://localhost:5173

**Type checking:**
```bash
npm run type-check
```

**Linting:**
```bash
npm run lint
```

**Build for production:**
```bash
npm run build
```

Output will be in `dist/` directory.

## Technology Stack

- **Vue 3** - Progressive JavaScript framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **Vue Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS
- **Vitest** - Unit testing

## Features

- ✅ **Module Dashboard** - Browse all available modules
- ✅ **Search & Filter** - Find modules quickly
- ✅ **Module Launch** - Configure and run modules
- ✅ **Real-Time Logs** - Stream logs via SSE
- ✅ **Configuration Management** - Save and load parameters
- ✅ **Run Monitoring** - Track module execution
- ✅ **Responsive Design** - Works on desktop and tablets

## Project Structure

```
Frontend/
├── src/                     # Source code
│   ├── main.ts             # Application entry point
│   ├── App.vue             # Root component
│   ├── router/             # Vue Router
│   │   └── index.ts        # Route definitions
│   ├── views/              # Page components
│   │   ├── Dashboard.vue       # Main dashboard
│   │   └── RunDetails.vue      # Run details page
│   ├── components/         # Reusable components
│   │   ├── ModuleCard.vue          # Module display card
│   │   ├── ModuleLaunchModal.vue   # Launch dialog
│   │   ├── LogViewer.vue           # Log viewer
│   │   ├── StatusBadge.vue         # Status indicator
│   │   ├── StatCard.vue            # Statistics card
│   │   ├── ParametersView.vue      # Parameter display
│   │   └── ResultsView.vue         # Results display
│   ├── services/           # API service layer
│   │   ├── api.ts          # Axios configuration
│   │   ├── modules.ts      # Module API
│   │   └── runs.ts         # Run API
│   ├── types/              # TypeScript types
│   │   ├── module.ts       # Module types
│   │   └── run.ts          # Run types
│   └── assets/             # Static assets
│       └── main.css        # Global styles
├── public/                 # Public static files
├── tests/                  # Test suite
├── index.html             # HTML template
├── package.json           # Dependencies
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript config
├── tailwind.config.js     # Tailwind config
└── README.md              # This file
```

## Configuration

### Environment Variables

Frontend configuration is in `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

**Important**: Variables must start with `VITE_` to be accessible in code.

### Production Configuration

Create `.env.production` for production builds:

```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

Build with:
```bash
npm run build
```

## Development

### Component Structure

Components use Vue 3 Composition API with TypeScript:

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import type { Module } from '@/types/module';

// Props
interface Props {
  moduleId: string;
}
const props = defineProps<Props>();

// State
const module = ref<Module | null>(null);
const loading = ref(false);

// Computed
const displayName = computed(() => {
  return module.value?.name || 'Unknown';
});

// Methods
async function loadModule() {
  loading.value = true;
  try {
    module.value = await fetchModule(props.moduleId);
  } finally {
    loading.value = false;
  }
}

// Lifecycle
onMounted(() => {
  loadModule();
});
</script>

<template>
  <div class="module-card">
    <h2>{{ displayName }}</h2>
  </div>
</template>

<style scoped>
.module-card {
  @apply border rounded-lg p-4 shadow-sm;
}
</style>
```

### Adding a New Component

1. **Create component file** in `src/components/`
2. **Define TypeScript types** in `src/types/`
3. **Add tests** in `tests/unit/components/`
4. **Import and use** in views or other components

See [../docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md) for detailed development guide.

### Code Style

- Use TypeScript for all code
- Follow Vue 3 Composition API patterns
- Use Tailwind CSS for styling
- Write unit tests for components

### Linting and Formatting

```bash
# Run linter
npm run lint

# Auto-fix issues
npm run lint:fix

# Type check
npm run type-check

# Format code
npm run format
```

## Testing

Run tests with Vitest:

```bash
# All tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage

# Specific test file
npm test -- ModuleCard.spec.ts
```

### Writing Tests

```typescript
// tests/unit/components/ModuleCard.spec.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import ModuleCard from '@/components/ModuleCard.vue';

describe('ModuleCard', () => {
  it('renders module name', () => {
    const wrapper = mount(ModuleCard, {
      props: {
        module: {
          id: 'test',
          name: 'Test Module',
          description: 'Test',
          category: 'Test',
          scriptPath: '/test.py',
          parameters: [],
          tags: []
        }
      }
    });
    
    expect(wrapper.text()).toContain('Test Module');
  });
});
```

## Routes

The application uses Vue Router with the following routes:

- `/` - Dashboard (module catalog)
- `/runs/:runId` - Run details page

Add new routes in `src/router/index.ts`.

## API Integration

The frontend communicates with the backend via REST API.

### API Service

```typescript
// src/services/modules.ts
import api from './api';
import type { Module } from '@/types/module';

export async function getModules(): Promise<Module[]> {
  const response = await api.get('/api/modules');
  return response.data.modules;
}

export async function getModule(moduleId: string): Promise<Module> {
  const response = await api.get(`/api/modules/${moduleId}`);
  return response.data;
}
```

### Using Services in Components

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getModules } from '@/services/modules';
import type { Module } from '@/types/module';

const modules = ref<Module[]>([]);

onMounted(async () => {
  modules.value = await getModules();
});
</script>
```

## Real-Time Features

### Log Streaming (SSE)

The application uses Server-Sent Events for real-time log streaming:

```typescript
// src/services/runs.ts
export function streamLogs(runId: string, onLog: (log: LogEntry) => void) {
  const eventSource = new EventSource(
    `${API_BASE_URL}/api/runs/${runId}/logs/stream`
  );
  
  eventSource.addEventListener('log', (event) => {
    const log = JSON.parse(event.data);
    onLog(log);
  });
  
  eventSource.addEventListener('complete', () => {
    eventSource.close();
  });
  
  return () => eventSource.close();
}
```

## Styling

The application uses Tailwind CSS for styling.

### Tailwind Configuration

Configure in `tailwind.config.js`:

```javascript
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#8b5cf6',
      }
    },
  },
  plugins: [],
}
```

### Using Tailwind

```vue
<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold text-gray-900">
      Dashboard
    </h1>
    <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
      Click Me
    </button>
  </div>
</template>
```

## Build and Deployment

### Development Build

```bash
npm run dev
```

Runs on http://localhost:5173 with hot module replacement.

### Production Build

```bash
npm run build
```

Outputs to `dist/`:
```
dist/
├── index.html
├── assets/
│   ├── index-[hash].js
│   └── index-[hash].css
└── ...
```

### Preview Production Build

```bash
npm run preview
```

### Deployment

Serve the `dist/` directory with any static file server:

- **nginx**: Configure as static file server
- **Apache**: Use with mod_rewrite
- **Vercel/Netlify**: Deploy directly from Git

## Troubleshooting

### Frontend Won't Start

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port in Use

```bash
# Use different port
npm run dev -- --port 3000
```

Update backend CORS:
```env
# Backend/.env
CORS_ORIGINS=http://localhost:3000
```

### Can't Connect to Backend

1. Verify backend is running: http://localhost:8000/health
2. Check `VITE_API_BASE_URL` in `.env`
3. Check backend CORS configuration
4. Restart frontend after `.env` changes

See [../docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) for more help.

## Documentation

- [Setup Guide](../docs/SETUP.md) - Installation and configuration
- [User Guide](../docs/USER_GUIDE.md) - Using the interface
- [Development Guide](../docs/DEVELOPMENT.md) - Contributing guide
- [Architecture](../docs/ARCHITECTURE.md) - System architecture

## Browser Support

- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

## License

All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

For issues and questions:
- Check [Troubleshooting Guide](../docs/TROUBLESHOOTING.md)
- Open GitHub issue: https://github.com/Nomoos/PrismQ.IdeaInspiration/issues

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-31  
**Maintained by**: PrismQ Development Team
