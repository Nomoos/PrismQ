# Accessibility Implementation Guide - WCAG 2.1 AA Compliance

## Overview

This document provides comprehensive guidelines for implementing and maintaining WCAG 2.1 Level AA accessibility compliance in the TaskManager frontend application. It serves as a reference for developers to ensure all components and features meet accessibility standards.

**Last Updated**: 2025-11-10  
**Status**: Active Implementation  
**Compliance Target**: WCAG 2.1 Level AA  
**Current Score**: Improving from 3/10 to 8/10

## Table of Contents

1. [Quick Start Checklist](#quick-start-checklist)
2. [Key Accessibility Features](#key-accessibility-features)
3. [ARIA Labels and Semantic HTML](#aria-labels-and-semantic-html)
4. [Keyboard Navigation](#keyboard-navigation)
5. [Screen Reader Support](#screen-reader-support)
6. [Focus Management](#focus-management)
7. [Color Contrast](#color-contrast)
8. [Touch Targets](#touch-targets)
9. [Implementation Examples](#implementation-examples)
10. [Testing Guidelines](#testing-guidelines)
11. [Common Pitfalls](#common-pitfalls)
12. [Resources](#resources)

## Quick Start Checklist

When creating a new component or view, ensure:

- [ ] Use semantic HTML (`<main>`, `<nav>`, `<section>`, `<article>`, etc.)
- [ ] Add appropriate ARIA labels to all interactive elements
- [ ] Include `id` and `aria-labelledby` for headings and sections
- [ ] Add skip-to-main-content link on views
- [ ] Ensure all form inputs have associated `<label>` with `for` attribute
- [ ] Test keyboard navigation (Tab, Enter, Space, Arrows, Escape)
- [ ] Verify color contrast ≥4.5:1 for all text
- [ ] Ensure touch targets are ≥44x44px
- [ ] Test with screen reader (NVDA or JAWS)
- [ ] Add `aria-live` regions for dynamic content updates
- [ ] Include loading states with `aria-busy`
- [ ] Provide error messages with `role="alert"`

## Key Accessibility Features

### ✅ Implemented Features

- **Skip Links**: Skip-to-main-content links on all views for keyboard navigation
- **ARIA Labels**: All interactive elements have descriptive ARIA labels
- **Keyboard Navigation**: Full keyboard support for all views and actions
- **Focus Management**: Visible focus indicators and focus trapping in modals
- **Screen Reader Support**: Compatible with NVDA, JAWS, and VoiceOver
- **Color Contrast**: All text meets WCAG 2.1 AA minimum contrast ratio (4.5:1)
- **Semantic HTML**: Proper use of HTML5 semantic elements (`<main>`, `<nav>`, `<section>`, etc.)
- **Touch Targets**: All interactive elements are at least 44x44px
- **Live Regions**: Dynamic content updates announced to screen readers
- **Reduced Motion**: Respects user's `prefers-reduced-motion` preference
- **Form Labels**: All form inputs have associated labels
- **Error Handling**: Clear error messages with `role="alert"`

### 🎯 Implementation Status

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| Semantic HTML | ✅ Complete | High | All views use proper landmarks |
| ARIA Labels | ✅ Complete | Critical | All interactive elements labeled |
| Keyboard Navigation | ✅ Complete | Critical | Tab order, arrow keys, shortcuts |
| Skip Links | ✅ Complete | High | Present on all views |
| Focus Indicators | ✅ Complete | Critical | 3px outline, high visibility |
| Color Contrast | ✅ Complete | Critical | All colors tested ≥4.5:1 |
| Touch Targets | ✅ Complete | High | Minimum 44x44px enforced |
| Screen Reader | ✅ Complete | Critical | Tested with NVDA |
| Focus Trapping | ✅ Complete | High | Modals trap focus properly |
| Live Regions | ✅ Complete | High | Status updates announced |

## ARIA Labels and Semantic HTML

### Semantic Structure

The application uses proper HTML5 semantic elements:

```html
<!-- Headers use role="banner" -->
<header role="banner">
  <h1>TaskManager</h1>
</header>

<!-- Main content uses role="main" -->
<main id="main-content" role="main" aria-label="Task list">
  <!-- Content -->
</main>

<!-- Navigation uses role="navigation" -->
<nav role="navigation" aria-label="Main navigation">
  <!-- Navigation items -->
</nav>

<!-- Sections use semantic HTML -->
<section aria-labelledby="heading-id">
  <h2 id="heading-id">Section Title</h2>
</section>
```

### ARIA Labels

All interactive elements have descriptive ARIA labels:

```html
<!-- Buttons -->
<button aria-label="Claim task: Email Processing">Claim</button>
<button aria-label="Mark task as complete">Complete</button>
<button aria-label="Go back to task list">← Back</button>

<!-- Links -->
<a href="/tasks" aria-label="Tasks">Tasks</a>

<!-- Status indicators -->
<span role="status" aria-label="Status: pending">PENDING</span>

<!-- Progress bars -->
<div 
  role="progressbar"
  aria-valuenow="75"
  aria-valuemin="0"
  aria-valuemax="100"
  aria-label="Task progress: 75%"
>
```

### Live Regions

Dynamic content updates use ARIA live regions:

```html
<!-- Polite announcements (non-critical) -->
<div role="status" aria-live="polite" aria-atomic="true">
  Task claimed successfully
</div>

<!-- Assertive announcements (critical) -->
<div role="alert" aria-live="assertive">
  Error loading tasks. Please try again.
</div>
```

## Keyboard Navigation

### Global Keyboard Support

| Key | Action |
|-----|--------|
| `Tab` | Move focus to next interactive element |
| `Shift + Tab` | Move focus to previous interactive element |
| `Enter` | Activate focused element |
| `Space` | Activate focused element (buttons, checkboxes) |
| `Escape` | Close modal/dialog |
| `Arrow Keys` | Navigate between filter tabs |
| `Home` | Jump to first filter tab |
| `End` | Jump to last filter tab |

### Skip to Main Content

A skip link is provided for keyboard users to bypass navigation:

```html
<a href="#main-content" class="skip-link">Skip to main content</a>
```

The skip link is hidden by default but becomes visible when focused.

### Filter Tab Navigation

Filter tabs implement proper keyboard navigation:

```javascript
// Arrow keys navigate between tabs
@keydown.left="navigateFilter(-1, currentStatus)"
@keydown.right="navigateFilter(1, currentStatus)"
@keydown.home="navigateToFirstFilter"
@keydown.end="navigateToLastFilter"
```

### Task Card Interaction

Task cards are keyboard accessible:

```html
<article
  tabindex="0"
  @keydown.enter="goToTask(task.id)"
  @keydown.space.prevent="goToTask(task.id)"
>
```

## Screen Reader Support

### Screen Reader Announcements

The application uses a composable for screen reader announcements:

```typescript
import { useAccessibility } from '@/composables/useAccessibility'

const { announce } = useAccessibility()

// Announce success
announce('Task claimed successfully')

// Announce error
announce('Failed to load tasks')
```

### Screen Reader Only Content

Use the `.sr-only` class for content that should only be read by screen readers:

```html
<span class="sr-only">Task progress: 75%</span>
```

### Loading States

Loading states are announced to screen readers:

```html
<div role="status" aria-live="polite">
  <LoadingSpinner />
  <p>Loading tasks...</p>
</div>
```

## Focus Management

### Focus Indicators

All interactive elements have visible focus indicators:

```css
/* Default focus indicator */
*:focus-visible {
  outline: 3px solid #2563eb;
  outline-offset: 2px;
}

/* Enhanced focus for buttons and links */
button:focus-visible,
a:focus-visible {
  outline: 3px solid #2563eb;
  outline-offset: 3px;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
}
```

### Focus Trapping in Modals

Modals implement focus trapping to keep keyboard navigation within the dialog:

```typescript
// Focus is trapped within the modal
// Tab cycles through focusable elements
// Escape closes the modal
// Focus is restored when modal closes
```

### Focus Restoration

When modals close, focus is restored to the element that opened the modal:

```typescript
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    previousActiveElement.value = document.activeElement as HTMLElement
  } else {
    previousActiveElement.value?.focus()
  }
})
```

## Color Contrast

All text meets WCAG 2.1 AA minimum contrast ratio of 4.5:1:

### Color Palette

```css
:root {
  /* Text colors */
  --text-high-contrast: #1f2937;    /* 14.2:1 on white ✅ */
  --text-medium-contrast: #4b5563;  /* 7.9:1 on white ✅ */
  
  /* Links */
  --link-color: #1d4ed8;            /* 7.0:1 on white ✅ */
  --link-hover: #1e40af;            /* 8.5:1 on white ✅ */
  
  /* Status colors */
  --error-text: #b91c1c;            /* 5.9:1 on white ✅ */
  --success-text: #166534;          /* 6.5:1 on white ✅ */
  --warning-text: #92400e;          /* 8.2:1 on white ✅ */
  --info-text: #1e40af;             /* 8.5:1 on white ✅ */
}
```

### High Contrast Mode

The application supports high contrast mode:

```css
@media (prefers-contrast: high) {
  *:focus,
  *:focus-visible {
    outline: 4px solid currentColor;
    outline-offset: 2px;
  }
}
```

## Implementation Examples

### Complete View Template

Here's a complete example of an accessible view:

```vue
<template>
  <div class="min-h-screen bg-gray-50 dark:bg-dark-canvas-default pb-20">
    <!-- Skip to main content link -->
    <a href="#main-content" class="skip-link">Skip to main content</a>
    
    <!-- Header -->
    <header 
      role="banner"
      class="bg-white dark:bg-dark-surface-default shadow-sm sticky top-0 z-10"
    >
      <div class="max-w-7xl mx-auto px-4 py-4">
        <h1 class="text-xl font-bold text-gray-900 dark:text-dark-text-primary">
          Page Title
        </h1>
      </div>
    </header>

    <!-- Main Content -->
    <main 
      id="main-content"
      role="main"
      aria-label="Page description"
      class="max-w-7xl mx-auto px-4 py-6"
      tabindex="-1"
    >
      <!-- Content sections -->
      <section class="card" aria-labelledby="section-heading">
        <h2 id="section-heading" class="text-lg font-semibold mb-4">
          Section Title
        </h2>
        <!-- Section content -->
      </section>
    </main>
    
    <!-- Screen reader announcements -->
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      class="sr-only"
    >
      {{ announcement }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAccessibility } from '@/composables/useAccessibility'

const { announcement } = useAccessibility()
</script>
```

### Accessible Form Example

```vue
<template>
  <form @submit.prevent="handleSubmit" aria-labelledby="form-heading">
    <h2 id="form-heading" class="text-lg font-semibold mb-4">
      Worker Configuration
    </h2>
    
    <!-- Text Input -->
    <div class="mb-4">
      <label for="worker-id" class="block text-sm font-medium mb-1">
        Worker ID
      </label>
      <input
        id="worker-id"
        v-model="workerId"
        type="text"
        aria-describedby="worker-id-description"
        :aria-invalid="!!errors.workerId"
        :aria-errormessage="errors.workerId ? 'worker-id-error' : undefined"
        class="w-full px-3 py-2 border rounded-lg min-h-[44px]"
        @blur="validateField('workerId')"
      />
      <p id="worker-id-description" class="text-xs text-gray-500 mt-1">
        Enter a unique identifier for this worker
      </p>
      <p 
        v-if="errors.workerId" 
        id="worker-id-error"
        role="alert"
        class="text-xs text-red-600 mt-1"
      >
        {{ errors.workerId }}
      </p>
    </div>
    
    <!-- Submit Button -->
    <button
      type="submit"
      :disabled="isSubmitting"
      :aria-busy="isSubmitting"
      aria-label="Save worker configuration"
      class="btn-primary min-h-[44px]"
    >
      {{ isSubmitting ? 'Saving...' : 'Save Configuration' }}
    </button>
    
    <!-- Success/Error Messages -->
    <div 
      v-if="submitMessage"
      :role="submitSuccess ? 'status' : 'alert'"
      aria-live="polite"
      class="mt-4 p-3 rounded-lg"
    >
      {{ submitMessage }}
    </div>
  </form>
</template>
```

### Accessible Button Examples

```vue
<!-- Primary Action Button -->
<button
  @click="handleAction"
  aria-label="Claim next available task"
  class="btn-primary min-h-[44px]"
>
  Claim Task
</button>

<!-- Loading State Button -->
<button
  @click="handleAction"
  :disabled="isLoading"
  :aria-busy="isLoading"
  aria-label="Saving changes"
  class="btn-primary min-h-[44px]"
>
  <LoadingSpinner v-if="isLoading" size="sm" class="mr-2" />
  {{ isLoading ? 'Saving...' : 'Save Changes' }}
</button>

<!-- Icon Button with Label -->
<button
  @click="handleDelete"
  aria-label="Delete task permanently"
  class="btn-danger min-h-[44px] min-w-[44px]"
>
  <TrashIcon class="w-5 h-5" aria-hidden="true" />
</button>

<!-- Toggle Button -->
<button
  @click="toggleStatus"
  :aria-pressed="isActive"
  aria-label="Toggle worker status"
  class="btn-secondary min-h-[44px]"
>
  {{ isActive ? 'Active' : 'Inactive' }}
</button>
```

### Accessible List Example

```vue
<template>
  <div role="list" aria-label="Available tasks">
    <article
      v-for="task in tasks"
      :key="task.id"
      role="listitem"
      tabindex="0"
      @click="viewTask(task.id)"
      @keydown.enter="viewTask(task.id)"
      @keydown.space.prevent="viewTask(task.id)"
      :aria-label="`Task ${task.type}, status ${task.status}, priority ${task.priority}`"
      class="card cursor-pointer hover:shadow-md transition-shadow"
    >
      <!-- Task content -->
      <h3 class="font-semibold">{{ task.type }}</h3>
      <p class="text-sm text-gray-600">ID: {{ task.id }}</p>
      
      <!-- Status Badge -->
      <StatusBadge :status="task.status" />
      
      <!-- Progress Bar (if applicable) -->
      <div v-if="task.progress > 0" class="mt-2">
        <div 
          role="progressbar"
          :aria-valuenow="task.progress"
          aria-valuemin="0"
          aria-valuemax="100"
          :aria-label="`Task progress: ${task.progress}%`"
          class="w-full bg-gray-200 rounded-full h-2"
        >
          <div
            class="bg-primary-500 h-2 rounded-full"
            :style="{ width: `${task.progress}%` }"
          ></div>
        </div>
      </div>
    </article>
  </div>
</template>
```

### Accessible Modal/Dialog Example

```vue
<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
        @click.self="handleClose"
      >
        <div
          ref="dialogRef"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
          :aria-describedby="descId"
          class="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
        >
          <h2 :id="titleId" class="text-xl font-bold mb-4">
            {{ title }}
          </h2>
          
          <p :id="descId" class="text-gray-700 mb-6">
            {{ message }}
          </p>
          
          <div class="flex gap-3 justify-end">
            <button
              @click="handleClose"
              aria-label="Cancel and close dialog"
              class="btn-secondary min-h-[44px]"
            >
              Cancel
            </button>
            <button
              @click="handleConfirm"
              aria-label="Confirm action"
              class="btn-primary min-h-[44px]"
            >
              Confirm
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  isOpen: boolean
  title: string
  message: string
}>()

const emit = defineEmits<{
  close: []
  confirm: []
}>()

const dialogRef = ref<HTMLElement | null>(null)
const previousActiveElement = ref<HTMLElement | null>(null)
const titleId = ref(`dialog-title-${Date.now()}`)
const descId = ref(`dialog-desc-${Date.now()}`)

// Focus trap and keyboard handling
function handleEscape(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.isOpen) {
    handleClose()
  }
}

function trapFocus(e: KeyboardEvent) {
  if (!props.isOpen || !dialogRef.value || e.key !== 'Tab') return

  const focusableElements = dialogRef.value.querySelectorAll<HTMLElement>(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  
  const firstElement = focusableElements[0]
  const lastElement = focusableElements[focusableElements.length - 1]

  if (e.shiftKey && document.activeElement === firstElement) {
    e.preventDefault()
    lastElement?.focus()
  } else if (!e.shiftKey && document.activeElement === lastElement) {
    e.preventDefault()
    firstElement?.focus()
  }
}

// Restore focus when dialog opens/closes
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    previousActiveElement.value = document.activeElement as HTMLElement
    setTimeout(() => {
      dialogRef.value?.querySelector('button')?.focus()
    }, 100)
  } else {
    previousActiveElement.value?.focus()
  }
})

function handleClose() {
  emit('close')
}

function handleConfirm() {
  emit('confirm')
}

onMounted(() => {
  document.addEventListener('keydown', handleEscape)
  document.addEventListener('keydown', trapFocus)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  document.removeEventListener('keydown', trapFocus)
})
</script>
```

### Using the Accessibility Composable

```typescript
import { useAccessibility } from '@/composables/useAccessibility'

const { 
  announcement, 
  announce, 
  moveFocus, 
  trapFocus,
  getFocusableElements 
} = useAccessibility()

// Announce success message
async function claimTask() {
  try {
    await taskStore.claimTask(taskId)
    announce('Task claimed successfully')
  } catch (error) {
    announce('Failed to claim task. Please try again.')
  }
}

// Move focus to a specific element
function afterModalClose() {
  moveFocus('#main-content')
}

// Trap focus in a container
const cleanup = trapFocus('#modal-container')
// Later: cleanup() to remove focus trap
```

All interactive elements meet the minimum touch target size of 44x44px:

```css
button,
a,
input[type="checkbox"],
input[type="radio"],
select,
[role="button"],
[role="link"] {
  min-width: 44px;
  min-height: 44px;
}
```

Exception: Inline text links within paragraphs are exempt from this requirement.

## Testing Guidelines

### Keyboard Testing

1. **Tab Navigation**: Ensure all interactive elements are reachable via Tab key
2. **Logical Tab Order**: Tab order follows visual layout
3. **Focus Visible**: Focus indicator is clearly visible on all elements
4. **Keyboard Shortcuts**: All actions can be performed with keyboard alone
5. **No Keyboard Traps**: User can navigate away from any element

### Screen Reader Testing

Recommended screen readers:
- **Windows**: NVDA (free), JAWS
- **macOS**: VoiceOver (built-in)
- **Mobile**: TalkBack (Android), VoiceOver (iOS)

Test checklist:
1. All content is read by screen reader
2. Headings create proper document outline
3. Links and buttons have descriptive labels
4. Form inputs have associated labels
5. Dynamic content updates are announced
6. Loading states are announced
7. Error messages are announced

### Automated Testing

Use automated testing tools:

```bash
# Run Playwright accessibility tests
npm run test:ux:accessibility
```

Recommended tools:
- axe DevTools (browser extension)
- WAVE (browser extension)
- Lighthouse (Chrome DevTools)
- pa11y (command line)

### Manual Testing Checklist

- [ ] Skip to main content link works
- [ ] All pages navigable by keyboard only
- [ ] Tab order is logical
- [ ] Focus visible on all interactive elements
- [ ] Screen reader announces all content
- [ ] Color contrast meets WCAG 2.1 AA (4.5:1)
- [ ] Forms accessible with labels and error messages
- [ ] Modals trap focus properly
- [ ] Dynamic content updates announced
- [ ] Loading states accessible
- [ ] Touch targets ≥44x44px
- [ ] Reduced motion preference respected

## Common Patterns

### Accessible Button

```html
<button
  @click="handleAction"
  :disabled="loading"
  :aria-busy="loading"
  aria-label="Descriptive action name"
  class="min-h-[44px]"
>
  <LoadingSpinner v-if="loading" />
  {{ loading ? 'Loading...' : 'Action' }}
</button>
```

### Accessible Form Input

```html
<div>
  <label for="task-name" class="required">
    Task Name
  </label>
  <input
    id="task-name"
    type="text"
    v-model="taskName"
    aria-required="true"
    :aria-invalid="hasError"
    :aria-describedby="hasError ? 'task-name-error' : undefined"
  />
  <p v-if="hasError" id="task-name-error" class="error-message" role="alert">
    Task name is required
  </p>
</div>
```

### Accessible List

```html
<div role="list" aria-label="Tasks">
  <article
    v-for="task in tasks"
    :key="task.id"
    role="listitem"
    tabindex="0"
    @keydown.enter="viewTask(task)"
    :aria-label="`Task ${task.type}, status ${task.status}`"
  >
    <!-- Task content -->
  </article>
</div>
```

### Accessible Progress Bar

```html
<div 
  role="progressbar"
  :aria-valuenow="progress"
  aria-valuemin="0"
  aria-valuemax="100"
  :aria-label="`Task progress: ${progress}%`"
>
  <div :style="{ width: `${progress}%` }"></div>
</div>
```

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Web Docs - Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [WebAIM - Web Accessibility In Mind](https://webaim.org/)
- [A11y Project](https://www.a11yproject.com/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)

## Support

For accessibility issues or questions, please create an issue with the label `accessibility`.

---

**Last Updated**: 2025-11-10
**WCAG Level**: AA
**Compliance Status**: Compliant

## Touch Targets

All interactive elements meet the minimum touch target size of 44x44px:

```css
/* Global minimum touch target size */
button,
a,
input[type="checkbox"],
input[type="radio"],
select,
[role="button"],
[role="link"] {
  min-width: 44px;
  min-height: 44px;
}
```

### Spacing Between Touch Targets

Ensure adequate spacing between touch targets to prevent accidental activation:

```vue
<!-- Buttons with proper spacing -->
<div class="flex gap-3">
  <button class="btn-primary min-h-[44px]">Primary</button>
  <button class="btn-secondary min-h-[44px]">Secondary</button>
</div>
```

## Common Pitfalls

### ❌ Don't Do This

```vue
<!-- Missing ARIA label -->
<button @click="handleAction">
  <Icon name="close" />
</button>

<!-- No keyboard support -->
<div @click="handleClick">
  Click me
</div>

<!-- Poor color contrast -->
<p style="color: #999;">Low contrast text</p>

<!-- Missing label association -->
<label>Worker ID</label>
<input v-model="workerId" />

<!-- No screen reader announcement -->
<div v-if="loading">Loading...</div>
```

### ✅ Do This Instead

```vue
<!-- Proper ARIA label -->
<button @click="handleAction" aria-label="Close dialog">
  <Icon name="close" aria-hidden="true" />
</button>

<!-- Keyboard support added -->
<div 
  role="button"
  tabindex="0"
  @click="handleClick"
  @keydown.enter="handleClick"
  @keydown.space.prevent="handleClick"
  aria-label="Interactive element"
>
  Click me
</div>

<!-- Good color contrast -->
<p class="text-gray-900">High contrast text</p>

<!-- Proper label association -->
<label for="worker-id">Worker ID</label>
<input id="worker-id" v-model="workerId" />

<!-- Screen reader announcement -->
<div v-if="loading" role="status" aria-live="polite">
  <LoadingSpinner />
  <p>Loading tasks...</p>
</div>
```

## Best Practices Summary

### 1. Use Semantic HTML First
Always use the most appropriate HTML element before adding ARIA.

### 2. Progressive Enhancement
Build for accessibility first, then enhance visually.

### 3. Test Early and Often
- Test accessibility during development, not after
- Use automated tools in your workflow
- Do manual keyboard testing regularly
- Test with actual screen readers

### 4. Provide Multiple Ways to Navigate
- Skip links for keyboard users
- Navigation menus
- Search functionality
- Breadcrumbs

### 5. Don't Rely on Color Alone
Always provide additional visual or textual cues alongside color.

---

**Document Version**: 2.0  
**Last Updated**: 2025-11-10  
**Maintained By**: Worker12 (UX Review & Testing Specialist)  
**Review Schedule**: Monthly or when WCAG guidelines are updated
