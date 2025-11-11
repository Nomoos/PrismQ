# Performance Optimization Guide

## Overview

This document describes the performance optimizations implemented for the Frontend/TaskManager application to ensure fast load times on 3G networks and excellent performance on mobile devices.

## Performance Budgets

The application is configured with the following performance budgets:

- **Total JavaScript**: < 500KB (currently ~136KB ✅)
- **Total CSS**: < 50KB (currently ~12KB ✅)
- **Total Assets**: < 1MB (currently ~155KB ✅)
- **Individual Chunks**: < 100KB warning threshold

### Current Performance Metrics

Based on the latest build:
- Total Size: **155.06 KB**
- JavaScript: **136.04 KB** (73% gzip compression)
- CSS: **12.11 KB** (75% gzip compression)
- Other Assets: **6.90 KB**

All budgets are **passing** ✅

## Build Optimizations

### 1. Code Splitting

The application uses Vite's code splitting features to separate vendor code from application code:

- **vue-vendor.js** (~88KB): Vue.js, Vue Router, and Pinia
- **axios-vendor.js** (~38KB): Axios HTTP client
- **Route chunks**: Lazy-loaded page components (< 8KB each)

### 2. Tree Shaking

Tree shaking is enabled by default in Vite to remove unused code:
- Using ES modules for all imports
- Named imports where possible
- Automatic removal of unused exports

### 3. Minification

Production builds use Terser for JavaScript minification with the following settings:
- Console statements removed (`console.log`, `console.info`)
- Debugger statements removed
- Comments removed
- Code optimized and compressed

### 4. CSS Optimization

CSS is optimized using:
- **Tailwind CSS JIT**: Only includes used utility classes
- **cssnano**: Minifies and optimizes CSS in production
- **PostCSS autoprefixer**: Adds vendor prefixes for browser compatibility
- **CSS code splitting**: Enabled for better caching

## Route Lazy Loading

All routes are lazy-loaded using dynamic imports:

```typescript
const routes = [
  {
    path: '/',
    component: () => import('../views/TaskList.vue')
  },
  // ... other routes
]
```

This ensures that users only download the code for the pages they visit.

## Scripts

### Build Scripts

- `npm run build` - Production build with all optimizations
- `npm run build:analyze` - Build with bundle analysis visualization
- `npm run preview` - Preview the production build locally

### Analysis Scripts

- `npm run bundle:size` - Check bundle sizes against budgets
- `npm run bundle:check` - Build and check bundle sizes

## Bundle Analysis

To visualize the bundle composition and identify large dependencies:

```bash
npm run build:analyze
```

This generates `dist/stats.html` with an interactive treemap visualization showing:
- Chunk sizes (parsed, gzipped, brotli)
- Module composition
- Dependency sizes

## Performance Testing

### Manual Testing

1. **Network Throttling**: Test with Chrome DevTools 3G throttling
2. **CPU Throttling**: Test with 6x CPU slowdown
3. **Mobile Device**: Test on actual Redmi 24115RA8EG device
4. **Cache Disabled**: Test with browser cache disabled

### Performance Metrics to Monitor

- **First Contentful Paint (FCP)**: Target < 2s
- **Largest Contentful Paint (LCP)**: Target < 2.5s
- **Time to Interactive (TTI)**: Target < 5s
- **Total Blocking Time (TBT)**: Target < 300ms
- **Cumulative Layout Shift (CLS)**: Target < 0.1

### Lighthouse Testing

Run Lighthouse audits to measure performance:

```bash
# Using Chrome DevTools
# 1. Open DevTools (F12)
# 2. Go to Lighthouse tab
# 3. Select "Mobile" and "Performance"
# 4. Click "Analyze page load"
```

Target: **Lighthouse Performance Score > 90**

## Optimization Checklist

### Build Optimization ✅
- [x] Vite configuration with code splitting
- [x] Manual chunk splitting (vue-vendor, axios-vendor)
- [x] Tree shaking enabled
- [x] Bundle analysis tooling
- [x] CSS optimization (Tailwind JIT, cssnano)
- [x] Minification settings (Terser)
- [x] Performance budgets configured
- [x] Bundle size monitoring scripts

### Asset Optimization (Future)
- [ ] Image optimization (WebP, lazy loading)
- [ ] Icon sprite sheet or inline SVG
- [ ] Font optimization (system fonts, subset)
- [ ] SVG optimization
- [ ] Favicon optimization

### Code Optimization
- [x] Lazy loading routes
- [ ] Dynamic imports for heavy components (if added)
- [ ] Virtual scrolling for long lists (if needed)
- [ ] Debounce/throttle for inputs (if needed)
- [ ] Memoization for expensive computations

### Network Optimization
- [ ] HTTP/2 push (server configuration)
- [ ] Service Worker for caching (future enhancement)
- [ ] API response compression (server configuration)
- [ ] Prefetching critical resources

## Best Practices

### For Developers

1. **Monitor bundle size**: Run `npm run bundle:check` before committing
2. **Use lazy loading**: Import heavy components dynamically
3. **Avoid large dependencies**: Check bundle analysis before adding new packages
4. **Use named imports**: Helps with tree shaking
5. **Test on 3G**: Always test performance on throttled connections

### For Code Reviews

1. Check bundle size reports in CI
2. Review large dependency additions
3. Verify lazy loading for new routes
4. Ensure no performance regressions

## Troubleshooting

### Bundle Size Exceeds Budget

If bundle size exceeds the budget:

1. Run bundle analysis: `npm run build:analyze`
2. Identify large dependencies in `dist/stats.html`
3. Consider alternatives or dynamic imports
4. Update budgets if justified

### Slow Load Times

If load times are slow:

1. Check network tab in DevTools
2. Identify slow-loading resources
3. Consider preloading critical assets
4. Optimize images and large assets
5. Enable compression on server

## Continuous Monitoring

### CI/CD Integration

The bundle size check is integrated into the build process:

```bash
npm run bundle:check
```

This will:
- Build the production bundle
- Analyze all chunks
- Report warnings and errors
- Fail the build if budgets are exceeded

### Future Enhancements

1. **Lighthouse CI**: Automated Lighthouse testing in CI/CD
2. **Performance budgets in CI**: Block PRs that exceed budgets
3. **Real User Monitoring**: Track actual user performance metrics
4. **Core Web Vitals**: Monitor FCP, LCP, FID, CLS
5. **Bundle size trends**: Track bundle size over time

## Resources

- [Vite Performance](https://vitejs.dev/guide/performance.html)
- [Web.dev Performance](https://web.dev/performance/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Core Web Vitals](https://web.dev/vitals/)
- [Bundle Analyzer](https://github.com/btd/rollup-plugin-visualizer)

---

**Last Updated**: 2025-11-09  
**Maintained By**: Worker04 (Mobile Performance Specialist)  
**Status**: Phase 0 Complete

## Phase 1: Runtime Performance Optimizations

### Core Web Vitals Tracking

The application now includes automatic tracking of Core Web Vitals metrics:

- **LCP (Largest Contentful Paint)**: Target < 2.5s
- **FID (First Input Delay)**: Target < 100ms  
- **CLS (Cumulative Layout Shift)**: Target < 0.1
- **FCP (First Contentful Paint)**: Target < 1.8s
- **TTFB (Time to First Byte)**: Target < 0.8s

Metrics are automatically logged in development and can be sent to analytics in production.

### Network Optimizations

#### Request Caching

Implemented intelligent request caching with the following features:

- **In-memory cache** with configurable TTL
- **Stale-while-revalidate**: Returns cached data while fetching fresh data in background
- **Request deduplication**: Prevents multiple identical requests
- **Automatic cleanup**: Removes expired cache entries

Cache configuration:
- Task details: 30 second cache
- Task types: 5 minute cache (rarely changes)
- Automatic invalidation on mutations

#### Performance Utilities

New utility functions for performance optimization:

**Debounce**: Delays function execution until after inactivity
```typescript
import { debounce } from '@/utils/debounce'

const search = debounce((query: string) => {
  taskStore.searchTasks(query)
}, 300)
```

**Throttle**: Limits function execution frequency
```typescript
import { throttle } from '@/utils/debounce'

const handleScroll = throttle(() => {
  // Handle scroll
}, 100)
```

**Request Idle Callback**: Defers non-critical work
```typescript
import { requestIdleCallback } from '@/utils/debounce'

requestIdleCallback(() => {
  // Perform non-critical work
})
```

### Performance Testing

#### Lighthouse CI

Automated performance testing with Lighthouse CI:

```bash
# Run full performance test suite
npm run perf:test

# Run Lighthouse only
npm run lighthouse

# Run Lighthouse in CI mode
npm run lighthouse:ci
```

Configuration includes:
- Mobile device emulation (Redmi specs)
- 3G network throttling
- Performance budget assertions
- Automated scoring

#### Performance Metrics

Track and analyze performance with:

```bash
# Check bundle sizes
npm run bundle:check

# Analyze bundle composition
npm run build:analyze

# Run comprehensive performance tests
node scripts/perf-test.js
```

### Best Practices

#### Code Optimization

1. **Use computed properties** for expensive calculations
2. **Avoid unnecessary re-renders** with proper reactivity
3. **Lazy load routes** (already implemented)
4. **Use v-once** for static content
5. **Implement virtual scrolling** for long lists (when needed)

#### Network Optimization

1. **Cache API responses** appropriately
2. **Batch API requests** when possible
3. **Use stale-while-revalidate** for non-critical data
4. **Prefetch critical resources**

#### Asset Optimization

1. **Optimize images** (WebP format, lazy loading)
2. **Minimize CSS** (already configured)
3. **Use system fonts** when possible
4. **Inline critical CSS** for above-the-fold content

### Monitoring and Debugging

#### Development Mode

In development, performance metrics are logged to console:
- Core Web Vitals automatically tracked
- Custom performance marks and measures
- Network request timing

#### Production Mode

In production:
- Metrics can be sent to analytics
- No console logging (removed by Terser)
- Monitoring should be configured in analytics service

### Performance Checklist

Before deploying:

- [ ] Run `npm run bundle:check` to verify budgets
- [ ] Run `npm run lighthouse` for performance audit
- [ ] Test on real mobile device (Redmi 24115RA8EG)
- [ ] Test on throttled 3G network
- [ ] Verify Core Web Vitals are within targets
- [ ] Check for memory leaks
- [ ] Verify no console errors

### Troubleshooting

#### Bundle Size Too Large

1. Check `dist/stats.html` for bundle composition
2. Look for large dependencies that can be replaced
3. Ensure tree shaking is working correctly
4. Consider lazy loading heavy components

#### Slow Load Times

1. Check network waterfall in DevTools
2. Verify caching is working
3. Check for render-blocking resources
4. Profile with Lighthouse

#### Poor Runtime Performance

1. Check for memory leaks in DevTools
2. Profile component renders
3. Look for expensive computed properties
4. Check for unnecessary watchers

## References

- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [Vite Performance](https://vitejs.dev/guide/features.html#build-optimizations)
- [Vue Performance](https://vuejs.org/guide/best-practices/performance.html)

## Performance Baseline Analysis

### Overview

Performance baseline analysis allows you to track and compare build metrics over time. This helps detect performance regressions early and ensures the application stays within budget as features are added.

### Baseline Commands

Three commands are available for baseline analysis:

```bash
# Capture current build metrics as baseline
npm run baseline:capture

# Compare current build against baseline
npm run baseline:compare

# Generate detailed baseline report
npm run baseline:report
```

### Workflow

#### 1. Capture Initial Baseline

After completing a major feature or release:

```bash
npm run build
npm run baseline:capture
```

This captures:
- Bundle sizes (total, JS, CSS, HTML, assets)
- File counts by type
- Largest chunks with sizes
- Git commit information
- Timestamp

The baseline is saved to `.baselines/performance-baseline.json` and tracked in git.

#### 2. Compare Against Baseline

Before committing changes that may affect bundle size:

```bash
npm run build
npm run baseline:compare
```

This shows:
- Delta from baseline (bytes and percentage)
- Size increase/decrease for each category
- Budget status (total, JS, CSS)
- File count changes
- Regression warnings

**Exit codes:**
- `0` - No significant changes or improvements
- `1` - Performance regression detected (size increased significantly)

#### 3. View Baseline Report

To see detailed information about the current baseline:

```bash
npm run baseline:report
```

This displays:
- Current baseline metrics
- Git information (commit, branch, author)
- File counts and sizes
- Largest chunks
- Historical trend (if multiple baselines captured)

### Understanding Results

#### Baseline Comparison Output

```
📊 Comparing Against Baseline

Baseline Information:
  Created:  11/9/2025, 9:14:07 PM
  Commit:   abc1234
  Branch:   main

Current Build:
  Commit:   def5678
  Branch:   feature/new-component

📏 Size Comparison:

Total Size:
  Baseline: 201.06 KB
  Current:  215.30 KB
  Delta:    +14.24 KB (+7.1%)  ← Red indicates increase

JavaScript:
  Baseline: 176.66 KB
  Current:  188.90 KB
  Delta:    +12.24 KB (+6.9%)

CSS:
  Baseline: 17.50 KB
  Current:  19.50 KB
  Delta:    +2.00 KB (+11.4%)
```

#### What is Significant?

A change is considered significant if:
- **Total size** changes by more than 10 KB
- **JavaScript** changes by more than 5 KB
- **CSS** changes by more than 1 KB

#### Performance Regression

A regression is flagged when:
- Any category size increases (total, JS, or CSS)
- AND the change is significant

Regressions should be investigated before merging.

### Best Practices

#### When to Capture Baseline

1. **After major releases** - Set new baseline for next development cycle
2. **Before refactoring** - Track if refactoring improves performance
3. **After optimization work** - Document improvements
4. **Weekly/Sprint boundaries** - Regular checkpoint for trends

#### When to Compare

1. **Before committing** - Catch regressions early
2. **During code review** - Include comparison in PR
3. **In CI/CD** - Automated regression detection
4. **After adding dependencies** - Verify bundle impact

#### Handling Regressions

If baseline comparison shows regression:

1. **Investigate** - Run `npm run build:analyze` to see what changed
2. **Justify** - Document why the increase is necessary
3. **Optimize** - Look for ways to reduce impact:
   - Use dynamic imports for new features
   - Check for duplicate dependencies
   - Review tree shaking effectiveness
4. **Update baseline** - If increase is justified and optimized

#### Historical Tracking

Baselines are tracked in `.baselines/baseline-history.json`:
- Last 50 builds recorded
- Useful for trend analysis
- Shows size evolution over time

### Integration with CI/CD

Add to your CI pipeline:

```yaml
# Example GitHub Actions workflow
- name: Build
  run: npm run build

- name: Check Performance
  run: npm run baseline:compare

# This will fail if regression is detected
```

Or make it informational:

```yaml
- name: Performance Report
  run: npm run baseline:compare || true

- name: Upload Baseline Report
  # Save comparison for review
```

### Example Scenarios

#### Scenario 1: Adding New Feature

```bash
# Before starting
git checkout -b feature/new-dashboard

# Develop feature
# ...

# Before committing
npm run build
npm run baseline:compare

# Output shows +25 KB increase
# Investigate and optimize
npm run build:analyze

# After optimization, down to +8 KB
npm run baseline:compare
# ✅ Acceptable increase

# Commit changes
git commit -am "Add dashboard feature (+8KB)"
```

#### Scenario 2: Performance Optimization

```bash
# Baseline before optimization
npm run baseline:capture

# Perform optimizations
# - Remove unused dependencies
# - Add code splitting
# - Optimize imports

# Check improvement
npm run build
npm run baseline:compare

# Output shows -40 KB decrease
# ✅ Success! Document the improvement

# Update baseline with new optimized values
npm run baseline:capture
```

#### Scenario 3: Dependency Update

```bash
# Check current baseline
npm run baseline:report

# Update dependency
npm update vue

# Check impact
npm run build
npm run baseline:compare

# Output shows +2 KB increase
# ✅ Minimal impact, acceptable
```

### Baseline File Format

`.baselines/performance-baseline.json`:
```json
{
  "timestamp": "2025-11-09T21:14:07.845Z",
  "date": "11/9/2025, 9:14:07 PM",
  "git": {
    "commit": "1193cf3",
    "branch": "main",
    "author": "developer",
    "message": "Optimize bundle size"
  },
  "metrics": {
    "totalSize": 205882,
    "jsSize": 180896,
    "cssSize": 17918,
    "htmlSize": 904,
    "assetSize": 6164,
    "fileCount": {
      "total": 14,
      "js": 9,
      "css": 2,
      "html": 1,
      "assets": 2
    },
    "largestChunks": [
      {
        "name": "vue-vendor-CiE07igK.js",
        "size": 100873
      }
    ]
  },
  "budgets": {
    "totalSize": 1048576,
    "jsSize": 512000,
    "cssSize": 51200,
    "chunkSize": 102400
  }
}
```

### Troubleshooting

#### No baseline found

```bash
❌ No baseline found. Run "npm run baseline:capture" first.
```

**Solution:** Capture an initial baseline:
```bash
npm run build
npm run baseline:capture
```

#### Build not found

```bash
❌ Current build not found. Run "npm run build" first.
```

**Solution:** Run build before comparing:
```bash
npm run build
npm run baseline:compare
```

#### Unexpected large increase

If you see an unexpected large increase:

1. Check git status - uncommitted changes?
2. Run `npm run build:analyze` - what changed?
3. Check `node_modules` - dependency update?
4. Review recent commits - which change caused it?

---

**Last Updated**: Phase 1 - 2025-11-09
**Status**: Runtime optimizations implemented, monitoring active, baseline analysis enabled
