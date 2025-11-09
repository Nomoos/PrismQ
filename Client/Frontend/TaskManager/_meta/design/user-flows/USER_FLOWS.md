# User Flows

**Version**: 1.0.0  
**Last Updated**: 2025-11-09  
**Design System**: [Design System](../DESIGN_SYSTEM.md)

---

## Table of Contents

1. [Task Claiming Flow](#task-claiming-flow)
2. [Task Completion Flow](#task-completion-flow)
3. [Task Creation Flow](#task-creation-flow)
4. [Task Failure Flow](#task-failure-flow)
5. [Error Recovery Flow](#error-recovery-flow)
6. [First-Time Onboarding](#first-time-onboarding)

---

## Task Claiming Flow

### Purpose
Allow workers to claim available tasks for processing.

### User Goal
Find and claim a task to work on.

### Flow Diagram

```
START
  │
  ├─> 1. View Task List
  │     ├─ All tasks displayed
  │     ├─ Filter: Pending
  │     └─ Sorted by priority
  │
  ├─> 2. Browse Tasks
  │     ├─ Scroll through list
  │     ├─ Read task descriptions
  │     └─ Check priority/type
  │
  ├─> 3. Select Task
  │     ├─ Tap task card
  │     └─ Navigate to detail view
  │
  ├─> 4. Review Task Details
  │     ├─ Read full description
  │     ├─ Check parameters
  │     ├─ Review requirements
  │     └─ Verify can complete
  │
  ├─> 5. Initiate Claim
  │     ├─ Tap "Claim Task" button
  │     └─ Trigger confirmation
  │
  ├─> 6. Confirm Claim
  │     ├─ Review claim details
  │     ├─ Confirm understanding
  │     └─ Submit claim request
  │
  ├─> 7. Process Claim (Backend)
  │     ├─ Validate worker
  │     ├─ Check task availability
  │     ├─ Lock task
  │     └─ Update status
  │
  ├─> 8. Receive Confirmation
  │     ├─ Success toast notification
  │     ├─ Task moves to "My Tasks"
  │     └─ Detail view updates
  │
  └─> END (Success)

Alternative Paths:
  │
  ├─> A. Quick Claim (Swipe)
  │     ├─ Swipe right on task card
  │     ├─ Claim without confirmation
  │     └─ Success feedback
  │
  └─> B. Claim Failed
        ├─ Task already claimed
        ├─ Error message displayed
        └─ Return to task list
```

### Steps in Detail

**Step 1: View Task List**
- Location: Task List View
- Display: All available tasks, filtered by "Pending"
- Interaction: Scroll to browse

**Step 2: Browse Tasks**
- User scans task cards
- Reads titles, priorities, descriptions
- Identifies suitable task

**Step 3: Select Task**
- Tap on task card
- Navigate to Task Detail View
- Animation: Slide transition (300ms)

**Step 4: Review Task Details**
- Read full description
- Review parameters and requirements
- Check max attempts and priority
- Decide if can complete

**Step 5: Initiate Claim**
- Tap "Claim Task" button (primary)
- Button triggers confirmation modal

**Step 6: Confirm Claim**
- Bottom sheet appears
- Shows task summary
- "Cancel" and "Confirm Claim" buttons
- Tap confirm to proceed

**Step 7: Process Claim**
- API request to backend
- Loading spinner on button
- Backend validates and locks task

**Step 8: Receive Confirmation**
- Success toast: "Task claimed successfully"
- Task moved to "My Tasks" tab
- Detail view shows "Claimed" status
- Progress bar appears (0%)

### Success Criteria
- ✅ Task status changed to "Claimed"
- ✅ Task visible in "My Tasks" tab
- ✅ Worker assigned to task
- ✅ Confirmation feedback shown

### Alternative Path: Quick Claim
- Swipe right on pending task card
- Task immediately claimed (no confirmation)
- Success haptic feedback
- Toast notification
- Use for experienced users

### Error Scenarios

**Task Already Claimed**:
- Error toast: "This task was just claimed by another worker"
- Task removed from list
- User returned to task list

**Network Error**:
- Error toast: "Unable to claim task. Check connection."
- Retry button available
- Task remains available

**Validation Error**:
- Error toast: "You cannot claim this task"
- Reason displayed (e.g., "Max active tasks reached")
- Return to list

---

## Task Completion Flow

### Purpose
Mark a claimed task as completed and submit results.

### User Goal
Complete work on a task and update the system.

### Flow Diagram

```
START (Task claimed, work done externally)
  │
  ├─> 1. Return to App
  │     ├─ Open app after doing work
  │     └─ Navigate to "My Tasks"
  │
  ├─> 2. Find Claimed Task
  │     ├─ View list of claimed tasks
  │     ├─ Locate the worked-on task
  │     └─ Tap to open detail
  │
  ├─> 3. Review Task
  │     ├─ Verify completed externally
  │     ├─ Check all requirements met
  │     └─ Prepare result data
  │
  ├─> 4. Initiate Completion
  │     ├─ Tap "Complete Task" button
  │     └─ Open completion form
  │
  ├─> 5. Enter Results (Optional)
  │     ├─ Fill result form
  │     ├─ Add notes/comments
  │     ├─ Upload files (if needed)
  │     └─ Review entered data
  │
  ├─> 6. Confirm Completion
  │     ├─ Review summary
  │     ├─ Tap "Submit Completion"
  │     └─ Send to backend
  │
  ├─> 7. Process Completion
  │     ├─ Validate results
  │     ├─ Update task status
  │     └─ Record completion time
  │
  ├─> 8. Receive Confirmation
  │     ├─ Success toast
  │     ├─ Task moves to "Completed"
  │     └─ Statistics updated
  │
  └─> END (Success)

Alternative Paths:
  │
  └─> B. Completion Failed
        ├─ Validation error
        ├─ Error message shown
        └─ Fix and resubmit
```

### Steps in Detail

**Step 1: Return to App**
- User has completed work externally
- Opens app
- Navigates to "My Tasks" tab

**Step 2: Find Claimed Task**
- View list of claimed tasks
- Tasks sorted by claim time
- Locate specific task
- Tap card to open detail

**Step 3: Review Task**
- Verify work completed
- Check all requirements met
- Confirm ready to submit

**Step 4: Initiate Completion**
- Tap "Complete Task" button
- Bottom sheet opens with form

**Step 5: Enter Results**
- Fill result fields (if required)
- Add optional notes
- Attach files (if supported)
- Validate inputs

**Step 6: Confirm Completion**
- Review entered data
- Tap "Submit Completion" button
- Loading spinner appears

**Step 7: Process Completion**
- API request sent
- Backend validates
- Task status updated to "Completed"
- Timestamp recorded

**Step 8: Receive Confirmation**
- Success toast: "Task completed successfully!"
- Task removed from "My Tasks"
- Task appears in "Completed" tab
- Worker statistics updated

### Success Criteria
- ✅ Task status changed to "Completed"
- ✅ Results saved
- ✅ Task removed from active tasks
- ✅ Statistics updated

### Error Scenarios

**Validation Error**:
- Error: "Please fill all required fields"
- Highlight invalid fields
- Allow correction and resubmit

**Network Error**:
- Error: "Unable to submit. Check connection."
- Data saved locally (draft)
- Retry option available

---

## Task Creation Flow

### Purpose
Create a new task in the system.

### User Goal
Add a new task for workers to claim.

### Flow Diagram

```
START
  │
  ├─> 1. Navigate to Create
  │     ├─ Tap "Create Task" button
  │     └─ Open creation form
  │
  ├─> 2. Select Task Type
  │     ├─ Choose from dropdown
  │     └─ Validate selection
  │
  ├─> 3. Set Priority
  │     ├─ Select: Low/Medium/High
  │     └─ Default: Medium
  │
  ├─> 4. Enter Description
  │     ├─ Type task description
  │     └─ Validate length
  │
  ├─> 5. Set Max Attempts
  │     ├─ Enter number (1-5)
  │     └─ Default: 3
  │
  ├─> 6. Add Parameters (Optional)
  │     ├─ Enter JSON parameters
  │     └─ Validate syntax
  │
  ├─> 7. Review Task
  │     ├─ Check all fields
  │     └─ Verify correctness
  │
  ├─> 8. Submit Task
  │     ├─ Tap "Create Task" button
  │     └─ Send to backend
  │
  ├─> 9. Process Creation
  │     ├─ Validate task data
  │     ├─ Create task record
  │     └─ Generate task ID
  │
  ├─> 10. Receive Confirmation
  │      ├─ Success toast
  │      ├─ Navigate to task list
  │      └─ New task visible
  │
  └─> END (Success)
```

### Success Criteria
- ✅ Task created with unique ID
- ✅ Task visible in task list
- ✅ All required fields saved
- ✅ Confirmation shown to user

---

## Task Failure Flow

### Purpose
Report a task failure and optionally retry.

### User Goal
Mark a task as failed and document the reason.

### Flow Diagram

```
START (Task claimed, unable to complete)
  │
  ├─> 1. Identify Failure
  │     ├─ Encounter blocking issue
  │     └─ Decide cannot complete
  │
  ├─> 2. Navigate to Task
  │     ├─ Open task detail
  │     └─ Review situation
  │
  ├─> 3. Initiate Failure Report
  │     ├─ Tap "Report Failure" button
  │     └─ Open failure form
  │
  ├─> 4. Select Failure Reason
  │     ├─ Choose from list
  │     └─ Or select "Other"
  │
  ├─> 5. Enter Details
  │     ├─ Describe issue
  │     └─ Add relevant info
  │
  ├─> 6. Submit Failure
  │     ├─ Tap "Submit Failure" button
  │     └─ Send to backend
  │
  ├─> 7. Process Failure
  │     ├─ Update task status
  │     ├─ Increment attempt count
  │     └─ Check max attempts
  │
  ├─> 8. Determine Next Action
  │     ├─ If attempts < max: Return to pending
  │     ├─ If attempts >= max: Mark as failed
  │     └─ Notify user
  │
  └─> END
```

### Success Criteria
- ✅ Failure recorded
- ✅ Task status updated
- ✅ Reason documented
- ✅ Worker notified

---

## Error Recovery Flow

### Purpose
Handle and recover from errors.

### Common Errors
1. Network connectivity issues
2. API errors
3. Validation errors
4. Authentication errors

### Recovery Steps

**Network Error**:
```
1. Detect connection loss
2. Show error toast
3. Cache user action (if possible)
4. Provide retry button
5. Auto-retry when connection restored
```

**API Error**:
```
1. Receive error response
2. Parse error message
3. Display user-friendly message
4. Log technical details
5. Offer retry or contact support
```

**Validation Error**:
```
1. Detect invalid input
2. Highlight problem field
3. Show specific error message
4. Allow correction
5. Re-validate on change
```

---

## First-Time Onboarding

### Purpose
Introduce new users to the app.

### Flow Diagram

```
START (First app launch)
  │
  ├─> 1. Welcome Screen
  │     ├─ Show app name/logo
  │     ├─ Brief description
  │     └─ "Get Started" button
  │
  ├─> 2. Feature Tour (Optional)
  │     ├─ Screen 1: Browse tasks
  │     ├─ Screen 2: Claim and work
  │     ├─ Screen 3: Track progress
  │     └─ Skip or continue
  │
  ├─> 3. Setup
  │     ├─ Enter worker ID
  │     ├─ Enter API key
  │     └─ Validate credentials
  │
  ├─> 4. Preferences
  │     ├─ Enable notifications?
  │     ├─ Choose theme?
  │     └─ Save preferences
  │
  ├─> 5. Complete Onboarding
  │     ├─ Mark as onboarded
  │     ├─ Navigate to task list
  │     └─ Show "Get started" tips
  │
  └─> END (Ready to use)
```

---

**Created By**: Worker11 (UX Design Specialist)  
**Date**: 2025-11-09  
**Status**: ✅ Complete  
**Version**: 1.0.0
