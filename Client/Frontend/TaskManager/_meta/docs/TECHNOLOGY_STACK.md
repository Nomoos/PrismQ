# Frontend/TaskManager - Technology Stack

**Last Updated**: 2025-11-11

## Core Framework

- **Framework**: Vue 3.4+ (Composition API)
- **Language**: TypeScript 5.0+ (strict mode)
- **Build Tool**: Vite 5.0+

## Styling

- **CSS Framework**: Tailwind CSS 3.4+
- **Approach**: Mobile-first utilities
- **Custom Styles**: CSS Modules + scoped styles

## State Management

- **Library**: Pinia 2.1+
- **Stores**: 
  - Tasks store (task management)
  - Worker store (worker state)
  - Auth store (authentication - future)

## Routing

- **Library**: Vue Router 4.2+
- **Mode**: HTML5 History mode
- **Structure**: Route-based code splitting

## HTTP & API

- **HTTP Client**: Axios
- **API Integration**: RESTful API client
- **Backend**: Backend/TaskManager REST API

## Testing

- **Unit Testing**: Vitest
- **E2E Testing**: Playwright
- **Coverage**: 97% pass rate (627 tests)

## Development Tools

- **TypeScript**: Static type checking
- **ESLint**: Code linting
- **Prettier**: Code formatting (configured via ESLint)

## Build & Deployment

- **Bundler**: Vite (Rollup-based)
- **Output**: Static files (HTML, CSS, JS)
- **Deployment**: PHP scripts for Vedos/Wedos hosting

## Performance Optimization

- **Code Splitting**: Route-based lazy loading
- **Tree Shaking**: Automatic unused code removal
- **Minification**: CSS and JS minification
- **Compression**: Gzip compression on server
- **Bundle Analysis**: Built-in bundle analyzer

## Accessibility

- **Standard**: WCAG 2.1 AA compliant
- **Tools**: 
  - Lighthouse auditing
  - Axe accessibility testing
  - Manual keyboard navigation testing

## Browser Support

### Desktop
- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)

### Mobile (Primary Target)
- Chrome Android (latest 2 versions)
- Safari iOS (latest 2 versions)

## Mobile-First Target

**Primary Device**: Redmi 24115RA8EG
- **Display**: 6.7" AMOLED, 2712x1220 (1.5K)
- **Viewport**: 360-428px (CSS pixels)
- **Touch Targets**: 44x44px minimum

## Dependencies Overview

### Production Dependencies
- `vue` - Core framework
- `vue-router` - Routing
- `pinia` - State management
- `axios` - HTTP client
- `dompurify` - XSS protection

### Development Dependencies
- `vite` - Build tool
- `vitest` - Unit testing
- `@playwright/test` - E2E testing
- `typescript` - Type checking
- `vue-tsc` - Vue TypeScript compiler
- `tailwindcss` - CSS framework
- `postcss` - CSS processing
- `autoprefixer` - CSS vendor prefixes

## Package Versions

See [`package.json`](../../package.json) for exact version numbers.

## Upgrade Policy

- **Major versions**: Evaluate before upgrading
- **Minor versions**: Safe to upgrade (follow semver)
- **Patch versions**: Apply security updates promptly

## Performance Targets

- **Bundle Size**: < 500KB initial JavaScript
- **Initial Load**: < 3s on 3G
- **Time to Interactive**: < 5s
- **First Contentful Paint**: < 2s
- **Lighthouse Score**: > 90

## Current Performance

- **Bundle Size**: 236KB (53% under budget)
- **Lighthouse Score**: 99-100/100
- **Load Time (3G)**: 1.5-2.1s
- **All targets**: ✅ Met or exceeded

## Related Documentation

- [Quick Start Guide](./QUICK_START.md)
- [Performance Guide](./PERFORMANCE.md)
- [API Integration](./API_INTEGRATION.md)
- [Testing Guide](./TESTING.md)
