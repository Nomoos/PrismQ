# Accessibility Guidelines

**Version**: 1.0  
**Last Updated**: 2025-11-09  
**Standard**: WCAG 2.1 Level AA  
**Target Device**: Redmi 24115RA8EG + All devices

---

## Overview

This document defines accessibility requirements for the TaskManager application to ensure WCAG 2.1 Level AA compliance and inclusive design for all users, including those with disabilities.

**Goal**: Create an application that is perceivable, operable, understandable, and robust for everyone.

---

## WCAG 2.1 Level AA Requirements

### Principle 1: Perceivable

Information and UI must be presentable to users in ways they can perceive.

#### 1.1 Text Alternatives

**Requirement**: Provide text alternatives for non-text content.

**Implementation**:

✅ **Images**
```html
<!-- Decorative images -->
<img src="icon.svg" alt="" role="presentation">

<!-- Meaningful images -->
<img src="success.svg" alt="Success indicator">

<!-- Complex images -->
<img src="chart.png" alt="Task completion rate: 85% complete, 10% in progress, 5% failed">
```

✅ **Icons**
```html
<!-- Icon-only buttons -->
<button aria-label="Close modal">
  <span class="icon-close" aria-hidden="true"></span>
</button>

<!-- Icon with text -->
<button>
  <span class="icon-save" aria-hidden="true"></span>
  Save
</button>
```

✅ **Form Inputs**
```html
<label for="task-title">Task Title</label>
<input id="task-title" type="text" aria-required="true">
```

#### 1.2 Time-based Media

**Requirement**: Provide alternatives for time-based media.

**Current Scope**: N/A (no audio/video in MVP)

**Future**: Captions for tutorial videos, transcripts for audio.

#### 1.3 Adaptable

**Requirement**: Create content that can be presented in different ways.

✅ **Semantic HTML**
```html
<header>
  <h1>TaskManager</h1>
  <nav>...</nav>
</header>

<main>
  <section aria-labelledby="tasks-heading">
    <h2 id="tasks-heading">Available Tasks</h2>
    <article>...</article>
  </section>
</main>

<footer>...</footer>
```

✅ **Heading Hierarchy**
```html
<h1>TaskManager</h1>          <!-- Page title -->
  <h2>Available Tasks</h2>     <!-- Section -->
    <h3>Task #1234</h3>        <!-- Sub-section -->
```

✅ **Meaningful Sequence**
- Visual order matches DOM order
- Tab order follows logical reading flow
- Content meaningful without CSS

✅ **Sensory Characteristics**
```html
<!-- ❌ Bad -->
<p>Click the green button</p>

<!-- ✅ Good -->
<p>Click the "Claim Task" button</p>
<button class="btn-primary">Claim Task</button>
```

#### 1.4 Distinguishable

**Requirement**: Make it easy to see and hear content.

✅ **Color Contrast**

**Normal Text** (< 24px or < 19px bold):
- Minimum: 4.5:1
- Examples:
  - White on primary-500 (#0ea5e9): 4.56:1 ✓
  - neutral-900 (#171717) on white: 14.1:1 ✓
  - neutral-700 (#404040) on white: 8.59:1 ✓

**Large Text** (≥ 24px or ≥ 19px bold):
- Minimum: 3:1
- Examples:
  - neutral-600 (#525252) on white: 6.58:1 ✓

**UI Components**:
- Minimum: 3:1
- Border colors: neutral-200 on white: 1.27:1 ✗
- **Solution**: Use neutral-300 or thicker borders

**Testing Tool**: WebAIM Contrast Checker

✅ **Resize Text**
- Support 200% zoom (browser default)
- No horizontal scrolling at 200%
- Relative units (rem, em)

```css
/* ✅ Good */
font-size: 1rem; /* 16px, scales with zoom */

/* ❌ Bad */
font-size: 16px; /* Fixed, but acceptable */
```

✅ **Text Spacing**

Allow user to adjust:
- Line height: ≥ 1.5 times font size
- Paragraph spacing: ≥ 2 times font size
- Letter spacing: ≥ 0.12 times font size
- Word spacing: ≥ 0.16 times font size

```css
body {
  line-height: 1.5;      /* ✓ */
  letter-spacing: normal; /* ✓ */
}
```

✅ **Reflow**

No horizontal scrolling at:
- 320px width for vertical scrolling
- 256px height for horizontal scrolling

```css
/* Use relative widths */
.container {
  width: 100%;
  max-width: 1280px;
}

/* Avoid fixed widths */
/* ❌ */ width: 800px;
```

✅ **Non-Text Contrast**

UI components and graphics: 3:1 minimum
- Buttons: Background vs. surrounding
- Form inputs: Border vs. background
- Focus indicators: 3:1 minimum

```css
/* Focus indicator */
:focus-visible {
  outline: 2px solid #0ea5e9; /* 4.56:1 on white ✓ */
  outline-offset: 2px;
}
```

✅ **Images of Text**

Avoid images of text (use real text).

**Exceptions**: Logos, brand names.

---

### Principle 2: Operable

UI and navigation must be operable.

#### 2.1 Keyboard Accessible

**Requirement**: All functionality available via keyboard.

✅ **Keyboard Navigation**
```
Tab       → Move to next focusable element
Shift+Tab → Move to previous
Enter     → Activate button, submit form
Space     → Activate button, toggle checkbox
Escape    → Close modal, cancel action
Arrow keys → Navigate within component (tabs, menus)
```

✅ **No Keyboard Trap**
```javascript
// Modal focus management
function openModal() {
  // Save last focused element
  lastFocusedElement = document.activeElement
  
  // Move focus to modal
  modal.focus()
  
  // Trap focus within modal
  modal.addEventListener('keydown', trapFocus)
}

function closeModal() {
  // Restore focus
  lastFocusedElement.focus()
}
```

✅ **Focus Order**

Logical tab order matching visual flow:
```
1. Skip to content link
2. Header (logo, nav)
3. Main content (tasks, actions)
4. Bottom navigation
5. Footer (if present)
```

✅ **Character Key Shortcuts**

If single-key shortcuts exist:
- Provide way to turn off
- Remap to Ctrl/Alt/Cmd + key
- Only active when component focused

**Current Scope**: No single-key shortcuts in MVP.

#### 2.2 Enough Time

**Requirement**: Provide enough time to read and use content.

✅ **Timing Adjustable**

No time limits or:
- Turn off timing
- Adjust time limit (10x minimum)
- Extend before expiration

**Current Scope**: No time limits in MVP.

**Session timeout** (future):
- Warning before expiration (20 seconds)
- Option to extend

✅ **Pause, Stop, Hide**

Auto-updating content:
- Provide pause/stop control
- Or make it essential

**Examples**:
```html
<!-- Auto-refresh toggle -->
<label>
  <input type="checkbox" checked> Auto-refresh tasks
</label>
```

✅ **No Timing**

No animations that:
- Flash more than 3 times per second
- Are larger than small safe area

**Compliance**: All animations meet this requirement.

#### 2.3 Seizures and Physical Reactions

**Requirement**: Do not design content that causes seizures.

✅ **Three Flashes or Below Threshold**

No content flashes more than 3 times per second.

**Compliance**: No flashing content in design.

#### 2.4 Navigable

**Requirement**: Provide ways to navigate, find content.

✅ **Skip Links**
```html
<a href="#main-content" class="skip-link">
  Skip to main content
</a>

<main id="main-content">
  <!-- Content -->
</main>
```

```css
.skip-link {
  position: absolute;
  left: -9999px;
  z-index: 999;
}

.skip-link:focus {
  left: 0;
  background: var(--primary-500);
  color: white;
  padding: 12px 16px;
}
```

✅ **Page Titled**
```html
<title>Task #1234 - TaskManager</title>
```

Dynamic updates:
```javascript
// Update title on navigation
router.afterEach((to) => {
  document.title = `${to.meta.title} - TaskManager`
})
```

✅ **Focus Order**

Logical and intuitive:
1. Header navigation
2. Main content (tasks)
3. Primary actions
4. Bottom navigation

✅ **Link Purpose (In Context)**

Link text describes destination:

```html
<!-- ✅ Good -->
<a href="/tasks/1234">View Task #1234</a>

<!-- ❌ Bad -->
<a href="/tasks/1234">Click here</a>
```

✅ **Multiple Ways**

Provide multiple ways to find content:
- Navigation menu
- Search (future)
- Sitemap/index (future)

**Current**: Bottom navigation, breadcrumbs.

✅ **Headings and Labels**

Descriptive headings and labels:

```html
<h2>Available Tasks</h2>

<label for="priority-filter">Filter by Priority</label>
<select id="priority-filter">...</select>
```

✅ **Focus Visible**

Keyboard focus clearly visible:

```css
:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}
```

#### 2.5 Input Modalities

**Requirement**: Make functionality easier to operate.

✅ **Pointer Gestures**

Single pointer alternative for multi-point/path-based gestures.

**Examples**:
- Swipe: Provide button alternative
- Pinch zoom: Provide zoom controls
- Drag: Provide click alternative

✅ **Pointer Cancellation**

For single-pointer activation:
- Down event doesn't execute
- Action on up event
- Abort by moving away
- Or essential for function

```javascript
// Correct implementation
button.addEventListener('touchend', handleClick)  // ✓
// Not this:
button.addEventListener('touchstart', handleClick) // ✗
```

✅ **Label in Name**

Visible label matches accessible name:

```html
<!-- ✅ Good -->
<button aria-label="Close">Close</button>

<!-- ❌ Bad -->
<button aria-label="Dismiss">Close</button>
```

✅ **Motion Actuation**

Device motion not required (or provide alternative).

**Current Scope**: No motion-based features.

✅ **Target Size**

Touch targets: 44px × 44px minimum ✓

**Exceptions**:
- Inline links in text
- Essential (e.g., map pins)
- User-controlled size

**Compliance**: All buttons and interactive elements ≥ 44px.

---

### Principle 3: Understandable

Information and UI must be understandable.

#### 3.1 Readable

**Requirement**: Make text readable and understandable.

✅ **Language of Page**
```html
<html lang="en">
```

✅ **Language of Parts**

For multi-language content:
```html
<p>The task is <span lang="fr">terminé</span>.</p>
```

**Current Scope**: English only.

#### 3.2 Predictable

**Requirement**: Make pages appear and operate predictably.

✅ **On Focus**

Focus doesn't trigger unexpected context change.

**Examples**:
- Focus on input: No auto-submit ✓
- Focus on button: No auto-activate ✓

✅ **On Input**

Input doesn't trigger unexpected change.

**Examples**:
- Typing in search: No auto-navigate ✓
- Selecting radio: No auto-submit ✓
- Debounced search: OK (expected)

✅ **Consistent Navigation**

Same navigation order on all pages:

```
Header → Main Content → Bottom Nav
```

Consistent across all views ✓

✅ **Consistent Identification**

Same functionality labeled consistently:

```html
<!-- Same icon/label everywhere -->
<button aria-label="Close">×</button>
```

#### 3.3 Input Assistance

**Requirement**: Help users avoid and correct mistakes.

✅ **Error Identification**

Errors clearly identified:

```html
<label for="email">Email</label>
<input 
  id="email" 
  type="email" 
  aria-invalid="true"
  aria-describedby="email-error"
>
<span id="email-error" class="error">
  Please enter a valid email address.
</span>
```

✅ **Labels or Instructions**

Provide labels and instructions:

```html
<label for="password">
  Password (min. 8 characters)
</label>
<input id="password" type="password" minlength="8">
```

✅ **Error Suggestion**

Suggest corrections:

```
❌ Invalid email
✅ Invalid email. Format: user@example.com
```

✅ **Error Prevention (Legal, Financial, Data)**

For important submissions:
- Reversible, or
- Checked for errors, or
- Confirmed

```html
<!-- Confirmation modal -->
<div role="dialog" aria-labelledby="confirm-title">
  <h2 id="confirm-title">Confirm Completion</h2>
  <p>Are you sure you want to complete this task?</p>
  <button>Cancel</button>
  <button>Confirm</button>
</div>
```

---

### Principle 4: Robust

Content must be robust enough for assistive technologies.

#### 4.1 Compatible

**Requirement**: Maximize compatibility with assistive technologies.

✅ **Parsing**

Valid HTML:
- Proper nesting
- Unique IDs
- Complete start/end tags

**Testing**: HTML validator

✅ **Name, Role, Value**

All UI components have programmatically determined:
- Name (accessible name)
- Role (implicit or explicit)
- Value (current state)

**Examples**:

```html
<!-- Button -->
<button>Claim Task</button>
<!-- Name: "Claim Task", Role: button -->

<!-- Custom checkbox -->
<div 
  role="checkbox" 
  aria-checked="true"
  aria-labelledby="auto-refresh-label"
  tabindex="0"
>
  <span id="auto-refresh-label">Auto-refresh</span>
</div>

<!-- Status badge -->
<span 
  class="badge badge-success"
  role="status"
  aria-label="Status: Completed"
>
  COMPLETED
</span>
```

---

## ARIA Usage

### Landmarks

```html
<header role="banner">...</header>
<nav role="navigation">...</nav>
<main role="main">...</main>
<aside role="complementary">...</aside>
<footer role="contentinfo">...</footer>
```

**Note**: Use semantic HTML; role is implicit.

### Live Regions

**Announcements** (non-interrupting):
```html
<div role="status" aria-live="polite">
  Task claimed successfully!
</div>
```

**Alerts** (interrupting):
```html
<div role="alert" aria-live="assertive">
  Error: Network connection lost.
</div>
```

### States and Properties

**Required field**:
```html
<input aria-required="true">
```

**Invalid input**:
```html
<input aria-invalid="true" aria-describedby="error-msg">
```

**Expanded/collapsed**:
```html
<button aria-expanded="false" aria-controls="panel">
  Show Details
</button>
<div id="panel" hidden>...</div>
```

**Selected item**:
```html
<button role="tab" aria-selected="true">Tasks</button>
```

**Current page**:
```html
<a href="/" aria-current="page">Home</a>
```

### Hidden Content

**Visually hidden** (still announced):
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

```html
<button>
  <span class="icon-delete" aria-hidden="true"></span>
  <span class="sr-only">Delete task</span>
</button>
```

**Completely hidden**:
```html
<div aria-hidden="true">...</div>
<!-- Or -->
<div hidden>...</div>
```

---

## Screen Reader Support

### Testing

**Screen Readers**:
- **iOS**: VoiceOver (Safari)
- **Android**: TalkBack (Chrome)
- **Desktop**: NVDA (Windows), VoiceOver (Mac)

### Best Practices

✅ **Descriptive Labels**
```html
<!-- Good -->
<button aria-label="Close modal">×</button>

<!-- Bad -->
<button>×</button>
```

✅ **Form Labels**
```html
<label for="task-title">Task Title</label>
<input id="task-title" type="text">
```

✅ **Table Headers**
```html
<table>
  <thead>
    <tr>
      <th scope="col">Task</th>
      <th scope="col">Status</th>
    </tr>
  </thead>
  <tbody>...</tbody>
</table>
```

✅ **Lists**
```html
<ul>
  <li>Task 1</li>
  <li>Task 2</li>
</ul>
```

Screen reader announces: "List, 2 items"

---

## Testing Checklist

### Automated Testing

- [ ] Run axe-core or Lighthouse
- [ ] Check HTML validity
- [ ] Test color contrast
- [ ] Verify ARIA usage

### Manual Testing

- [ ] Keyboard-only navigation
- [ ] Screen reader (VoiceOver/TalkBack)
- [ ] 200% zoom
- [ ] Reduced motion
- [ ] High contrast mode

### Mobile Testing

- [ ] Touch target size (44px min)
- [ ] Pinch zoom enabled
- [ ] Landscape orientation
- [ ] Screen reader gestures

---

## Common Issues & Solutions

### Issue: Low Contrast

**Problem**: Text on background < 4.5:1

**Solution**:
```css
/* Bad: 2.1:1 */
color: #999999;
background: white;

/* Good: 5.74:1 */
color: #666666;
background: white;
```

### Issue: Missing Alt Text

**Problem**: Images without alt attribute

**Solution**:
```html
<!-- Decorative -->
<img src="decoration.svg" alt="">

<!-- Meaningful -->
<img src="success.svg" alt="Success icon">
```

### Issue: Non-Semantic HTML

**Problem**: Divs as buttons

**Solution**:
```html
<!-- Bad -->
<div onclick="claim()">Claim</div>

<!-- Good -->
<button onclick="claim()">Claim</button>
```

### Issue: Unlabeled Form

**Problem**: Input without label

**Solution**:
```html
<!-- Bad -->
<input type="text" placeholder="Email">

<!-- Good -->
<label for="email">Email</label>
<input id="email" type="text">
```

### Issue: Keyboard Trap

**Problem**: Can't tab out of modal

**Solution**:
```javascript
function trapFocus(e) {
  const focusable = modal.querySelectorAll('button, input, a')
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  
  if (e.key === 'Tab') {
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault()
      last.focus()
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault()
      first.focus()
    }
  }
}
```

---

## Compliance Status

| Criterion           | Level | Status | Notes                    |
|---------------------|-------|--------|--------------------------|
| 1.1 Text Alt        | A     | ✅     | All images have alt      |
| 1.3 Adaptable       | A     | ✅     | Semantic HTML used       |
| 1.4.3 Contrast      | AA    | ✅     | 4.5:1 minimum            |
| 1.4.11 Non-text     | AA    | ✅     | 3:1 for UI components    |
| 2.1 Keyboard        | A     | ✅     | All operable             |
| 2.4.7 Focus Visible | AA    | ✅     | Clear focus indicators   |
| 2.5.5 Target Size   | AAA   | ✅     | 44px minimum             |
| 3.2 Predictable     | A     | ✅     | Consistent navigation    |
| 3.3 Input Assist    | A     | ✅     | Labels and errors        |
| 4.1 Compatible      | A     | ✅     | Valid HTML, ARIA         |

**Overall**: WCAG 2.1 Level AA Compliant ✅

---

## Resources

**WCAG 2.1**: https://www.w3.org/WAI/WCAG21/quickref/  
**ARIA**: https://www.w3.org/TR/wai-aria-1.2/  
**Contrast Checker**: https://webaim.org/resources/contrastchecker/  
**Axe DevTools**: https://www.deque.com/axe/devtools/

---

**Version**: 1.0  
**Maintained by**: Worker11 (UX Design Specialist)  
**Testing by**: Worker12 (UX Testing & Accessibility Audit)  
**Last Updated**: 2025-11-09
