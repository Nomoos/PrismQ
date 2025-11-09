# Component Specifications

**Version**: 1.0.0  
**Last Updated**: 2025-11-09  
**Design System**: [Design System](../DESIGN_SYSTEM.md)

---

## Table of Contents

1. [Task Card](#task-card)
2. [Buttons](#buttons)
3. [Form Inputs](#form-inputs)
4. [Navigation](#navigation)
5. [Modals & Sheets](#modals--sheets)
6. [Badges & Status Indicators](#badges--status-indicators)
7. [Loading States](#loading-states)
8. [Empty States](#empty-states)
9. [Toast Notifications](#toast-notifications)

---

## Task Card

### Purpose
Display task information in list views with status, priority, and quick actions.

### Specifications

**Dimensions**:
- Minimum height: 72px (touch-friendly)
- Padding: 16px
- Margin bottom: 12px
- Border radius: 8px

**Layout**:
```
┌─────────────────────────────────────┐
│ ● Task Type              [Status]   │
│ ID: 12345                           │
│ Priority: High | Attempts: 1/3      │
│ ──────────────────── 45% (if active)│
│ Created: 2h ago                     │
└─────────────────────────────────────┘
```

**States**:
1. **Default**: White background, light gray border, shadow-sm
2. **Hover**: shadow-md, slight lift (transform: translateY(-2px))
3. **Active/Pressed**: shadow-sm, no transform
4. **Claimed**: Warning-50 background
5. **Completed**: Success-50 background
6. **Failed**: Error-50 background

**Visual Specifications**:

```css
.task-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  min-height: 72px;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  transition: box-shadow 200ms ease-out,
              transform 200ms ease-out;
  cursor: pointer;
}

.task-card:hover {
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1),
              0 2px 4px -2px rgb(0 0 0 / 0.1);
  transform: translateY(-2px);
}

.task-card.claimed {
  background: #fffbeb;
  border-color: #fef3c7;
}

.task-card.completed {
  background: #f0fdf4;
  border-color: #dcfce7;
}

.task-card.failed {
  background: #fef2f2;
  border-color: #fee2e2;
}
```

**Content Elements**:

1. **Status Indicator** (Circle):
   - Size: 12px diameter
   - Position: Top-left, inline with title
   - Colors: Pending (blue), Claimed (orange), Completed (green), Failed (red)

2. **Task Type** (Title):
   - Font: 16px, font-weight: 600, color: gray-900
   - Truncate with ellipsis if too long

3. **Task ID**:
   - Font: 14px, color: gray-500
   - Format: "ID: {number}"

4. **Metadata Row**:
   - Font: 14px, color: gray-600
   - Format: "Priority: {level} | Attempts: {current}/{max}"

5. **Progress Bar** (if claimed and progress > 0):
   - Height: 8px
   - Background: gray-200
   - Foreground: primary-500
   - Border radius: 4px (full)
   - Margin top: 8px

6. **Status Badge**:
   - Position: Top-right
   - Padding: 4px 8px
   - Font: 12px, font-weight: 500
   - Border radius: 4px

7. **Timestamp**:
   - Font: 12px, color: gray-500
   - Format: Relative time (e.g., "2h ago")

**Interactions**:
- **Tap**: Navigate to task detail view
- **Swipe Right**: Quick claim (pending tasks only)
- **Swipe Left**: Reveal quick actions menu

**Accessibility**:
- Full card is focusable and keyboard accessible
- Screen reader announces: "{Task type}, {status}, priority {level}"
- Focus indicator: 2px primary-500 outline with 2px offset
- Minimum tap target: 72px height ensures > 44px

---

## Buttons

### Primary Button

**Purpose**: Main call-to-action (Claim, Complete, Submit)

**Specifications**:
- Height: 44px (minimum touch target)
- Padding: 12px 24px
- Font: 16px, font-weight: 600
- Border radius: 8px
- Background: primary-500
- Text color: white
- Shadow: shadow-sm

**States**:
```css
.btn-primary {
  height: 44px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  background: #0ea5e9;
  color: #ffffff;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  transition: background-color 150ms ease-out;
}

.btn-primary:hover {
  background: #0284c7;
}

.btn-primary:active {
  background: #0369a1;
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}
```

### Secondary Button

**Purpose**: Secondary actions (Cancel, Back)

**Specifications**:
- Height: 44px
- Padding: 12px 24px
- Font: 16px, font-weight: 600
- Border radius: 8px
- Background: white
- Text color: gray-700
- Border: 1px solid gray-300

```css
.btn-secondary {
  height: 44px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  background: #ffffff;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}
```

### Danger Button

**Purpose**: Destructive actions (Fail Task, Delete)

**Specifications**:
- Same dimensions as Primary Button
- Background: error-500
- Text color: white

```css
.btn-danger {
  height: 44px;
  padding: 12px 24px;
  background: #ef4444;
  color: #ffffff;
}

.btn-danger:hover {
  background: #dc2626;
}
```

### Icon Button

**Purpose**: Icon-only actions (Close, Menu, More)

**Specifications**:
- Size: 44x44px (minimum touch target)
- Icon size: 24px
- Border radius: 8px (square) or 50% (circular)
- Background: transparent (default)

```css
.btn-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: transparent;
  color: #6b7280;
}

.btn-icon:hover {
  background: #f3f4f6;
}
```

**Accessibility**:
- All buttons must have aria-label if no visible text
- Minimum 44x44px touch target
- Focus indicator: 2px outline

---

## Form Inputs

### Text Input

**Purpose**: Single-line text entry

**Specifications**:
- Height: 44px (minimum touch target)
- Padding: 12px 16px
- Font: 16px (prevents iOS zoom)
- Border radius: 8px
- Border: 1px solid gray-300
- Background: white

```css
.input-text {
  height: 44px;
  padding: 12px 16px;
  font-size: 16px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #111827;
  width: 100%;
}

.input-text:focus {
  outline: 2px solid #0ea5e9;
  outline-offset: 0;
  border-color: #0ea5e9;
}

.input-text:disabled {
  background: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
}

.input-text.error {
  border-color: #ef4444;
}
```

### Textarea

**Purpose**: Multi-line text entry

**Specifications**:
- Min-height: 88px (2 lines)
- Padding: 12px 16px
- Font: 16px
- Border radius: 8px
- Resize: vertical only

```css
.input-textarea {
  min-height: 88px;
  padding: 12px 16px;
  font-size: 16px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  resize: vertical;
}
```

### Select / Dropdown

**Purpose**: Choose from predefined options

**Specifications**:
- Height: 44px
- Padding: 12px 16px
- Font: 16px
- Border radius: 8px
- Chevron icon: right side

```css
.input-select {
  height: 44px;
  padding: 12px 16px;
  font-size: 16px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  appearance: none;
  background-image: url("data:image/svg+xml,..."); /* chevron */
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 40px;
}
```

### Checkbox

**Purpose**: Boolean selection

**Specifications**:
- Size: 20x20px
- Border radius: 4px
- Border: 2px solid gray-400
- Checkmark: primary-500

```css
.input-checkbox {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 2px solid #9ca3af;
  appearance: none;
  cursor: pointer;
}

.input-checkbox:checked {
  background: #0ea5e9;
  border-color: #0ea5e9;
  background-image: url("data:image/svg+xml,..."); /* checkmark */
}
```

### Label

**Purpose**: Input labels

**Specifications**:
- Font: 14px, font-weight: 500
- Color: gray-700
- Margin-bottom: 8px
- Display: block

```css
.input-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.input-label.required::after {
  content: " *";
  color: #ef4444;
}
```

### Error Message

**Purpose**: Validation feedback

**Specifications**:
- Font: 14px
- Color: error-600
- Margin-top: 4px

```css
.input-error {
  font-size: 14px;
  color: #dc2626;
  margin-top: 4px;
}
```

**Accessibility**:
- All inputs must have associated labels
- Error messages: aria-describedby
- Required fields: aria-required="true"
- Invalid fields: aria-invalid="true"

---

## Navigation

### Bottom Tab Bar

**Purpose**: Primary navigation (mobile)

**Specifications**:
- Height: 56px
- Position: fixed bottom
- Background: white
- Border-top: 1px solid gray-200
- Shadow: shadow-lg (reversed, upward)

```css
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: #ffffff;
  border-top: 1px solid #e5e7eb;
  box-shadow: 0 -4px 6px -1px rgb(0 0 0 / 0.1);
  display: flex;
  justify-content: space-around;
  z-index: 50;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  text-decoration: none;
  padding: 8px 0;
}

.nav-item.active {
  color: #0ea5e9;
}

.nav-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 4px;
}

.nav-label {
  font-size: 12px;
  font-weight: 500;
}
```

### Header (Top App Bar)

**Purpose**: Page title, back button, actions

**Specifications**:
- Height: 64px
- Background: white
- Border-bottom: 1px solid gray-200
- Position: sticky top 0

```css
.header {
  position: sticky;
  top: 0;
  height: 64px;
  padding: 0 16px;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 40;
}

.header-title {
  flex: 1;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}
```

---

## Modals & Sheets

### Bottom Sheet

**Purpose**: Mobile-friendly modal for forms and confirmations

**Specifications**:
- Max-height: 80vh
- Border-radius: 16px 16px 0 0 (top corners only)
- Background: white
- Shadow: shadow-2xl

```css
.bottom-sheet {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  max-height: 80vh;
  background: #ffffff;
  border-radius: 16px 16px 0 0;
  box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  z-index: 100;
  transform: translateY(100%);
  transition: transform 300ms ease-out;
}

.bottom-sheet.open {
  transform: translateY(0);
}
```

### Modal Backdrop

**Purpose**: Overlay behind modals

**Specifications**:
- Background: rgba(0, 0, 0, 0.5)
- Backdrop-filter: blur(4px) (optional)

```css
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 90;
  opacity: 0;
  transition: opacity 300ms ease-out;
}

.modal-backdrop.open {
  opacity: 1;
}
```

---

## Badges & Status Indicators

### Status Badge

**Purpose**: Display task status

**Specifications**:
- Padding: 4px 8px
- Font: 12px, font-weight: 500
- Border radius: 4px

```css
.badge {
  padding: 4px 8px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.badge.pending {
  background: #dbeafe;
  color: #1e40af;
}

.badge.claimed {
  background: #fef3c7;
  color: #92400e;
}

.badge.completed {
  background: #dcfce7;
  color: #166534;
}

.badge.failed {
  background: #fee2e2;
  color: #991b1b;
}
```

---

## Loading States

### Spinner

**Purpose**: Indicate loading

**Specifications**:
- Size: 24px (default), 16px (small), 32px (large)
- Border: 3px
- Color: primary-500
- Animation: 0.6s linear infinite

```css
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: #0ea5e9;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### Skeleton Screen

**Purpose**: Content placeholder during loading

**Specifications**:
- Background: gray-200
- Animation: pulse (1.5s infinite)

```css
.skeleton {
  background: #e5e7eb;
  border-radius: 4px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

---

## Empty States

### Empty State

**Purpose**: Display when no content available

**Specifications**:
- Icon: 48px, gray-400
- Title: 18px, font-weight: 600, gray-900
- Description: 14px, gray-500
- Action button (optional)

```css
.empty-state {
  text-align: center;
  padding: 48px 24px;
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: #9ca3af;
  margin: 0 auto 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
}

.empty-description {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 24px;
}
```

---

## Toast Notifications

### Toast

**Purpose**: Brief feedback messages

**Specifications**:
- Min-height: 48px
- Padding: 12px 16px
- Border-radius: 8px
- Shadow: shadow-lg
- Position: top or bottom of screen
- Duration: 3s (auto-dismiss)

```css
.toast {
  min-height: 48px;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
}

.toast.success {
  border-left: 4px solid #22c55e;
}

.toast.error {
  border-left: 4px solid #ef4444;
}

.toast.info {
  border-left: 4px solid #3b82f6;
}
```

---

## Vue Component Props

### TaskCard.vue

```typescript
interface TaskCardProps {
  task: {
    id: number;
    type: string;
    status: 'pending' | 'claimed' | 'completed' | 'failed';
    priority: 'low' | 'medium' | 'high';
    attempts: number;
    maxAttempts: number;
    progress?: number;
    createdAt: string;
  };
}
```

### BaseButton.vue

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: string;
}
```

---

**Created By**: Worker11 (UX Design Specialist)  
**Date**: 2025-11-09  
**Status**: ✅ Complete  
**Version**: 1.0.0
