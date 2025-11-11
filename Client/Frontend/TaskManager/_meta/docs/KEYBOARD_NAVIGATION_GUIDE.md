# Keyboard Navigation Guide

## Overview

This guide provides a comprehensive reference for keyboard navigation in the TaskManager frontend application. All features are fully accessible via keyboard without requiring a mouse.

**Last Updated**: 2025-11-10  
**Compliance**: WCAG 2.1 Level AA

## Global Keyboard Shortcuts

### Essential Keys

| Key | Action | Context |
|-----|--------|---------|
| `Tab` | Move focus to next interactive element | Global |
| `Shift + Tab` | Move focus to previous interactive element | Global |
| `Enter` | Activate focused button or link | Global |
| `Space` | Activate focused button or toggle | Global |
| `Escape` | Close modal, dialog, or cancel action | Modals |

## View-Specific Navigation

### TaskList View

#### Skip Navigation
- **First Tab**: Focus skip-to-main-content link
- **Enter**: Jump directly to main content area

#### Filter Tabs
| Key | Action |
|-----|--------|
| `Tab` | Move to filter tabs |
| `Left Arrow` | Move to previous filter tab |
| `Right Arrow` | Move to next filter tab |
| `Home` | Jump to first filter tab (All) |
| `End` | Jump to last filter tab (Failed) |
| `Enter` | Select focused filter tab |

#### Task Cards
| Key | Action |
|-----|--------|
| `Tab` | Navigate through task cards |
| `Enter` | Open task detail page |
| `Space` | Open task detail page |

**Navigation Flow**:
1. Tab to skip link → Press Enter to jump to main
2. Tab to filter tabs → Use arrows to select filter
3. Tab through task cards → Press Enter to view details

### TaskDetail View

#### Navigation Flow
| Key | Action |
|-----|--------|
| `Tab` | Navigate through page sections |
| First Tab | Back button |
| `Enter` on back button | Return to task list |
| Continue Tab | Navigate through task information |
| Action Buttons | Claim, Complete, or Fail task |
| `Space` or `Enter` | Activate button |

#### Modal Interactions (Failed Task Confirmation)
| Key | Action |
|-----|--------|
| `Tab` | Move between Cancel and Confirm buttons |
| `Escape` | Close modal and cancel action |
| `Enter` | Activate focused button |

### Settings View

#### Form Navigation
| Key | Action |
|-----|--------|
| `Tab` | Move to next form field or button |
| `Shift + Tab` | Move to previous form field |
| Type | Enter text in focused input field |
| `Enter` in input | Move to next field (no submit) |
| `Enter` on button | Submit form / Save settings |

**Form Fields in Order**:
1. Worker ID input field
2. Save Worker ID button
3. (API fields are read-only, tabbable but not editable)

### WorkerDashboard View

#### Status Controls
| Key | Action |
|-----|--------|
| `Tab` | Navigate to status buttons |
| `Enter` or `Space` | Toggle worker status |

#### Task Actions
| Key | Action |
|-----|--------|
| `Tab` | Move to Claim Next Task button |
| `Enter` or `Space` | Claim next available task |

#### My Tasks List
| Key | Action |
|-----|--------|
| `Tab` | Navigate through claimed tasks |
| `Enter` | Open task detail |
| `Space` | Open task detail |

## Component-Specific Navigation

### Bottom Navigation Bar

| Key | Action |
|-----|--------|
| `Tab` | Navigate between navigation items |
| `Enter` | Navigate to selected page |

**Tab Order**:
1. Tasks link
2. Workers link
3. Settings link

### Modals and Dialogs

All modals implement **focus trapping**:

#### ConfirmDialog
| Key | Action |
|-----|--------|
| `Tab` | Cycle through Cancel and Confirm buttons |
| `Shift + Tab` | Cycle backwards |
| `Escape` | Close modal (same as Cancel) |
| `Enter` | Activate focused button |

**Focus Trap Behavior**:
- When modal opens, focus moves to first button (Cancel)
- Tab wraps from last button to first button
- Shift+Tab wraps from first button to last button
- Cannot tab outside the modal
- Focus returns to trigger element when modal closes

### Loading States

When content is loading:
- Spinner receives `role="status"` with aria-label
- Loading message announced to screen readers
- Interactive elements may be disabled
- Tab order preserved

### Error States

When errors occur:
- Error message has `role="alert"`
- Screen reader announces error immediately
- Focus remains on trigger element
- Retry button accessible via Tab

## Tips for Effective Keyboard Navigation

### Getting Started
1. **Disconnect your mouse** to fully experience keyboard navigation
2. **Press Tab** to start navigating
3. **Look for the blue outline** showing keyboard focus
4. **Use Enter or Space** to activate elements

### Best Practices
- ✅ Use Tab to move forward, Shift+Tab to move backward
- ✅ Look for the focus indicator (blue outline)
- ✅ Use arrow keys when navigating tab groups
- ✅ Press Escape to cancel or close dialogs
- ✅ Use Enter or Space to activate buttons

### Common Patterns
1. **Skip repetitive navigation**: Use skip links at top of each page
2. **Filter content**: Use arrow keys in filter tab groups
3. **Activate cards**: Press Enter or Space on focused cards
4. **Close modals**: Press Escape or Tab to Cancel/Confirm
5. **Submit forms**: Tab to submit button and press Enter

## Tab Order by View

### TaskList
1. Skip to main content link
2. Page heading (not focusable, but present)
3. Filter tab: All
4. Filter tab: Pending
5. Filter tab: Claimed
6. Filter tab: Completed
7. Filter tab: Failed
8. Task card 1
9. Task card 2
10. Task card 3...
11. Bottom nav: Tasks
12. Bottom nav: Workers
13. Bottom nav: Settings

### TaskDetail
1. Skip to main content link
2. Back button
3. Claim button (if pending)
4. Complete button (if claimed by user)
5. Fail button (if claimed by user)

### Settings
1. Skip to main content link
2. Worker ID input field
3. Save Worker ID button
4. API Base URL input (read-only)
5. API Key input (read-only)
6. Bottom nav: Tasks
7. Bottom nav: Workers
8. Bottom nav: Settings

### WorkerDashboard
1. Skip to main content link
2. Initialize Worker button (if not initialized)
3. Set Active button (if initialized)
4. Set Idle button (if initialized)
5. Claim Next Task button
6. My Task card 1 (if any)
7. My Task card 2 (if any)...
8. Bottom nav: Tasks
9. Bottom nav: Workers
10. Bottom nav: Settings

## Accessibility Features

### Visual Focus Indicators
- **Default**: 3px solid blue outline (`#2563eb`)
- **Offset**: 2-3px from element
- **Enhanced**: Additional box shadow for buttons/links
- **Dark Mode**: Light blue outline (`#60a5fa`)
- **High Contrast**: 4px outline for high contrast mode

### Focus Management
- **Focus trapping** in modals prevents tabbing outside
- **Focus restoration** returns focus after modal closes
- **Skip links** allow jumping to main content
- **Logical tab order** follows visual layout

### Screen Reader Support
- All interactive elements have descriptive labels
- Dynamic content updates are announced
- Loading states are announced
- Error messages are announced immediately

## Troubleshooting

### Issue: Can't see where focus is
**Solution**: Check that focus indicators are enabled in browser settings. Look for the blue outline around focused elements.

### Issue: Tab doesn't move focus
**Solution**: Ensure you're on an interactive element. Some decorative elements are not focusable by design.

### Issue: Can't escape from modal
**Solution**: Press Escape key, or Tab to Cancel/Confirm button and press Enter.

### Issue: Arrow keys don't work
**Solution**: Arrow keys only work in specific contexts like filter tabs. Use Tab for general navigation.

### Issue: Skip link doesn't appear
**Solution**: Skip links are hidden until focused. Press Tab once on page load to reveal them.

## Testing Keyboard Navigation

### Manual Test Checklist
- [ ] Navigate entire app using only keyboard
- [ ] Verify skip links work on all views
- [ ] Test all buttons with Enter and Space
- [ ] Navigate filter tabs with arrow keys
- [ ] Verify modal focus trapping
- [ ] Check focus restoration after modals
- [ ] Confirm Escape closes modals
- [ ] Test form navigation and submission
- [ ] Verify focus indicators are visible
- [ ] Check tab order is logical

### Automated Testing
```bash
# Run accessibility tests including keyboard navigation
npm run test:ux:accessibility
```

## Additional Resources

- [ACCESSIBILITY_GUIDE.md](./ACCESSIBILITY_GUIDE.md) - Complete accessibility guide
- [WCAG 2.1 Keyboard Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/keyboard.html)
- [WebAIM Keyboard Testing](https://webaim.org/articles/keyboard/)

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-10  
**Author**: Worker12 (UX Review & Testing Specialist)  
**Next Review**: Monthly
