# Mobile Interaction Patterns

**Version**: 1.0.0  
**Last Updated**: 2025-11-09  
**Design System**: [Design System](DESIGN_SYSTEM.md)

---

## Table of Contents

1. [Touch Gestures](#touch-gestures)
2. [Swipe Actions](#swipe-actions)
3. [Pull-to-Refresh](#pull-to-refresh)
4. [Bottom Sheets](#bottom-sheets)
5. [Toast Notifications](#toast-notifications)
6. [Haptic Feedback](#haptic-feedback)
7. [Scrolling & Pagination](#scrolling--pagination)

---

## Touch Gestures

### Tap

**Purpose**: Primary interaction method

**Specifications**:
- **Touch Target**: Minimum 44x44px (WCAG)
- **Feedback Timing**: < 100ms
- **Visual Feedback**: Background color change or scale

**Implementation**:
```css
.touchable {
  min-width: 44px;
  min-height: 44px;
  cursor: pointer;
  transition: background-color 100ms ease-out;
}

.touchable:active {
  background-color: rgba(0, 0, 0, 0.05);
  transform: scale(0.98);
}
```

**Use Cases**:
- Opening task details
- Clicking buttons
- Selecting options
- Navigating

---

### Long Press

**Purpose**: Reveal context menu or additional actions

**Specifications**:
- **Trigger Duration**: 500ms
- **Visual Feedback**: Scale animation + subtle vibration
- **Cancel**: If finger moves > 10px before trigger

**Implementation**:
```javascript
let longPressTimer;
const LONG_PRESS_DURATION = 500;

element.addEventListener('touchstart', (e) => {
  longPressTimer = setTimeout(() => {
    // Trigger long press action
    showContextMenu();
    if (navigator.vibrate) {
      navigator.vibrate(50);
    }
  }, LONG_PRESS_DURATION);
});

element.addEventListener('touchend', () => {
  clearTimeout(longPressTimer);
});

element.addEventListener('touchmove', () => {
  clearTimeout(longPressTimer);
});
```

**Use Cases**:
- Opening context menu on task cards
- Quick actions menu
- Advanced options

---

### Double Tap

**Purpose**: Zoom or toggle view (limited use)

**Specifications**:
- **Time Window**: 300ms between taps
- **Feedback**: Immediate visual change
- **Avoid**: Can conflict with single tap

**Implementation**:
```javascript
let lastTap = 0;
const DOUBLE_TAP_DELAY = 300;

element.addEventListener('touchend', (e) => {
  const currentTime = new Date().getTime();
  const tapLength = currentTime - lastTap;
  
  if (tapLength < DOUBLE_TAP_DELAY && tapLength > 0) {
    // Double tap detected
    handleDoubleTap();
    e.preventDefault();
  }
  
  lastTap = currentTime;
});
```

**Use Cases**:
- Zoom images (task attachments)
- Toggle details view
- **Recommendation**: Use sparingly

---

### Pinch to Zoom

**Purpose**: Zoom in/out on images or content

**Specifications**:
- **Zoom Range**: 0.5x - 3x
- **Animation**: Smooth (60fps)
- **Reset**: Double tap to reset to 1x

**Implementation**:
```javascript
let initialDistance = 0;
let currentScale = 1;

element.addEventListener('touchstart', (e) => {
  if (e.touches.length === 2) {
    initialDistance = getDistance(e.touches[0], e.touches[1]);
  }
});

element.addEventListener('touchmove', (e) => {
  if (e.touches.length === 2) {
    const currentDistance = getDistance(e.touches[0], e.touches[1]);
    const scale = currentDistance / initialDistance;
    currentScale = Math.min(Math.max(scale, 0.5), 3);
    element.style.transform = `scale(${currentScale})`;
  }
});

function getDistance(touch1, touch2) {
  const dx = touch1.clientX - touch2.clientX;
  const dy = touch1.clientY - touch2.clientY;
  return Math.sqrt(dx * dx + dy * dy);
}
```

**Use Cases**:
- Viewing task images
- Reading detailed content
- Chart/graph inspection

---

## Swipe Actions

### Swipe Right (Quick Claim)

**Purpose**: Quick action to claim a pending task

**Specifications**:
- **Trigger Distance**: 80px
- **Animation**: Slide + reveal (200ms)
- **Feedback**: Haptic feedback on trigger
- **Auto-complete**: Swipe continues to edge

**Visual Design**:
```
┌──────────────────────────────┐
│ [Claim] ← ● Task Name        │ ← Revealed action
└──────────────────────────────┘
```

**Implementation**:
```javascript
let startX = 0;
let currentX = 0;
const SWIPE_THRESHOLD = 80;

card.addEventListener('touchstart', (e) => {
  startX = e.touches[0].clientX;
});

card.addEventListener('touchmove', (e) => {
  currentX = e.touches[0].clientX;
  const diffX = currentX - startX;
  
  if (diffX > 0 && diffX < 120) {
    // Slide card to reveal action
    card.style.transform = `translateX(${diffX}px)`;
    
    // Change background color as threshold approaches
    const opacity = Math.min(diffX / SWIPE_THRESHOLD, 1);
    card.style.backgroundColor = `rgba(34, 197, 94, ${opacity * 0.1})`;
  }
});

card.addEventListener('touchend', (e) => {
  const diffX = currentX - startX;
  
  if (diffX > SWIPE_THRESHOLD) {
    // Trigger claim action
    claimTask();
    card.style.transform = 'translateX(100%)';
    setTimeout(() => card.remove(), 300);
  } else {
    // Reset position
    card.style.transform = 'translateX(0)';
    card.style.backgroundColor = '';
  }
});
```

**Use Cases**:
- Quick claim pending tasks
- Fast workflow for experienced users

---

### Swipe Left (Quick Actions)

**Purpose**: Reveal additional actions menu

**Specifications**:
- **Trigger Distance**: 60px (just reveal)
- **Actions Shown**: Complete, Fail, View
- **Auto-hide**: Tap elsewhere to hide

**Visual Design**:
```
┌──────────────────────────────┐
│ Task Name → [✓] [✗] [···]    │ ← Revealed actions
└──────────────────────────────┘
```

**Implementation**:
```javascript
// Similar to swipe right, but reveal buttons on left swipe
// Actions: Complete (green), Fail (red), More (gray)
```

**Use Cases**:
- Quick complete claimed tasks
- Report failures
- Access more options

---

## Pull-to-Refresh

**Purpose**: Refresh task list data

**Specifications**:
- **Trigger Distance**: 80px
- **Loading Spinner**: Appears at 60px
- **Animation**: Smooth elastic pull
- **Timing**: Min 500ms loading indicator

**Visual Design**:
```
     ↓ Pull to refresh
┌──────────────────────────────┐
│         ◌ Loading...         │ ← Spinner appears
├──────────────────────────────┤
│ Task cards below...          │
```

**Implementation**:
```javascript
let startY = 0;
let pulling = false;
const TRIGGER_DISTANCE = 80;

container.addEventListener('touchstart', (e) => {
  if (container.scrollTop === 0) {
    startY = e.touches[0].clientY;
    pulling = true;
  }
});

container.addEventListener('touchmove', (e) => {
  if (!pulling) return;
  
  const currentY = e.touches[0].clientY;
  const pullDistance = currentY - startY;
  
  if (pullDistance > 0 && pullDistance < 120) {
    // Show pull indicator
    const opacity = Math.min(pullDistance / TRIGGER_DISTANCE, 1);
    refreshIndicator.style.opacity = opacity;
    refreshIndicator.style.transform = `translateY(${pullDistance}px)`;
  }
});

container.addEventListener('touchend', (e) => {
  if (pulling) {
    const pullDistance = currentY - startY;
    
    if (pullDistance > TRIGGER_DISTANCE) {
      // Trigger refresh
      refreshData();
      showLoadingSpinner();
    } else {
      // Reset
      refreshIndicator.style.opacity = 0;
      refreshIndicator.style.transform = 'translateY(0)';
    }
    
    pulling = false;
  }
});
```

**Use Cases**:
- Refresh task list
- Update task status
- Sync with server

---

## Bottom Sheets

**Purpose**: Mobile-friendly modals

**Specifications**:
- **Height**: 40% - 80% of viewport
- **Border Radius**: 16px (top corners)
- **Handle**: 32x4px gray bar at top
- **Backdrop**: Semi-transparent (rgba(0,0,0,0.5))

**Interactions**:
- **Open**: Slide up from bottom (300ms)
- **Close**: Swipe down, tap backdrop, tap close
- **Resize**: Drag handle to adjust height (optional)

**Implementation**:
```css
.bottom-sheet {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  max-height: 80vh;
  background: white;
  border-radius: 16px 16px 0 0;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(100%);
  transition: transform 300ms ease-out;
  z-index: 1000;
}

.bottom-sheet.open {
  transform: translateY(0);
}

.sheet-handle {
  width: 32px;
  height: 4px;
  background: #d1d5db;
  border-radius: 2px;
  margin: 12px auto;
}

.sheet-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 300ms ease-out;
  z-index: 999;
}

.sheet-backdrop.open {
  opacity: 1;
}
```

**Use Cases**:
- Task claim confirmation
- Task completion form
- Filters and settings
- Action confirmations

---

## Toast Notifications

**Purpose**: Brief, non-intrusive feedback

**Specifications**:
- **Duration**: 3s (info), 5s (error), Auto (success)
- **Position**: Bottom (mobile), Top (desktop)
- **Height**: Min 48px
- **Animation**: Slide in + fade (200ms)

**Types**:
1. **Success**: Green accent, checkmark icon
2. **Error**: Red accent, X icon
3. **Info**: Blue accent, info icon
4. **Warning**: Orange accent, warning icon

**Implementation**:
```javascript
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${getIcon(type)}</span>
    <span class="toast-message">${message}</span>
    <button class="toast-close" aria-label="Close">×</button>
  `;
  
  document.body.appendChild(toast);
  
  // Trigger animation
  setTimeout(() => toast.classList.add('show'), 10);
  
  // Auto-dismiss
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 200);
  }, duration);
  
  // Manual dismiss
  toast.querySelector('.toast-close').addEventListener('click', () => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 200);
  });
}
```

**Use Cases**:
- Task claimed successfully
- Operation completed
- Error occurred
- Network status

---

## Haptic Feedback

**Purpose**: Tactile feedback for actions

**Specifications**:
- **Duration**: 10-50ms
- **Intensity**: Light (10ms), Medium (25ms), Heavy (50ms)
- **Use Sparingly**: Only for important actions

**Implementation**:
```javascript
function hapticFeedback(type = 'light') {
  if (!navigator.vibrate) return;
  
  const patterns = {
    light: 10,
    medium: 25,
    heavy: 50,
    success: [10, 50, 10],
    error: [50, 100, 50]
  };
  
  navigator.vibrate(patterns[type] || 10);
}
```

**Use Cases**:
- Task claimed: `hapticFeedback('success')`
- Task completed: `hapticFeedback('success')`
- Error occurred: `hapticFeedback('error')`
- Long press trigger: `hapticFeedback('medium')`

**Best Practices**:
- Always make optional (settings toggle)
- Respect system preferences
- Don't overuse
- Test on actual devices

---

## Scrolling & Pagination

### Infinite Scroll

**Purpose**: Load more tasks as user scrolls

**Specifications**:
- **Trigger Point**: 200px from bottom
- **Loading Indicator**: Spinner at bottom
- **Batch Size**: 20 items
- **Error Handling**: Retry button if load fails

**Implementation**:
```javascript
let loading = false;
let hasMore = true;

window.addEventListener('scroll', () => {
  if (loading || !hasMore) return;
  
  const scrollPosition = window.innerHeight + window.scrollY;
  const threshold = document.documentElement.scrollHeight - 200;
  
  if (scrollPosition >= threshold) {
    loading = true;
    loadMoreTasks()
      .then(tasks => {
        appendTasks(tasks);
        hasMore = tasks.length > 0;
        loading = false;
      })
      .catch(error => {
        showError('Failed to load more tasks');
        loading = false;
      });
  }
});
```

### Virtual Scrolling

**Purpose**: Optimize large lists (> 100 items)

**Specifications**:
- Only render visible items + buffer
- Reuse DOM elements
- Maintain scroll position

**Use Cases**:
- Very long task lists
- Performance optimization

---

**Created By**: Worker11 (UX Design Specialist)  
**Date**: 2025-11-09  
**Status**: ✅ Complete  
**Version**: 1.0.0
