# Component Specifications

**Version**: 1.0  
**Last Updated**: 2025-11-09  
**Design System**: See [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md)  
**Target Device**: Redmi 24115RA8EG

---

## Overview

This document provides detailed specifications for all UI components in the TaskManager application. Each component includes:
- Visual specifications
- Behavior and interactions
- States and variants
- Accessibility requirements
- Implementation notes

---

## Base Components

### 1. BaseButton

**Purpose**: Primary interactive element for actions.

#### Variants

**Primary**
```
┌────────────────┐
│  Claim Task    │  Height: 44px min
└────────────────┘  Padding: 12px 16px
                    Background: primary-500
                    Text: white, 16px, semibold
                    Border radius: 8px
```

**Secondary**
```
┌────────────────┐
│  Cancel        │  Same size as primary
└────────────────┘  Background: white
                    Border: 2px solid primary-500
                    Text: primary-600
```

**Text Button**
```
Skip for now        No background
                    Text: primary-600
                    Padding: 12px 8px
                    Min height: 44px
```

**Destructive**
```
┌────────────────┐
│  Delete        │  Background: error-500
└────────────────┘  Text: white
                    Same sizing as primary
```

#### States

**Default**
- Background: primary-500
- Text: white
- Shadow: none

**Hover** (desktop)
- Background: primary-600
- Cursor: pointer

**Active** (pressed)
- Background: primary-700
- Transform: scale(0.98)

**Disabled**
- Background: neutral-300
- Text: neutral-500
- Cursor: not-allowed
- Opacity: 0.6

**Loading**
- Show spinner icon
- Disable interaction
- Maintain size
- Text: "Loading..." or keep original

#### Accessibility

- ✓ 44px x 44px minimum touch target
- ✓ Color contrast: 4.56:1 (white on primary-500)
- ✓ Focus ring: 2px solid primary-500, 2px offset
- ✓ ARIA: `role="button"`, `aria-disabled` when disabled
- ✓ Keyboard: Enter and Space trigger action

#### Props (Vue Component)

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'text' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  fullWidth?: boolean
  type?: 'button' | 'submit' | 'reset'
}
```

---

### 2. TaskCard

**Purpose**: Display task information in list view.

#### Anatomy

```
┌──────────────────────────────────────────────┐
│ ● Task Title                        [PENDING]│  Min height: 72px
│   ID: #1234                                  │  Padding: 16px
│   Priority: High | Attempts: 0/3            │  Background: white
│   ▓▓▓▓▓░░░░░ 50%                            │  Border radius: 12px
│   2h ago                                     │  Shadow: sm
└──────────────────────────────────────────────┘
```

#### Elements

**Status Dot**
- Size: 12px diameter
- Position: Left, aligned with title
- Colors:
  - Pending: warning-400 (#facc15)
  - Claimed: primary-500 (#0ea5e9)
  - Completed: success-500 (#22c55e)
  - Failed: error-500 (#ef4444)

**Title**
- Font: 16px semibold
- Color: neutral-900
- Max lines: 1 (truncate with ellipsis)

**Metadata**
- Font: 14px regular
- Color: neutral-500
- Format: "ID: #1234"
- Format: "Priority: {value} | Attempts: {n}/{max}"

**Progress Bar** (when status = claimed and progress > 0)
- Height: 8px
- Background: neutral-200
- Fill: primary-500
- Border radius: 4px (full)
- Text: 12px, neutral-500, "{progress}% complete"

**Status Badge**
- Position: Top right
- Padding: 4px 8px
- Border radius: 4px
- Font: 12px semibold
- Background + text colors:
  - Pending: warning-100 bg, warning-800 text
  - Claimed: primary-100 bg, primary-800 text
  - Completed: success-100 bg, success-800 text
  - Failed: error-100 bg, error-800 text

**Timestamp**
- Font: 12px regular
- Color: neutral-500
- Format: Relative (e.g., "2h ago", "Just now")
- Position: Below badge

#### States

**Default**
- Background: white
- Shadow: sm
- Border: none

**Hover** (desktop)
- Shadow: md
- Transform: translateY(-2px)
- Cursor: pointer
- Transition: 200ms ease-out

**Active** (pressed)
- Transform: translateY(0)
- Shadow: sm

**Selected** (optional)
- Border: 2px solid primary-500
- Shadow: md

#### Interactions

- **Tap**: Navigate to task detail
- **Long press** (future): Show context menu
- **Swipe right** (future): Quick claim
- **Swipe left** (future): Show actions

#### Accessibility

- ✓ Full card is tappable (72px minimum height)
- ✓ Semantic HTML: `<article>` or `<div role="article">`
- ✓ Status communicated via text + color (not color alone)
- ✓ Focus ring when keyboard focused

---

### 3. BaseInput

**Purpose**: Text input for forms.

#### Anatomy

```
Label Text
┌────────────────────────────────────┐
│ Placeholder text                   │  Height: 44px min
└────────────────────────────────────┘  Padding: 12px
Error message text                      Border: 2px solid
                                        Border radius: 8px
```

#### States

**Default**
- Border: neutral-200
- Background: white
- Text: neutral-900, 16px

**Focus**
- Border: primary-500
- Box shadow: 0 0 0 3px rgba(14, 165, 233, 0.1)
- Outline: none

**Error**
- Border: error-500
- Box shadow: 0 0 0 3px rgba(239, 68, 68, 0.1)

**Disabled**
- Background: neutral-100
- Border: neutral-200
- Text: neutral-500
- Cursor: not-allowed

**Filled** (has value)
- Border: neutral-300

#### Elements

**Label**
- Font: 14px medium
- Color: neutral-700
- Margin bottom: 8px
- Required indicator: `*` in error-500

**Input Field**
- Font size: 16px (prevents iOS zoom)
- Autocapitalize: off (for email, username)
- Autocorrect: off (for technical fields)

**Error Message**
- Font: 14px regular
- Color: error-600
- Margin top: 4px
- Icon: ⚠️ optional

**Helper Text**
- Font: 14px regular
- Color: neutral-500
- Margin top: 4px

#### Types

**Text**
```html
<input type="text" />
```

**Email**
```html
<input type="email" inputmode="email" />
```

**Number**
```html
<input type="number" inputmode="numeric" />
```

**Password**
```html
<input type="password" />
<!-- Toggle visibility icon -->
```

#### Accessibility

- ✓ Label associated with `for` attribute
- ✓ `aria-describedby` for error/helper text
- ✓ `aria-invalid` when error
- ✓ `aria-required` for required fields
- ✓ 16px font prevents iOS zoom
- ✓ Focus visible

---

### 4. StatusBadge

**Purpose**: Display task status.

#### Variants

**Pending**
```
┌─────────┐
│ PENDING │  Background: warning-100
└─────────┘  Text: warning-800
             Uppercase, 12px semibold
```

**Claimed**
```
┌─────────┐
│ CLAIMED │  Background: primary-100
└─────────┘  Text: primary-800
```

**Completed**
```
┌───────────┐
│ COMPLETED │  Background: success-100
└───────────┘  Text: success-800
```

**Failed**
```
┌────────┐
│ FAILED │  Background: error-100
└────────┘  Text: error-800
```

#### Specifications

- Padding: 4px 8px
- Border radius: 4px
- Font: 12px semibold, uppercase
- Letter spacing: 0.05em
- White space: nowrap
- Display: inline-block

#### Accessibility

- ✓ Color + text (not color alone)
- ✓ Contrast ratio: > 4.5:1
- ✓ Screen reader reads status text

---

### 5. LoadingSpinner

**Purpose**: Indicate loading state.

#### Specifications

```
    ╱──╲
   │    │    Size: 32px (default)
    ╲──╱     Border: 4px
             Color: primary-500
             Animation: spin 1s linear infinite
```

#### Sizes

- `sm`: 16px (button spinners)
- `md`: 32px (default)
- `lg`: 48px (page loading)

#### Animation

```css
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

#### Accessibility

- ✓ ARIA: `role="status"`, `aria-live="polite"`
- ✓ Screen reader text: "Loading..."
- ✓ Reduced motion: Show static icon instead

---

## Page Components

### 6. Bottom Navigation

**Purpose**: Primary navigation for mobile.

#### Anatomy

```
┌─────────┬─────────┬─────────┐
│  Tasks  │ Workers │Settings │  Height: 56px + safe area
│    ●    │    ○    │    ○    │  Background: white
└─────────┴─────────┴─────────┘  Border top: 1px neutral-200
                                  Position: fixed bottom
```

#### Elements

**Nav Item**
- Width: Flex 1 (equal distribution)
- Height: 56px
- Display: Column (icon + label)
- Alignment: Center
- Min height: 44px (touch target)

**Icon**
- Size: 24px
- Color: neutral-600 (inactive), primary-600 (active)

**Label**
- Font: 12px medium
- Color: Same as icon
- Margin top: 2px

**Active Indicator**
- Color change to primary-600
- Optional: Dot above icon (4px, primary-500)

#### States

**Inactive**
- Icon: neutral-600
- Label: neutral-600

**Active**
- Icon: primary-600
- Label: primary-600
- Font weight: 600

**Pressed**
- Background: neutral-100
- Border radius: 8px (inset)

#### Safe Area (iOS)

```css
padding-bottom: env(safe-area-inset-bottom);
```

Ensures navigation doesn't overlap iPhone home indicator.

#### Accessibility

- ✓ Semantic: `<nav>` element
- ✓ Each item: `<a>` or `<button>`
- ✓ ARIA: `aria-current="page"` for active
- ✓ Touch targets: 44px height
- ✓ Keyboard navigable

---

### 7. Page Header

**Purpose**: Page title and primary actions.

#### Anatomy

```
┌──────────────────────────────────────┐
│ ← TaskManager               [+] [⚙] │  Height: 56px
└──────────────────────────────────────┘  Background: white
                                          Shadow: sm
                                          Sticky: top 0
```

#### Elements

**Back Button** (optional)
- Icon: ← (24px)
- Size: 44px x 44px
- Position: Left
- Color: neutral-700

**Title**
- Font: 20px semibold
- Color: neutral-900
- Position: Center or left (if no back button)

**Actions** (optional)
- Icon buttons: 44px x 44px
- Position: Right
- Color: neutral-700
- Max: 2 icons (to maintain spacing)

#### Variations

**Simple**
```
┌──────────────────────────────────────┐
│ TaskManager                          │
└──────────────────────────────────────┘
```

**With Back**
```
┌──────────────────────────────────────┐
│ ← Task Details                       │
└──────────────────────────────────────┘
```

**With Actions**
```
┌──────────────────────────────────────┐
│ TaskManager                 [+] [⚙] │
└──────────────────────────────────────┘
```

#### Behavior

- **Sticky**: Remains at top on scroll
- **Z-index**: 10 (above content)
- **Safe area**: Padding top for notch devices

---

### 8. FilterTabs

**Purpose**: Filter task list by status.

#### Anatomy

```
┌──────┬──────┬──────┬──────┬──────┐
│ All  │Pending│Claimed│Done│Failed│  Height: 40px
│ (12) │  (5) │  (3) │ (4) │  (0) │  Horizontal scroll
└──────┴──────┴──────┴──────┴──────┘  Gap: 8px
```

#### Tab Specifications

**Active Tab**
- Background: primary-500
- Text: white, 14px semibold
- Padding: 8px 16px
- Border radius: 8px
- Count: Opacity 0.75

**Inactive Tab**
- Background: white
- Text: neutral-700, 14px medium
- Border: 1px solid neutral-200
- Count: neutral-500

**Hover** (desktop)
- Background: neutral-100 (inactive only)

**Pressed**
- Transform: scale(0.98)

#### Container

- Overflow: X scroll (mobile)
- Scrollbar: Hidden
- Padding: 0 16px
- Gap: 8px
- White space: nowrap

#### Accessibility

- ✓ ARIA: `role="tablist"`
- ✓ Each tab: `role="tab"`, `aria-selected`
- ✓ Keyboard: Arrow keys to navigate
- ✓ Touch target: 40px height minimum

---

### 9. EmptyState

**Purpose**: Display when no content available.

#### Anatomy

```
       ┌───┐
       │   │     Icon (48px)
       └───┘
                 
   No tasks found        Title (16px semibold)
                         
  Try claiming a task    Message (14px regular)
  from the list          
                         
┌─────────────────┐      Action (optional)
│  Browse Tasks   │
└─────────────────┘
```

#### Specifications

**Icon**
- Size: 48px
- Color: neutral-400
- Common icons: 📭, 🔍, ⚠️

**Title**
- Font: 16px semibold
- Color: neutral-700
- Margin: 16px top

**Message**
- Font: 14px regular
- Color: neutral-500
- Max width: 300px
- Text align: center
- Margin: 8px top

**Action Button** (optional)
- Primary or secondary variant
- Margin: 24px top

#### Variations

**No Tasks**
```
📭
No tasks found
There are no tasks matching your filter
```

**No Results**
```
🔍
No search results
Try different keywords
```

**Error State**
```
⚠️
Something went wrong
Please try again later
[Retry]
```

---

### 10. Modal/Dialog

**Purpose**: Overlay for focused tasks.

#### Anatomy (Mobile)

```
┌──────────────────────────────────┐
│ ×                                │  Header: 56px
│ Confirm Action                   │  
├──────────────────────────────────┤
│                                  │  Content: Variable
│ Are you sure you want to         │  Padding: 24px
│ complete this task?              │  
│                                  │  
│ This action cannot be undone.    │
│                                  │
├──────────────────────────────────┤
│ [Cancel]        [Confirm]        │  Footer: 72px
└──────────────────────────────────┘  
```

#### Specifications

**Backdrop**
- Background: rgba(0, 0, 0, 0.5)
- Position: fixed, full screen
- Z-index: 1000
- Tap to dismiss (optional)

**Modal Container**
- Background: white
- Border radius: 16px (desktop), 16px top only (mobile)
- Shadow: xl
- Max width: 480px (desktop)
- Width: 100% (mobile)
- Position: Center (desktop), bottom (mobile)

**Header**
- Height: 56px
- Padding: 16px 24px
- Border bottom: 1px solid neutral-200

**Close Button**
- Icon: × (24px)
- Size: 44px x 44px
- Position: Top right
- Color: neutral-600

**Title**
- Font: 18px semibold
- Color: neutral-900

**Content**
- Padding: 24px
- Max height: 60vh
- Overflow: Scroll

**Footer**
- Padding: 16px 24px
- Border top: 1px solid neutral-200
- Buttons: Flex, gap 12px
- Primary action: Right

#### Animations

**Entrance**
```css
/* Backdrop */
opacity: 0 → 1 (200ms)

/* Modal */
transform: translateY(100%) → translateY(0)  /* Mobile */
transform: scale(0.95) → scale(1)            /* Desktop */
opacity: 0 → 1
duration: 200ms ease-out
```

**Exit**
- Reverse of entrance
- Duration: 150ms

#### Accessibility

- ✓ ARIA: `role="dialog"`, `aria-modal="true"`
- ✓ Focus trap: Keep focus within modal
- ✓ Initial focus: First focusable element or close button
- ✓ Escape key: Close modal
- ✓ Return focus: To trigger element on close
- ✓ Screen reader: Announce modal title

---

## Responsive Behavior

### Mobile (< 640px)

- Single column layouts
- Bottom navigation visible
- Modals slide from bottom
- Full-width cards
- Horizontal scroll for tabs

### Tablet (640px - 1023px)

- 2-column grids for task cards
- Side navigation optional
- Modals centered
- Increased padding (20px)

### Desktop (1024px+)

- Sidebar + main content
- Hover states active
- Modals centered, max 480px
- Keyboard shortcuts
- Larger spacing

---

## Performance Considerations

### Rendering

- **Virtual scrolling**: For lists > 50 items
- **Lazy loading**: Images and heavy components
- **Debounce**: Search and filter inputs (300ms)

### Animations

- Use `transform` and `opacity` only
- Avoid animating `width`, `height`, `top`, `left`
- Respect `prefers-reduced-motion`

### Touch Feedback

- Minimum 44px x 44px targets
- Instant visual feedback (< 100ms)
- Haptic feedback (if supported)

---

## Component Status

| Component        | Design | Spec | Implementation | Tests | Status |
|------------------|--------|------|----------------|-------|--------|
| BaseButton       | ✅     | ✅   | ⏳             | ⏳    | Ready  |
| TaskCard         | ✅     | ✅   | ⏳             | ⏳    | Ready  |
| BaseInput        | ✅     | ✅   | ⏳             | ⏳    | Ready  |
| StatusBadge      | ✅     | ✅   | ⏳             | ⏳    | Ready  |
| LoadingSpinner   | ✅     | ✅   | ⏳             | ⏳    | Ready  |
| BottomNavigation | ✅     | ✅   | ⏳             | ⏳    | Ready  |
| PageHeader       | ✅     | ✅   | ⏳             | ⏳    | Ready  |
| FilterTabs       | ✅     | ✅   | ⏳             | ⏳    | Ready  |
| EmptyState       | ✅     | ✅   | ⏳             | ⏳    | Ready  |
| Modal            | ✅     | ✅   | ⏳             | ⏳    | Ready  |

---

**Version**: 1.0  
**Maintained by**: Worker11 (UX Design Specialist)  
**Next Review**: Worker12 (UX Testing) + Worker03 (Implementation)  
**Last Updated**: 2025-11-09
