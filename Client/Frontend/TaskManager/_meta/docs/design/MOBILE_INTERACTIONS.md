# Mobile Interaction Patterns

**Version**: 1.0  
**Last Updated**: 2025-11-09  
**Target Device**: Redmi 24115RA8EG (6.7" AMOLED, 2712x1220)  
**Platform**: Mobile Web (Progressive Web App)

---

## Overview

This document defines mobile-specific interaction patterns optimized for touch interfaces on the Redmi 24115RA8EG device. These patterns ensure a native-like experience within a web application.

---

## Touch Interactions

### 1. Tap (Primary Action)

**Definition**: Quick touch and release.

**Usage**: Primary action on any interactive element.

**Specifications**:
- **Minimum target size**: 44px × 44px
- **Recommended**: 48px × 48px
- **Spacing between targets**: 8px minimum
- **Response time**: < 100ms visual feedback
- **Haptic feedback**: Optional on critical actions

**Examples**:
```
Tap button       → Execute action
Tap card         → Navigate to detail
Tap tab          → Switch filter
Tap checkbox     → Toggle state
```

**Visual Feedback**:
```css
/* Active state */
transform: scale(0.98);
transition: transform 100ms ease-out;

/* Touch highlight (system) */
-webkit-tap-highlight-color: rgba(14, 165, 233, 0.1);
```

**Best Practices**:
- ✓ Instant visual feedback
- ✓ No double-tap zoom on buttons
- ✓ Clear touch boundaries
- ✗ Avoid tiny tap targets
- ✗ No hover-dependent features

---

### 2. Long Press (Secondary Action)

**Definition**: Touch and hold for 500ms+.

**Usage**: Reveal context menus, additional options.

**Specifications**:
- **Trigger time**: 500ms
- **Haptic feedback**: On trigger
- **Visual feedback**: Scale or shadow increase
- **Cancellation**: Drag away before trigger

**Examples**:
```
Long press task card    → Show context menu (future)
Long press image        → Save/share options
Long press text         → Select text
```

**Implementation**:
```javascript
let longPressTimer
const LONG_PRESS_DURATION = 500

onTouchStart() {
  longPressTimer = setTimeout(() => {
    triggerLongPress()
    hapticFeedback()
  }, LONG_PRESS_DURATION)
}

onTouchEnd() {
  clearTimeout(longPressTimer)
}
```

**Visual Feedback**:
```css
/* During long press */
@keyframes longPressRipple {
  0% { transform: scale(1); opacity: 0.3; }
  100% { transform: scale(1.1); opacity: 0; }
}
```

---

### 3. Swipe (Navigation/Action)

**Definition**: Touch, drag, and release in a direction.

**Types**:

#### Horizontal Swipe (Navigation)

**Usage**: Navigate between views, reveal actions.

**Specifications**:
- **Minimum distance**: 50px
- **Velocity threshold**: 0.5 px/ms
- **Response**: Immediate visual tracking
- **Completion**: Snap to position or cancel

**Examples**:
```
Swipe right on task  → Quick claim (future)
Swipe left on task   → Reveal actions (future)
Swipe between tabs   → Switch views (future)
```

**States**:
```
1. Touch Start    → Record position
2. Touch Move     → Track delta, show preview
3. Touch End      → Evaluate: commit or cancel
   - Distance > threshold & velocity > min → Commit
   - Otherwise → Cancel (spring back)
```

**Visual Feedback**:
```css
/* Swipe preview */
transform: translateX(${deltaX}px);
transition: none; /* During drag */

/* On release */
transition: transform 200ms cubic-bezier(0.4, 0, 0.2, 1);
```

#### Vertical Swipe (Scroll/Refresh)

**Usage**: Scroll content, pull-to-refresh.

**Specifications**:
- **Scroll**: Native behavior
- **Pull-to-refresh**: Custom at top of scroll
- **Overscroll**: Bounce effect (iOS-like)

---

### 4. Pull to Refresh

**Definition**: Pull down from top of scrollable content to reload.

**Usage**: Refresh task list, update data.

**Specifications**:
- **Trigger area**: Top of scrollable container
- **Pull distance**: 80px to trigger
- **Indicator**: Rotating arrow/spinner
- **Haptic**: On trigger (threshold reached)
- **Auto-dismiss**: On completion

**Flow**:
```
┌─────────────────────┐
│  Task List          │  Scroll position: 0
├─────────────────────┤
│  Task 1             │
└─────────────────────┘
        ↓ Pull down (touch + drag)
┌─────────────────────┐
│      ↓              │  Indicator appears
│  Release to refresh │  Distance: 40px
├─────────────────────┤
│  Task List          │
└─────────────────────┘
        ↓ Continue pulling
┌─────────────────────┐
│      ↻              │  Ready to refresh
│  Release to refresh │  Distance: 80px (threshold)
├─────────────────────┤  Haptic feedback
│  Task List          │
└─────────────────────┘
        ↓ Release
┌─────────────────────┐
│      ●              │  Loading
│   Refreshing...     │  API request
├─────────────────────┤
│  Task List          │
└─────────────────────┘
        ↓ Complete (1-2s)
┌─────────────────────┐
│  Task List          │  Updated data
│  Task 1 (new)       │  Indicator dismissed
└─────────────────────┘
```

**Implementation Considerations**:
- Detect scroll position = 0
- Track pull distance
- Threshold: 80px for trigger
- Prevent page scroll during pull
- Native overscroll bounce

---

### 5. Pinch to Zoom

**Definition**: Two-finger pinch/spread gesture.

**Usage**: Zoom images, maps (if needed).

**Specifications**:
- **Not recommended** for core UI
- **Use case**: Image gallery, diagrams
- **Accessibility**: Provide zoom controls too

**Current Scope**: Not in MVP (future enhancement).

---

### 6. Double Tap

**Definition**: Two rapid taps.

**Usage**: **Avoid** - Causes 300ms delay on older browsers.

**Alternative**: Use single tap for all actions.

**Exception**: Native behaviors (e.g., text selection).

---

## Thumb Zones

### Redmi 24115RA8EG Ergonomics

**Device**: 6.7" screen, 162.9mm × 75.5mm

**Comfortable Reach Zones** (Right-handed):

```
┌─────────────────────┐  Top: Hard to reach
│   🔴  Hard          │  Requires hand shift
│                     │
├─────────────────────┤  Middle: Easy to reach
│   🟢  Easy          │  Natural thumb position
│                     │
├─────────────────────┤  Bottom: Very easy
│   🟢  Natural       │  Prime real estate
│      [Nav Bar]      │
└─────────────────────┘
```

**Design Implications**:

1. **Critical Actions** → Bottom third
   - Primary buttons
   - Bottom navigation
   - FAB (Floating Action Button)

2. **Secondary Actions** → Middle third
   - Cards (scrollable)
   - List items
   - Content

3. **Informational** → Top third
   - Page title
   - Status indicators
   - Secondary info

### One-Handed Usage

**Principle**: Design for one-handed operation.

**Guidelines**:
- Bottom navigation (not top)
- Reachable actions
- No critical actions in top corners
- Content in natural scroll zone

**Reachability Map** (Right thumb):
```
┌────┬────┬────┬────┐
│ ⚠️ │ ⚠️ │ ⚠️ │ ⚠️ │  Very Hard
├────┼────┼────┼────┤
│ ⚠️ │ 🔶 │ 🔶 │ ⚠️ │  Hard
├────┼────┼────┼────┤
│ 🔶 │ ✅ │ ✅ │ 🔶 │  Good
├────┼────┼────┼────┤
│ ✅ │ ✅ │ ✅ │ ✅ │  Easy
└────┴────┴────┴────┘
        Center
       ↑ Best
```

---

## Touch Targets

### Minimum Sizes

**44px × 44px** - Absolute minimum (WCAG 2.1 AA)
```css
.touch-target {
  min-width: 44px;
  min-height: 44px;
}
```

**48px × 48px** - Recommended for primary actions
```css
.btn-primary {
  min-width: 48px;
  min-height: 48px;
}
```

**56px × 56px** - Large targets (FAB, important actions)
```css
.fab {
  width: 56px;
  height: 56px;
}
```

### Spacing

**Minimum gap**: 8px between touch targets
```css
.button-group {
  gap: 8px;
}
```

**Recommended gap**: 12px for comfortable tapping
```css
.toolbar {
  gap: 12px;
}
```

### Visual vs. Touch Area

**Principle**: Touch area ≥ Visual area

**Example**: Icon button
```
Visual icon: 24px × 24px
Touch area: 48px × 48px

┌─────────────┐
│             │  
│   ▶ Icon    │  Visual: 24px
│             │  Touch: 48px (padding)
└─────────────┘
```

**Implementation**:
```css
.icon-btn {
  width: 24px;
  height: 24px;
  padding: 12px; /* Expands touch area to 48px */
}
```

---

## Gestures

### Scroll

**Native behavior** - No custom implementation needed.

**Optimizations**:
- Momentum scrolling (iOS)
- Snap points (optional)
- Scroll position restoration

```css
/* Enable smooth momentum */
-webkit-overflow-scrolling: touch;

/* Snap scroll (optional) */
scroll-snap-type: y mandatory;
scroll-snap-align: start;
```

### Overscroll

**iOS-like bounce** - Visual feedback at scroll boundaries.

```css
/* Preserve overscroll behavior */
overscroll-behavior: auto;

/* Or contain within element */
overscroll-behavior: contain;
```

### Horizontal Scroll (Tabs)

**Use case**: Filter tabs, image carousel.

**Specifications**:
- Touch-draggable
- Snap to items (optional)
- Hide scrollbar
- Scroll indicators (shadows/gradients)

```css
.horizontal-scroll {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none; /* Firefox */
  -webkit-overflow-scrolling: touch;
}

.horizontal-scroll::-webkit-scrollbar {
  display: none; /* Chrome, Safari */
}
```

---

## Haptic Feedback

**Purpose**: Physical confirmation of actions.

**Browser Support**: Limited (iOS Safari only via Vibration API).

**Usage** (Progressive Enhancement):

### Light Tap
```javascript
if ('vibrate' in navigator) {
  navigator.vibrate(10) // 10ms
}
```

**Use cases**:
- Button tap
- Toggle switch
- Checkbox selection

### Medium Impact
```javascript
navigator.vibrate(20) // 20ms
```

**Use cases**:
- Task claimed
- Modal opened
- Important action

### Heavy Impact
```javascript
navigator.vibrate([30, 10, 30]) // Pattern
```

**Use cases**:
- Task completed (success)
- Error occurred
- Critical alert

### Success Pattern
```javascript
navigator.vibrate([10, 50, 10, 50, 20])
```

**Use case**: Task completion celebration.

**Implementation**:
```javascript
function hapticFeedback(type = 'light') {
  if (!('vibrate' in navigator)) return
  
  const patterns = {
    light: 10,
    medium: 20,
    heavy: 30,
    success: [10, 50, 10, 50, 20],
    error: [20, 100, 20]
  }
  
  navigator.vibrate(patterns[type])
}
```

**Accessibility**: Respect user preferences (disable if preferred).

---

## Responsive Touch Feedback

### Visual Feedback Types

#### 1. Scale Down (Press)
```css
.btn:active {
  transform: scale(0.98);
  transition: transform 100ms ease-out;
}
```

#### 2. Color Change
```css
.btn:active {
  background-color: var(--primary-700);
}
```

#### 3. Ripple Effect (Material Design)
```css
.btn {
  position: relative;
  overflow: hidden;
}

.btn::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transition: transform 0.5s;
}

.btn:active::after {
  transform: translate(-50%, -50%) scale(2);
}
```

#### 4. Shadow Lift (Cards)
```css
.card {
  transition: box-shadow 200ms, transform 200ms;
}

.card:active {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}
```

### Timing

**Instant**: < 100ms
- Color change
- Scale transform
- Tap highlight

**Quick**: 100-200ms
- Ripple start
- Shadow transition
- Icon animation

**Delayed**: 200-300ms
- Complex animations
- Page transitions
- Modal entrance

---

## Safe Areas

### iPhone Notch / Home Indicator

**CSS Environment Variables**:
```css
:root {
  --safe-area-top: env(safe-area-inset-top);
  --safe-area-bottom: env(safe-area-inset-bottom);
  --safe-area-left: env(safe-area-inset-left);
  --safe-area-right: env(safe-area-inset-right);
}
```

**Bottom Navigation**:
```css
.bottom-nav {
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
}
```

**Full-Screen Content**:
```css
.fullscreen {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
}
```

### Android Navigation Bar

**Transparent navigation**:
```html
<meta name="theme-color" content="#ffffff">
```

**Consider bottom nav height**:
- Android: ~48px
- iOS: ~34px (home indicator)
- Safe approach: `env(safe-area-inset-bottom)`

---

## Modal Interactions

### Bottom Sheet (Mobile)

**Behavior**:
- Slides up from bottom
- Backdrop dims content
- Drag down to dismiss
- Tap backdrop to dismiss (optional)

**Anatomy**:
```
┌─────────────────────┐
│                     │  Backdrop (dimmed)
│                     │
│  ┌──────────────┐  │
│  │ ──  Handle   │  │  Drag handle (optional)
│  │              │  │
│  │   Content    │  │  Modal content
│  │              │  │
│  │  [Actions]   │  │
│  └──────────────┘  │
└─────────────────────┘
```

**Interactions**:
1. **Tap backdrop** → Dismiss (if enabled)
2. **Drag handle down** → Dismiss
3. **Swipe content down** → Dismiss
4. **Tap cancel/close** → Dismiss

**States**:
```
Closed     → Hidden (translateY(100%))
Opening    → Animating in (200ms)
Open       → Visible (translateY(0))
Dragging   → Following touch
Closing    → Animating out (150ms)
```

---

## Loading States

### Skeleton Screens

**Purpose**: Show layout while loading.

**Example**:
```
┌──────────────────────┐
│ ▓▓▓▓▓▓▓▓▓░░░░░░░    │  Title placeholder
│ ▓▓▓▓░░░░░░░░        │  Subtitle
│                      │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓     │  Content
└──────────────────────┘
```

**Animation**:
```css
@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 0%,
    #f8f8f8 50%,
    #f0f0f0 100%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite;
}
```

### Progress Indicators

**Spinner**: Small, inline loading
**Progress Bar**: Known duration/progress
**Skeleton**: Layout-preserving placeholder

---

## Performance Considerations

### Scroll Performance

```css
/* Use transform for smooth animations */
transform: translateY(0);
will-change: transform; /* Use sparingly */

/* Avoid expensive properties */
/* ❌ */ top: 0; /* Triggers layout */
/* ✅ */ transform: translateY(0); /* GPU-accelerated */
```

### Touch Delay Removal

```css
/* Remove 300ms tap delay */
touch-action: manipulation;

/* Prevent zoom on double-tap */
touch-action: pan-y;
```

```html
<!-- Viewport meta for no delay -->
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
```

### Event Listeners

```javascript
// Use passive listeners for scroll/touch
element.addEventListener('touchstart', handler, { passive: true })
element.addEventListener('touchmove', handler, { passive: true })
```

---

## Accessibility

### Touch + Keyboard

**Support both**:
- Touch: Tap, swipe, long-press
- Keyboard: Enter, Space, Arrow keys
- Screen reader: Semantic HTML, ARIA

### Focus Management

```css
/* Visible focus for keyboard users */
:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* Hide focus for touch users */
:focus:not(:focus-visible) {
  outline: none;
}
```

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Testing

### Device Testing

**Primary**: Redmi 24115RA8EG
- Touch accuracy
- Scroll performance
- Gesture recognition

**Secondary**:
- iOS Safari (iPhone)
- Chrome Android
- Samsung Internet

### Testing Checklist

- [ ] All touch targets ≥ 44px
- [ ] No accidental taps (adequate spacing)
- [ ] Smooth scrolling (60fps)
- [ ] Pull-to-refresh works
- [ ] Haptic feedback (iOS)
- [ ] Safe areas respected
- [ ] No 300ms tap delay
- [ ] Works one-handed
- [ ] Landscape orientation (optional)

---

## Pattern Status

| Pattern             | Designed | Documented | Implemented | Tested |
|---------------------|----------|------------|-------------|--------|
| Tap                 | ✅       | ✅         | ✅          | ⏳     |
| Long Press          | ✅       | ✅         | ⏳          | ⏳     |
| Swipe               | ✅       | ✅         | ⏳          | ⏳     |
| Pull-to-Refresh     | ✅       | ✅         | ⏳          | ⏳     |
| Touch Targets       | ✅       | ✅         | ✅          | ⏳     |
| Haptic Feedback     | ✅       | ✅         | ⏳          | ⏳     |
| Bottom Sheet        | ✅       | ✅         | ⏳          | ⏳     |
| Skeleton Loading    | ✅       | ✅         | ⏳          | ⏳     |

---

**Version**: 1.0  
**Maintained by**: Worker11 (UX Design Specialist)  
**Testing by**: Worker12 (UX Testing) on Redmi 24115RA8EG  
**Last Updated**: 2025-11-09
