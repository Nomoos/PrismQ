# Frontend/TaskManager - Component Library

**Version**: 1.0  
**Last Updated**: 2025-11-09  
**Audience**: Developers

---

## Views

### TaskList.vue

**Description**: Main page displaying all tasks with filtering capabilities.

**Location**: `src/views/TaskList.vue`

**Features**:
- Task cards with status indicators
- Filter tabs (All, Pending, Claimed, Completed, Failed)
- Loading and error states
- Pull-to-refresh support
- Click to navigate to task detail

**Usage**:
```vue
<!-- Routed automatically to "/" -->
<router-link to="/">Task List</router-link>
```

**Props**: None (uses route)

**Events**: None (navigation only)

---

### TaskDetail.vue

**Description**: Detailed view of a single task with claim/complete functionality.

**Location**: `src/views/TaskDetail.vue`

**Features**:
- Full task information display
- Claim button for pending tasks
- Progress update for claimed tasks
- Complete/fail buttons
- Back navigation

**Usage**:
```vue
<!-- Routed automatically -->
<router-link :to="`/tasks/${taskId}`">View Task</router-link>
```

**Props**: None (uses route params)

**Events**: None (uses store actions)

---

### WorkerDashboard.vue

**Description**: Dashboard for worker management and monitoring.

**Location**: `src/views/WorkerDashboard.vue`

**Features**:
- Worker initialization
- Worker status management (Active/Idle)
- Worker ID display
- Demo task claiming

**Usage**:
```vue
<router-link to="/workers">Worker Dashboard</router-link>
```

---

### Settings.vue

**Description**: Application settings and configuration.

**Location**: `src/views/Settings.vue`

**Features**:
- API configuration display
- About information
- Version display

**Usage**:
```vue
<router-link to="/settings">Settings</router-link>
```

---

## Styling Guide

### Color Scheme

**Status Colors**:
- Pending: Blue (`bg-blue-100`, `text-blue-800`)
- Claimed: Yellow (`bg-yellow-100`, `text-yellow-800`)
- Completed: Green (`bg-green-100`, `text-green-800`)
- Failed: Red (`bg-red-100`, `text-red-800`)

**UI Colors**:
- Primary: Blue 600 (`bg-blue-600`)
- Secondary: Gray 200 (`bg-gray-200`)
- Background: Gray 50 (`bg-gray-50`)
- Card: White (`bg-white`)

### Common Components

**Button Primary**:
```vue
<button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
  Click Me
</button>
```

**Button Secondary**:
```vue
<button class="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300">
  Cancel
</button>
```

**Card**:
```vue
<div class="bg-white rounded-lg shadow-sm p-4">
  Card content
</div>
```

**Badge**:
```vue
<span class="inline-block px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-800">
  Active
</span>
```

---

## Accessibility

All components follow WCAG 2.1 AA guidelines:

- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Touch Targets**: Minimum 44x44px
- **Color Contrast**: Minimum 4.5:1 for text
- **ARIA Labels**: Screen reader support
- **Focus Indicators**: Visible focus states

---

**Document Owner**: Worker06 (Documentation Specialist)  
**Last Updated**: 2025-11-09  
**Version**: 1.0  
**Status**: ✅ Complete
