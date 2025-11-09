# User Flows

**Version**: 1.0  
**Last Updated**: 2025-11-09  
**Target Device**: Redmi 24115RA8EG  
**Context**: TaskManager Mobile Application

---

## Overview

This document defines the key user flows for the TaskManager application. Each flow describes:
- User goal
- Entry points
- Step-by-step journey
- Success/error states
- Mobile interactions

---

## Primary Flows

### 1. Task Claiming Flow

**User Goal**: Claim an available task to work on.

**Entry Point**: Task List View (Home)

#### Happy Path

```
┌──────────────────────┐
│   Task List View     │  User views pending tasks
│  ┌────────────────┐  │
│  │ Task #1234     │  │  
│  │ [PENDING]      │  │
│  └────────────────┘  │
└──────────────────────┘
          ↓ Tap task card
┌──────────────────────┐
│  Task Detail View    │  User sees full details
│  ┌────────────────┐  │
│  │ Title: Task..  │  │
│  │ Description    │  │
│  │ Priority: High │  │
│  └────────────────┘  │
│  [Claim Task]        │  
└──────────────────────┘
          ↓ Tap "Claim Task"
┌──────────────────────┐
│  Loading State       │  Brief loading
│  ● Processing...     │  (< 1 second)
└──────────────────────┘
          ↓
┌──────────────────────┐
│  Success Feedback    │  Toast notification
│  ✓ Task claimed!     │  "Task #1234 claimed"
└──────────────────────┘
          ↓ Auto-dismiss (3s)
┌──────────────────────┐
│  Task Detail View    │  Updated view
│  Status: CLAIMED     │  
│  [Complete Task]     │  New action available
└──────────────────────┘
```

#### Steps

1. **View Task List**
   - User sees list of pending tasks
   - Tasks sorted by priority (high → low)
   - Status filter: "Pending" selected

2. **Select Task**
   - User taps task card
   - Card provides haptic feedback (if supported)
   - Navigation to task detail

3. **Review Task Details**
   - Full task information displayed
   - "Claim Task" button prominent
   - User verifies they can complete task

4. **Claim Task**
   - User taps "Claim Task" button
   - Button shows loading state
   - API request sent

5. **Receive Confirmation**
   - Success toast appears: "✓ Task claimed!"
   - View updates: status → "CLAIMED"
   - Button changes: "Complete Task" available

6. **Continue or Exit**
   - Option A: Begin work (external to app)
   - Option B: Return to task list (back button)
   - Option C: View worker dashboard

#### Error Scenarios

**Already Claimed (by another worker)**
```
┌──────────────────────┐
│  Error Toast         │
│  ⚠️ Task already     │  Red background
│  claimed by another  │  Auto-dismiss 5s
│  worker              │  
└──────────────────────┘
          ↓
┌──────────────────────┐
│  Task Detail View    │  Status updated
│  Status: CLAIMED     │  Button disabled
│  Worker: Worker02    │  Show claim owner
└──────────────────────┘
```

**Network Error**
```
┌──────────────────────┐
│  Error Toast         │
│  ⚠️ Network error.   │  
│  Please try again    │  [Retry] button
└──────────────────────┘
          ↓ Tap Retry
┌──────────────────────┐
│  Retry Attempt       │  Same claim flow
└──────────────────────┘
```

**Maximum Attempts Reached**
```
┌──────────────────────┐
│  Error Toast         │
│  ⚠️ Cannot claim.    │
│  Task has reached    │
│  max attempts        │
└──────────────────────┘
          ↓
┌──────────────────────┐
│  Task Detail View    │  Button disabled
│  [Claim Unavailable] │  Explanation shown
└──────────────────────┘
```

#### Mobile Interactions

- **Tap**: Primary action (claim task)
- **Swipe Right** (future): Quick claim from list
- **Pull to Refresh**: Reload task list
- **Haptic Feedback**: On successful claim

#### Analytics Events

1. `task_viewed` - User opens task detail
2. `task_claim_initiated` - User taps claim button
3. `task_claim_success` - Task successfully claimed
4. `task_claim_failed` - Error occurred

---

### 2. Task Completion Flow

**User Goal**: Mark claimed task as complete.

**Entry Point**: Task Detail View (claimed task)

#### Happy Path

```
┌──────────────────────┐
│  Task Detail View    │  User has completed work
│  Status: CLAIMED     │  (external to app)
│  [Complete Task]     │  
└──────────────────────┘
          ↓ Tap "Complete Task"
┌──────────────────────┐
│  Confirmation Modal  │  Verify intention
│  Complete this task? │
│                      │
│  [Cancel] [Confirm]  │
└──────────────────────┘
          ↓ Tap "Confirm"
┌──────────────────────┐
│  (Optional)          │  If task requires result
│  Result Input        │  
│  ┌────────────────┐  │
│  │ Enter result   │  │
│  └────────────────┘  │
│  [Submit]            │
└──────────────────────┘
          ↓ Tap "Submit" or Skip
┌──────────────────────┐
│  Loading State       │
│  ● Processing...     │
└──────────────────────┘
          ↓
┌──────────────────────┐
│  Success Feedback    │  
│  ✓ Task completed!   │  Celebration animation
│  +10 points          │  (optional)
└──────────────────────┘
          ↓ Auto-dismiss (3s)
┌──────────────────────┐
│  Task List View      │  Navigated back
│  Task moved to       │  
│  "Completed"         │  
└──────────────────────┘
```

#### Steps

1. **Access Claimed Task**
   - User navigates to claimed task
   - "Complete Task" button visible
   - Task details shown

2. **Initiate Completion**
   - User taps "Complete Task"
   - Confirmation modal appears
   - Prevents accidental completion

3. **Confirm Action**
   - User taps "Confirm"
   - Modal dismisses
   - Optional: Result input shown

4. **(Optional) Provide Result**
   - Input field for result data
   - Validation if required
   - Submit or skip

5. **Process Completion**
   - API request sent
   - Loading indicator shown
   - Brief wait (< 1s typical)

6. **Receive Confirmation**
   - Success toast with celebration
   - Optional: Points/reward shown
   - Auto-navigate to task list

7. **View Updated List**
   - Task moved to "Completed" filter
   - Count updated
   - Next task available for claim

#### Error Scenarios

**Network Error**
```
┌──────────────────────┐
│  Error Toast         │
│  ⚠️ Failed to mark   │
│  complete. Retry?    │
│  [Retry] [Cancel]    │
└──────────────────────┘
```

**Task State Changed**
```
┌──────────────────────┐
│  Error Toast         │
│  ⚠️ Task no longer   │
│  claimed by you      │
└──────────────────────┘
          ↓
┌──────────────────────┐
│  Task Detail View    │  Refreshed state
│  Status: COMPLETED   │  (if completed by admin)
│  or PENDING          │  (if unclaimed)
└──────────────────────┘
```

**Invalid Result Data**
```
┌──────────────────────┐
│  Result Input        │
│  ┌────────────────┐  │
│  │ [invalid data] │  │  Red border
│  └────────────────┘  │
│  ⚠️ Invalid format   │  Error message
└──────────────────────┘
```

#### Mobile Interactions

- **Tap**: Complete task
- **Swipe Left** (future): Quick complete from list
- **Modal**: Bottom sheet on mobile
- **Haptic**: Success vibration on completion

---

### 3. Task Browsing Flow

**User Goal**: Browse and filter available tasks.

**Entry Point**: App Launch or Bottom Navigation → Tasks

#### Flow

```
┌──────────────────────┐
│  App Launch          │  
└──────────────────────┘
          ↓
┌──────────────────────┐
│  Loading Screen      │  Brief splash
│  ● Loading...        │  (< 1s)
└──────────────────────┘
          ↓
┌──────────────────────┐
│  Task List View      │  Default: All tasks
│  [All] Pending Claimed│ Filter tabs
│  ┌────────────────┐  │
│  │ Task 1 [PEND]  │  │  List of tasks
│  │ Task 2 [CLAIM] │  │  Sorted by priority
│  │ Task 3 [DONE]  │  │
│  └────────────────┘  │
└──────────────────────┘
          ↓ Tap "Pending" filter
┌──────────────────────┐
│  Task List View      │  Filtered view
│  All [Pending] Claimed│ 
│  ┌────────────────┐  │
│  │ Task 1 [PEND]  │  │  Only pending tasks
│  │ Task 4 [PEND]  │  │
│  └────────────────┘  │
└──────────────────────┘
          ↓ Pull down to refresh
┌──────────────────────┐
│  Refreshing...       │  Pull-to-refresh
│  ↻                   │  
└──────────────────────┘
          ↓
┌──────────────────────┐
│  Task List View      │  Updated data
│  Count updated       │  
└──────────────────────┘
```

#### Filter Options

1. **All** - Show all tasks (default)
2. **Pending** - Only unclaimed tasks
3. **Claimed** - Only tasks claimed by any worker
4. **Completed** - Finished tasks
5. **Failed** - Tasks that failed

#### Sort Options (Future)

- Priority (High → Low)
- Created date (Newest → Oldest)
- Attempts (Fewest → Most)

#### Empty States

**No Tasks**
```
┌──────────────────────┐
│       📭             │
│   No tasks found     │
│                      │
│  All tasks completed │
└──────────────────────┘
```

**No Pending**
```
┌──────────────────────┐
│       ✓              │
│  All caught up!      │
│                      │
│ No pending tasks     │
└──────────────────────┘
```

---

### 4. Worker Dashboard Flow

**User Goal**: View personal task statistics and activity.

**Entry Point**: Bottom Navigation → Workers

#### Flow

```
┌──────────────────────┐
│  Bottom Nav          │
│  Tasks [Workers] Set │  Tap "Workers"
└──────────────────────┘
          ↓
┌──────────────────────┐
│  Worker Dashboard    │  
│  ┌────────────────┐  │
│  │ My Stats       │  │  Personal metrics
│  │ Tasks: 12      │  │
│  │ Complete: 8    │  │
│  │ In Progress: 2 │  │
│  └────────────────┘  │
│                      │
│  ┌────────────────┐  │
│  │ My Tasks       │  │  Claimed tasks
│  │ ─────────────  │  │  
│  │ Task 1 [CLAIM] │  │
│  │ Task 2 [CLAIM] │  │
│  └────────────────┘  │
└──────────────────────┘
          ↓ Tap task
┌──────────────────────┐
│  Task Detail View    │  Standard detail view
└──────────────────────┘
```

#### Dashboard Components

1. **Stats Card**
   - Total tasks claimed
   - Completed count
   - In progress count
   - Success rate %

2. **My Tasks Section**
   - List of claimed tasks
   - Quick access to continue work
   - Progress indicators

3. **Activity Timeline** (Future)
   - Recent actions
   - Completions
   - Claims

---

### 5. Error Recovery Flow

**User Goal**: Recover from errors and continue using app.

#### Network Error

```
┌──────────────────────┐
│  Task List View      │  
│  ● Loading...        │  Network request
└──────────────────────┘
          ↓ Network fails
┌──────────────────────┐
│  Error State         │
│  ⚠️                  │
│  Network error       │
│                      │
│  Check connection    │
│  and try again       │
│                      │
│  [Retry]             │  
└──────────────────────┘
          ↓ Tap "Retry"
┌──────────────────────┐
│  Loading...          │  Retry request
└──────────────────────┘
          ↓ Success
┌──────────────────────┐
│  Task List View      │  Data loaded
└──────────────────────┘
```

#### Unauthorized Error

```
┌──────────────────────┐
│  Error Toast         │
│  ⚠️ Session expired  │
│                      │
│  Please login again  │
└──────────────────────┘
          ↓ Auto-redirect (2s)
┌──────────────────────┐
│  Login Screen        │  (Future feature)
└──────────────────────┘
```

#### Server Error

```
┌──────────────────────┐
│  Error State         │
│  ⚠️                  │
│  Server error        │
│                      │
│  We're working on it │
│  Please try later    │
│                      │
│  [Go Back]           │
└──────────────────────┘
```

---

### 6. First-Time User Onboarding (Future)

**User Goal**: Understand how to use the app.

#### Flow

```
┌──────────────────────┐
│  Welcome Screen      │  First launch
│  Welcome to          │  
│  TaskManager!        │
│                      │
│  [Get Started]       │
└──────────────────────┘
          ↓
┌──────────────────────┐
│  Tutorial Slide 1    │  
│  Browse tasks        │  Swipeable cards
│  [● ○ ○ ○]          │  Dots indicator
│  [Skip] [Next]       │
└──────────────────────┘
          ↓ Swipe left / Tap Next
┌──────────────────────┐
│  Tutorial Slide 2    │
│  Claim tasks         │
│  [○ ● ○ ○]          │
│  [Skip] [Next]       │
└──────────────────────┘
          ↓ Continue
┌──────────────────────┐
│  Tutorial Slide 3    │
│  Complete work       │
│  [○ ○ ● ○]          │
│  [Skip] [Next]       │
└──────────────────────┘
          ↓ Continue
┌──────────────────────┐
│  Tutorial Slide 4    │
│  Track progress      │
│  [○ ○ ○ ●]          │
│  [Done]              │
└──────────────────────┘
          ↓ Tap Done
┌──────────────────────┐
│  Task List View      │  Main app
└──────────────────────┘
```

---

## Interaction Patterns

### Pull to Refresh

**Trigger**: Pull down from top of scrollable list  
**Feedback**: 
1. Reveal refresh indicator
2. Show "Release to refresh"
3. On release: Spinner + "Refreshing..."
4. On complete: Indicator dismisses

**Duration**: 1-2 seconds

### Infinite Scroll (Future)

**Trigger**: Scroll to bottom of list  
**Behavior**: Load next page automatically  
**Indicator**: Small spinner at bottom

### Swipe Actions (Future)

**Swipe Right on Task Card**: Quick claim
```
┌─────────────────────────────┐
│ → Claim  │ Task #1234 [PEND]│  Swipe reveals action
└─────────────────────────────┘
```

**Swipe Left on Task Card**: Show options
```
┌─────────────────────────────┐
│ Task #1234 [CLAIM] │ Complete│  Swipe reveals action
└─────────────────────────────┘
```

---

## Navigation Patterns

### Deep Linking

**URL Structure**:
```
/                    → Task List
/tasks/:id           → Task Detail
/workers             → Worker Dashboard
/settings            → Settings
```

**Back Navigation**:
- Android: Hardware back button
- iOS: Swipe from left edge
- All: Header back button (←)

### Tab Navigation

Bottom navigation tabs:
1. **Tasks** - Main task list (home)
2. **Workers** - Worker dashboard
3. **Settings** - App settings

Active tab highlighted in primary color.

---

## Loading States

### Initial Load
- Full-screen spinner
- "Loading tasks..."
- Duration: < 2 seconds

### Partial Update
- Small spinner in affected area
- Rest of UI remains interactive
- Duration: < 1 second

### Background Refresh
- Subtle indicator in header
- No blocking UI
- Success: Silent update
- Error: Toast notification

---

## Success Feedback

### Toast Notifications

**Duration**:
- Success: 3 seconds
- Error: 5 seconds (or until dismissed)
- Info: 4 seconds

**Position**: Top center (mobile), top right (desktop)

**Examples**:
- ✓ Task claimed successfully
- ✓ Task completed
- ⚠️ Network error. Try again.
- ℹ️ Task updated

### Visual Feedback

- Button press: Scale down slightly (0.98)
- Card tap: Brief background color change
- Success: Green checkmark animation
- Error: Red shake animation

---

## Error Handling

### Error Types

1. **Network Errors**
   - Offline
   - Timeout
   - Server unreachable

2. **Validation Errors**
   - Invalid input
   - Missing required fields
   - Format errors

3. **Business Logic Errors**
   - Task already claimed
   - Max attempts reached
   - Unauthorized action

4. **Server Errors**
   - 500 Internal Server Error
   - Service unavailable
   - Unexpected errors

### Error Display

- **Inline**: For form validation
- **Toast**: For transient errors
- **Full Page**: For critical errors
- **Modal**: For important warnings

---

## Accessibility Considerations

### Screen Reader Support

- Announce page changes
- Announce loading states
- Announce errors
- Announce success feedback

### Keyboard Navigation

- Tab order follows visual flow
- Enter to activate buttons
- Escape to close modals
- Arrow keys for tabs

### Reduced Motion

- Disable animations if `prefers-reduced-motion`
- Use instant transitions
- Maintain visual feedback

---

## Flow Status

| Flow                | Designed | Documented | Implemented | Tested |
|---------------------|----------|------------|-------------|--------|
| Task Claiming       | ✅       | ✅         | ⏳          | ⏳     |
| Task Completion     | ✅       | ✅         | ⏳          | ⏳     |
| Task Browsing       | ✅       | ✅         | ⏳          | ⏳     |
| Worker Dashboard    | ✅       | ✅         | ⏳          | ⏳     |
| Error Recovery      | ✅       | ✅         | ⏳          | ⏳     |
| First-Time Onboard  | ✅       | ✅         | ⏳          | ⏳     |

---

**Version**: 1.0  
**Maintained by**: Worker11 (UX Design Specialist)  
**Next Steps**: User testing with Worker12  
**Last Updated**: 2025-11-09
