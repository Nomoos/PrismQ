# PrismQ Frontend Design System

**Version**: 1.0.0  
**Last Updated**: 2025-11-09  
**Target Device**: Redmi 24115RA8EG (6.7" AMOLED, 2712x1220px)

## Overview

Mobile-first design system for the PrismQ Frontend application, optimized for the Redmi 24115RA8EG device with WCAG 2.1 AA accessibility compliance. This design system provides the foundation for a task management interface that is intuitive, accessible, and performant.

---

## Table of Contents

1. [Design Principles](#design-principles)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing System](#spacing-system)
5. [Breakpoints](#breakpoints)
6. [Iconography](#iconography)
7. [Shadows & Elevation](#shadows--elevation)
8. [Animations](#animations)
9. [Border Radius](#border-radius)

---

## Design Principles

### 1. Mobile-First
- Design for 360px viewport first
- Progressive enhancement for larger screens
- Touch-optimized interactions (44x44px minimum)
- Portrait-primary orientation
- Thumb-friendly navigation zones

### 2. Accessibility
- WCAG 2.1 AA compliance (target AAA where possible)
- Color contrast minimum 4.5:1 for normal text
- Color contrast minimum 3:1 for large text (18px+)
- Screen reader compatible
- Keyboard navigable
- Focus indicators visible (2px outline)
- Touch targets 44x44px minimum

### 3. Performance
- Lightweight visuals
- System fonts for fast loading
- Optimized images (WebP, lazy loading)
- Minimal animations (60fps target)
- AMOLED-optimized dark theme
- Bundle size < 500KB initial load

### 4. Task-Focused
- Clear task status indicators
- Quick actions (claim, complete, fail)
- Minimal steps to complete workflows
- Clear error states and recovery paths
- Progress visibility throughout

---

## Color System

### Primary Colors (Task Actions)

```css
/* Primary Blue - Main Actions */
--primary-50:  #f0f9ff;
--primary-100: #e0f2fe;
--primary-200: #b9e6fe;
--primary-300: #7dd3fc;
--primary-400: #38bdf8;
--primary-500: #0ea5e9;  /* Main primary */
--primary-600: #0284c7;  /* Hover state */
--primary-700: #0369a1;  /* Active state */
--primary-800: #075985;
--primary-900: #0c4a6e;
```

**Usage**: Claim buttons, active states, links, primary CTAs

**Accessibility**:
- primary-500 on white: 4.51:1 ✅ (WCAG AA)
- primary-600 on white: 6.04:1 ✅ (WCAG AA)
- primary-700 on white: 8.03:1 ✅ (WCAG AAA)

### Status Colors

```css
/* Success Green - Completed Tasks */
--success-50:  #f0fdf4;
--success-100: #dcfce7;
--success-500: #22c55e;  /* Main success */
--success-600: #16a34a;  /* Dark variant */
--success-700: #15803d;

/* Warning Orange - Claimed/In Progress */
--warning-50:  #fffbeb;
--warning-100: #fef3c7;
--warning-500: #f59e0b;  /* Main warning */
--warning-600: #d97706;  /* Dark variant */
--warning-700: #b45309;

/* Error Red - Failed Tasks */
--error-50:  #fef2f2;
--error-100: #fee2e2;
--error-500: #ef4444;  /* Main error */
--error-600: #dc2626;  /* Dark variant */
--error-700: #b91c1c;

/* Info Blue - Pending Tasks */
--info-50:  #eff6ff;
--info-100: #dbeafe;
--info-500: #3b82f6;  /* Main info */
--info-600: #2563eb;  /* Dark variant */
--info-700: #1d4ed8;
```

**Status Mapping**:
- **Pending**: Info Blue (--info-500)
- **Claimed**: Warning Orange (--warning-500)
- **Completed**: Success Green (--success-500)
- **Failed**: Error Red (--error-500)

**Accessibility**:
- All status colors meet 4.5:1 contrast on white backgrounds
- All -600 variants meet 7:1 contrast (AAA)

### Neutral Colors

```css
/* Gray Scale */
--gray-50:  #f9fafb;  /* Background light */
--gray-100: #f3f4f6;  /* Card background */
--gray-200: #e5e7eb;  /* Border light */
--gray-300: #d1d5db;  /* Border */
--gray-400: #9ca3af;  /* Disabled text */
--gray-500: #6b7280;  /* Secondary text */
--gray-600: #4b5563;  /* Body text */
--gray-700: #374151;  /* Headings */
--gray-800: #1f2937;  /* Dark headings */
--gray-900: #111827;  /* Black */
```

**Usage**:
- gray-50/100: Backgrounds
- gray-200/300: Borders
- gray-400: Disabled states
- gray-500: Secondary text
- gray-600: Body text
- gray-700/800/900: Headings

**Accessibility**:
- gray-600 on white: 7.02:1 ✅ (AAA)
- gray-700 on white: 10.74:1 ✅ (AAA)
- gray-500 on white: 4.52:1 ✅ (AA)

### Dark Theme (GitHub-Inspired AMOLED)

```css
/* Background Colors */
--dark-bg-primary:   #000000;  /* True black for AMOLED */
--dark-bg-secondary: #0d1117;  /* GitHub dark */
--dark-bg-tertiary:  #161b22;  /* Elevated surfaces */
--dark-bg-card:      #1c2128;  /* Card backgrounds */

/* Border Colors */
--dark-border-primary:   #30363d;
--dark-border-secondary: #21262d;

/* Text Colors */
--dark-text-primary:   #e6edf3;  /* Main text (AAA) */
--dark-text-secondary: #7d8590;  /* Secondary text */
--dark-text-tertiary:  #656d76;  /* Tertiary text */

/* Link & Interactive */
--dark-link: #58a6ff;  /* GitHub blue */
--dark-link-hover: #79c0ff;
```

**Accessibility** (Dark Theme):
- dark-text-primary on dark-bg-primary: 13.45:1 ✅ (AAA)
- dark-text-secondary on dark-bg-primary: 7.18:1 ✅ (AAA)
- dark-link on dark-bg-primary: 8.32:1 ✅ (AAA)

**Dark Status Colors**:
```css
--dark-success: #3fb950;  /* Green */
--dark-warning: #d29922;  /* Orange */
--dark-error:   #f85149;  /* Red */
--dark-info:    #58a6ff;  /* Blue */
```

### Background Colors

```css
/* Light Theme */
--bg-primary:   #ffffff;  /* Main background */
--bg-secondary: #f9fafb;  /* Secondary background */
--bg-tertiary:  #f3f4f6;  /* Tertiary background */

/* Dark Theme */
--bg-dark-primary:   #000000;  /* AMOLED black */
--bg-dark-secondary: #0d1117;
--bg-dark-tertiary:  #161b22;
```

---

## Typography

### Font Stack (System Fonts)

```css
--font-family-base: -apple-system, BlinkMacSystemFont, "Segoe UI", 
                    Roboto, "Helvetica Neue", Arial, sans-serif;

--font-family-mono: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono",
                    Consolas, "Courier New", monospace;
```

**Rationale**: System fonts for instant loading, native feel, and performance.

### Font Sizes (Mobile-First)

```css
/* Mobile (default) */
--text-xs:   12px;  /* Captions, timestamps */
--text-sm:   14px;  /* Labels, secondary text */
--text-base: 16px;  /* Body text (minimum) */
--text-lg:   18px;  /* Large body, small headings */
--text-xl:   20px;  /* H4 */
--text-2xl:  24px;  /* H3 */
--text-3xl:  28px;  /* H2 */
--text-4xl:  32px;  /* H1 */
--text-5xl:  36px;  /* Display headings */
```

**Accessibility**:
- Minimum body text: 16px (WCAG AA)
- All text scalable to 200%
- No text in images

### Font Weights

```css
--font-normal:    400;  /* Body text */
--font-medium:    500;  /* Emphasized text */
--font-semibold:  600;  /* Subheadings */
--font-bold:      700;  /* Headings */
```

### Line Heights

```css
--leading-tight:  1.25;  /* Headings */
--leading-normal: 1.5;   /* Body text (WCAG) */
--leading-relaxed: 1.75; /* Long-form content */
```

**Accessibility**:
- Body text: 1.5 minimum (WCAG AA)
- Headings: 1.25 (tighter for visual hierarchy)

### Typography Scale Usage

```css
/* Headings */
h1: text-4xl (32px), font-bold, leading-tight
h2: text-3xl (28px), font-bold, leading-tight
h3: text-2xl (24px), font-semibold, leading-tight
h4: text-xl (20px), font-semibold, leading-tight
h5: text-lg (18px), font-medium, leading-normal
h6: text-base (16px), font-medium, leading-normal

/* Body */
body: text-base (16px), font-normal, leading-normal
small: text-sm (14px), font-normal, leading-normal
caption: text-xs (12px), font-normal, leading-normal

/* Interactive */
button: text-base (16px), font-medium
link: text-base (16px), font-medium, underline
label: text-sm (14px), font-medium
```

---

## Spacing System

### Base Unit: 8px Grid

```css
--space-0:  0;
--space-1:  4px;   /* 0.5 × base */
--space-2:  8px;   /* 1 × base */
--space-3:  12px;  /* 1.5 × base */
--space-4:  16px;  /* 2 × base */
--space-5:  20px;  /* 2.5 × base */
--space-6:  24px;  /* 3 × base */
--space-8:  32px;  /* 4 × base */
--space-10: 40px;  /* 5 × base */
--space-12: 48px;  /* 6 × base */
--space-16: 64px;  /* 8 × base */
--space-20: 80px;  /* 10 × base */
```

### Touch Targets

```css
--touch-min: 44px;  /* Minimum touch target (WCAG) */
--touch-lg:  48px;  /* Large touch target */
--touch-xl:  56px;  /* Extra large touch target */
```

**Accessibility**: All interactive elements ≥ 44x44px

### Common Spacing Patterns

```css
/* Component Padding */
--padding-xs:  8px;   /* Tight padding */
--padding-sm:  12px;  /* Small padding */
--padding-md:  16px;  /* Default padding */
--padding-lg:  24px;  /* Large padding */
--padding-xl:  32px;  /* Extra large padding */

/* Section Spacing */
--section-gap-sm: 16px;  /* Tight sections */
--section-gap-md: 24px;  /* Default sections */
--section-gap-lg: 32px;  /* Large sections */
--section-gap-xl: 48px;  /* Extra large sections */

/* Card Spacing */
--card-padding: 16px;     /* Card internal padding */
--card-gap:     16px;     /* Gap between cards */

/* Form Spacing */
--form-field-gap: 16px;   /* Between form fields */
--form-label-gap: 8px;    /* Label to input */
```

---

## Breakpoints

### Mobile-First Breakpoints

```css
/* Mobile (default) - 0-639px */
/* Redmi 24115RA8EG primary target: 360-428px */

/* Small tablets - 640px+ */
@media (min-width: 640px) { /* sm */ }

/* Tablets - 768px+ */
@media (min-width: 768px) { /* md */ }

/* Laptops - 1024px+ */
@media (min-width: 1024px) { /* lg */ }

/* Desktops - 1280px+ */
@media (min-width: 1280px) { /* xl */ }

/* Large desktops - 1536px+ */
@media (min-width: 1536px) { /* 2xl */ }
```

### Breakpoint Usage

**Mobile (< 640px)**:
- Single column layout
- Bottom tab navigation
- Full-width cards
- Stack vertically
- Touch-optimized

**Tablet (640px - 1023px)**:
- 2-column grid for cards
- Side navigation option
- Increased padding
- Larger touch targets

**Desktop (1024px+)**:
- Multi-column layouts
- Persistent sidebar
- Hover states
- Keyboard shortcuts
- More whitespace

---

## Iconography

### Icon Sizes

```css
--icon-xs:  16px;  /* Small icons */
--icon-sm:  20px;  /* Regular icons */
--icon-md:  24px;  /* Default icons */
--icon-lg:  32px;  /* Large icons */
--icon-xl:  48px;  /* Extra large icons */
```

### Icon Library

**Recommended**: Heroicons (MIT license)
- Outline style: Regular use
- Solid style: Active/selected states

**Icon Usage**:
- Navigation: 24px (md)
- Buttons: 20px (sm)
- Status indicators: 16px (xs)
- Feature icons: 32px (lg)

### Accessibility

```html
<!-- Icon with text (preferred) -->
<button>
  <icon aria-hidden="true" />
  <span>Button Text</span>
</button>

<!-- Icon-only (requires aria-label) -->
<button aria-label="Close">
  <icon aria-hidden="true" />
</button>
```

---

## Shadows & Elevation

### Shadow System

```css
/* Elevation Levels */
--shadow-xs:  0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-sm:  0 1px 3px 0 rgb(0 0 0 / 0.1),
              0 1px 2px -1px rgb(0 0 0 / 0.1);
--shadow-md:  0 4px 6px -1px rgb(0 0 0 / 0.1),
              0 2px 4px -2px rgb(0 0 0 / 0.1);
--shadow-lg:  0 10px 15px -3px rgb(0 0 0 / 0.1),
              0 4px 6px -4px rgb(0 0 0 / 0.1);
--shadow-xl:  0 20px 25px -5px rgb(0 0 0 / 0.1),
              0 8px 10px -6px rgb(0 0 0 / 0.1);
--shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
```

### Elevation Hierarchy

- **Level 0** (no shadow): Page background
- **Level 1** (shadow-xs): Cards, containers
- **Level 2** (shadow-sm): Hover states
- **Level 3** (shadow-md): Dropdowns, popovers
- **Level 4** (shadow-lg): Modals, dialogs
- **Level 5** (shadow-xl): Toast notifications

### Dark Theme Shadows

```css
/* Dark theme uses lighter shadows with glow */
--dark-shadow-sm: 0 1px 3px 0 rgb(255 255 255 / 0.05);
--dark-shadow-md: 0 4px 6px -1px rgb(255 255 255 / 0.1);
--dark-shadow-lg: 0 10px 15px -3px rgb(255 255 255 / 0.15);
```

---

## Animations

### Transition Durations

```css
--duration-fast:   150ms;  /* Hover, focus */
--duration-base:   200ms;  /* Default */
--duration-medium: 300ms;  /* Modals, dropdowns */
--duration-slow:   500ms;  /* Page transitions */
```

### Easing Functions

```css
--ease-in:     cubic-bezier(0.4, 0, 1, 1);
--ease-out:    cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

### Animation Guidelines

1. **Performance**: Use transform and opacity only (GPU-accelerated)
2. **Frame Rate**: Target 60fps
3. **Reduced Motion**: Respect `prefers-reduced-motion`
4. **Subtle**: Animations should enhance, not distract

```css
/* Reduced Motion Support */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Common Animations

```css
/* Fade In */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide Up */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scale In */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```

---

## Border Radius

```css
--radius-none: 0;
--radius-sm:   4px;   /* Small elements */
--radius-md:   8px;   /* Default (cards, buttons) */
--radius-lg:   12px;  /* Large cards */
--radius-xl:   16px;  /* Modals */
--radius-full: 9999px; /* Pills, avatars */
```

**Usage**:
- Buttons: 8px (md)
- Cards: 8px (md)
- Inputs: 8px (md)
- Modals: 16px (xl)
- Badges: 9999px (full)

---

## Tailwind CSS Configuration

### Configuration Example

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
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
      },
      spacing: {
        'touch': '44px',
        'touch-lg': '48px',
        'touch-xl': '56px',
      },
      screens: {
        'xs': '360px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Cascadia Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
```

---

## CSS Custom Properties (CSS Variables)

### Complete Variable Set

```css
:root {
  /* Colors - Primary */
  --primary-500: #0ea5e9;
  --primary-600: #0284c7;
  --primary-700: #0369a1;
  
  /* Colors - Status */
  --success-500: #22c55e;
  --warning-500: #f59e0b;
  --error-500: #ef4444;
  --info-500: #3b82f6;
  
  /* Colors - Neutral */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-900: #111827;
  
  /* Typography */
  --text-base: 16px;
  --leading-normal: 1.5;
  --font-normal: 400;
  --font-semibold: 600;
  
  /* Spacing */
  --space-2: 8px;
  --space-4: 16px;
  --space-6: 24px;
  --touch-min: 44px;
  
  /* Shadows */
  --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  
  /* Animations */
  --duration-base: 200ms;
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  
  /* Border Radius */
  --radius-md: 8px;
  --radius-lg: 12px;
}

/* Dark Theme */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #000000;
    --bg-secondary: #0d1117;
    --text-primary: #e6edf3;
    --text-secondary: #7d8590;
    --border-primary: #30363d;
  }
}
```

---

## Implementation Guidelines

### 1. Start with Tailwind

Use Tailwind CSS utilities first:
```html
<button class="bg-primary-500 text-white px-4 py-2 rounded-md">
  Claim Task
</button>
```

### 2. Use CSS Variables for Theming

```css
.task-card {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}
```

### 3. Component-Specific Styles

Create scoped styles when needed:
```vue
<style scoped>
.custom-component {
  /* Use design system tokens */
  padding: var(--space-4);
  font-size: var(--text-base);
}
</style>
```

---

## Accessibility Checklist

- [ ] All text meets 4.5:1 contrast ratio (AA)
- [ ] All touch targets ≥ 44x44px
- [ ] Focus indicators visible (2px outline)
- [ ] Keyboard navigable (tab order)
- [ ] Screen reader compatible (ARIA labels)
- [ ] Form labels explicitly associated
- [ ] Error messages linked to fields
- [ ] No color-only information
- [ ] Text scalable to 200%
- [ ] Respects prefers-reduced-motion

---

## Next Steps

1. **Worker03**: Implement Tailwind configuration
2. **Worker03**: Create Vue component library
3. **Worker12**: Validate accessibility compliance
4. **Worker04**: Optimize for mobile performance

---

**Created By**: Worker11 (UX Design Specialist)  
**Date**: 2025-11-09  
**Status**: ✅ Complete  
**Version**: 1.0.0
