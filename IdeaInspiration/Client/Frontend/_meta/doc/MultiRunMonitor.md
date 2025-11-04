# MultiRunMonitor Component

## Overview

The `MultiRunMonitor` component provides a tabbed interface for monitoring multiple PrismQ module runs simultaneously. It enables users to view live logs from different runs and switch between them easily.

## Features

- 📑 **Tabbed Interface** - Monitor multiple runs in separate tabs
- 🔴 **Status Indicators** - Visual status with animated pulse for running processes
- 📊 **Live Log Streaming** - Real-time log updates via LogViewer integration
- 🔄 **Auto-Refresh** - Polls for status updates every 5 seconds (only for active runs)
- ⌨️ **Keyboard Navigation** - Full keyboard accessibility
- 🧹 **Smart Cleanup** - Automatic resource cleanup on unmount

## Usage

### Basic Usage

```vue
<template>
  <div>
    <MultiRunMonitor ref="monitorRef" />
    <button @click="addRunToMonitor">Add Run</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import MultiRunMonitor from '@/components/MultiRunMonitor.vue'
import type { Run } from '@/types/run'

const monitorRef = ref<InstanceType<typeof MultiRunMonitor>>()

function addRunToMonitor() {
  const run: Run = {
    run_id: 'run-123',
    module_id: 'classification',
    module_name: 'Classification Module',
    status: 'running',
    parameters: {},
    created_at: new Date().toISOString()
  }
  
  monitorRef.value?.addRun(run)
}
</script>
```

### Advanced Usage with Active Runs

```vue
<template>
  <div>
    <ActiveRuns @run-selected="addToMonitor" />
    <MultiRunMonitor ref="monitorRef" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ActiveRuns from '@/components/ActiveRuns.vue'
import MultiRunMonitor from '@/components/MultiRunMonitor.vue'
import type { Run } from '@/types/run'

const monitorRef = ref<InstanceType<typeof MultiRunMonitor>>()

function addToMonitor(run: Run) {
  monitorRef.value?.addRun(run)
}
</script>
```

## Exposed Methods

### `addRun(run: Run)`

Add a run to the monitoring tabs.

**Parameters:**
- `run` - Run object containing run_id, module_name, status, etc.

**Behavior:**
- If the run is already being monitored, switches to that tab
- If it's a new run, creates a new tab and switches to it
- Validates that the run has a valid ID before adding

**Example:**
```typescript
monitorRef.value?.addRun({
  run_id: 'run-123',
  module_name: 'Test Module',
  status: 'running',
  // ... other properties
})
```

### `removeRun(runId: string)`

Remove a specific run from monitoring.

**Parameters:**
- `runId` - The ID of the run to remove

**Behavior:**
- Removes the tab for the specified run
- If removing the active tab, switches to the previous tab
- If no tabs remain, shows empty state

**Example:**
```typescript
monitorRef.value?.removeRun('run-123')
```

### `clearAll()`

Remove all monitored runs and reset to empty state.

**Example:**
```typescript
monitorRef.value?.clearAll()
```

## Status Indicators

The component shows colored status indicators for each run:

| Status | Color | Animation |
|--------|-------|-----------|
| `queued` | 🟡 Yellow | None |
| `running` | 🔵 Blue | Pulse |
| `completed` | 🟢 Green | None |
| `failed` | 🔴 Red | None |
| `cancelled` | ⚪ Gray | None |

## Keyboard Shortcuts

- `Tab` - Navigate between tabs
- `Enter` or `Space` - Close the focused tab
- `Escape` - (LogViewer) Stop log streaming

## Performance Optimization

The component is optimized for performance:

1. **Smart Polling**: Only polls for runs with `running` or `queued` status
2. **Minimal Re-renders**: Uses Vue 3 reactivity to update only changed data
3. **Automatic Cleanup**: Stops polling and cleans up resources on unmount
4. **Lazy Loading**: LogViewer is only rendered for the active tab

## Integration with RunService

The component integrates with the run service API:

```typescript
// Auto-polls every 5 seconds for active runs
const updated = await runService.getRun(runId)
```

## Styling

The component uses Tailwind CSS utility classes and is fully responsive. You can customize the appearance by overriding these CSS classes:

```css
.multi-run-monitor { /* Main container */ }
.tabs { /* Tab bar */ }
.tab { /* Individual tab */ }
.tab.active { /* Active tab */ }
.status-indicator { /* Status dot */ }
.close-btn { /* Close button */ }
.tab-content { /* Log viewer container */ }
```

## Accessibility

The component follows WCAG 2.1 guidelines:

- ✅ Keyboard navigation
- ✅ ARIA roles and labels
- ✅ Focus management
- ✅ Screen reader support

## Example: Full Integration

```vue
<template>
  <div class="dashboard">
    <!-- Active Runs Section -->
    <section>
      <h2>Active Runs</h2>
      <ActiveRuns @run-clicked="monitorRun" />
    </section>
    
    <!-- Multi-Run Monitor -->
    <section>
      <h2>Run Monitor</h2>
      <MultiRunMonitor ref="monitorRef" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ActiveRuns from '@/components/ActiveRuns.vue'
import MultiRunMonitor from '@/components/MultiRunMonitor.vue'
import type { Run } from '@/types/run'

const monitorRef = ref<InstanceType<typeof MultiRunMonitor>>()

function monitorRun(run: Run) {
  monitorRef.value?.addRun(run)
}
</script>
```

## Testing

The component has comprehensive test coverage:

```bash
# Run tests
npm test -- MultiRunMonitor

# Run with coverage
npm run coverage -- MultiRunMonitor
```

See `_meta/tests/Frontend/unit/MultiRunMonitor.spec.ts` for test examples.

## Related Components

- **ActiveRuns** - Displays list of active runs
- **RunHistory** - Shows historical runs with filtering
- **LogViewer** - Displays live logs for a run
- **StatusBadge** - Shows run status badge

## Troubleshooting

### Run not showing in tabs

**Issue**: Added a run but it doesn't appear in tabs

**Solution**: Check that the run object has either `run_id` or `id` property:
```typescript
// ✅ Correct
{ run_id: 'run-123', ... }

// ❌ Incorrect
{ some_id: 'run-123', ... }
```

### Polling not working

**Issue**: Run status not updating

**Solution**: 
1. Check browser console for API errors
2. Verify the run has status `running` or `queued` (completed runs don't poll)
3. Check that EventSource connection is active in LogViewer

### Memory leak concerns

**Issue**: Worried about memory usage with many tabs

**Solution**: The component:
- Only polls active (running/queued) runs
- Cleans up resources on unmount
- Uses Vue 3's efficient reactivity system

Recommended: Don't monitor more than 10 concurrent runs for best performance.

## Future Enhancements

Potential improvements (not yet implemented):

- [ ] Batch API calls for updating multiple runs
- [ ] Desktop notifications for run completion
- [ ] Drag-and-drop tab reordering
- [ ] Tab grouping by module type
- [ ] Export logs from all tabs at once
