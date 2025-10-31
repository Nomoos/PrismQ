# PrismQ Web Client - Frontend

Vue 3 frontend for the PrismQ Web Client control panel.

## Overview

This frontend provides a modern web interface for discovering, configuring, and running PrismQ data collection modules. It features:

- **Module Discovery**: Browse available PrismQ modules
- **Module Launch**: Configure and start module runs
- **Real-time Updates**: Monitor execution status
- **Responsive Design**: Works on desktop and mobile

## Technology Stack

- **Framework**: Vue 3 with Composition API
- **Language**: TypeScript
- **Build Tool**: Vite 6
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **Routing**: Vue Router 4
- **HTTP Client**: Axios

## Quick Start

### Prerequisites

- Node.js 18+ or higher
- npm package manager

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running the Application

**Development mode** (with hot reload):
```bash
npm run dev
```

The application will be available at http://localhost:5173

**Production build**:
```bash
npm run build
```

**Preview production build**:
```bash
npm run preview
```

## Project Structure

```
Frontend/
├── src/
│   ├── main.ts              # Application entry point
│   ├── App.vue              # Root component
│   ├── router/              # Vue Router configuration
│   │   └── index.ts
│   ├── components/          # Reusable Vue components
│   │   └── ModuleCard.vue
│   ├── views/               # Page components
│   │   └── Dashboard.vue
│   ├── services/            # API service layer
│   │   ├── api.ts
│   │   ├── modules.ts
│   │   └── runs.ts
│   ├── types/               # TypeScript type definitions
│   │   ├── module.ts
│   │   └── run.ts
│   └── assets/              # Static assets
│       └── main.css
├── public/                  # Public static files
├── index.html               # HTML template
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

## Configuration

### Environment Variables

Create a `.env` file (or copy from `.env.example`):

```env
VITE_API_BASE_URL=http://localhost:8000
```

- `VITE_API_BASE_URL` - Backend API base URL

### Backend Integration

The frontend is configured to proxy API requests to the backend during development:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## Development

### Code Style

- Use TypeScript for type safety
- Follow Vue 3 Composition API patterns
- Use Tailwind CSS utility classes
- Write clear, self-documenting code

### Adding New Features

1. Create components in `src/components/`
2. Define types in `src/types/`
3. Add services in `src/services/`
4. Create views in `src/views/`
5. Update router in `src/router/`

### Testing

### Running Tests

**Run all tests:**
```bash
npm test
```

**Run tests in watch mode:**
```bash
npm test -- --watch
```

**Run tests with UI:**
```bash
npm run test:ui
```

**Generate coverage report:**
```bash
npm run coverage
```

### Test Structure

Tests are located in `tests/unit/`:
- `types.spec.ts` - TypeScript type validation tests
- `services.spec.ts` - API service layer tests
- `ModuleCard.spec.ts` - Component tests

**Test Coverage:**
- ✅ Type definitions (Module, Run, parameters)
- ✅ API service methods (list modules, get module, error handling)
- ✅ ModuleCard component (rendering, events, states)
- ✅ All tests passing (18/18)

## Building for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

## Features

### Dashboard

- Lists all available modules
- Shows module information (name, category, description)
- Displays parameter count
- Launch button for each module

### Module Cards

- Clean, card-based UI
- Hover effects
- Disabled state for inactive modules
- One-click launch with default parameters

## API Integration

The frontend communicates with the Backend API:

- **GET /api/modules** - List all modules
- **GET /api/modules/{id}** - Get module details
- **POST /api/runs** - Start a module run
- **GET /api/runs** - List all runs
- **GET /api/runs/{id}** - Get run details

## License

Proprietary - Copyright (c) 2025 PrismQ
