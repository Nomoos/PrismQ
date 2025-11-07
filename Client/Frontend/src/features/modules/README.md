# Modules Feature

## Overview

The Modules feature is a self-contained feature module that encapsulates all functionality related to PrismQ module discovery, configuration, and launching. This module follows the single responsibility principle and feature-based architecture.

## Structure

```
features/modules/
├── README.md                 # This documentation
├── index.ts                  # Main exports
├── components/               # Vue components
│   ├── index.ts
│   ├── ModuleCard.vue       # Module display card
│   ├── ModuleLaunchModal.vue # Module launch modal
│   └── ModuleTabs.vue       # Module category tabs
├── services/                 # API services
│   ├── index.ts
│   └── modules.ts           # Module API service
├── types/                    # TypeScript types
│   ├── index.ts
│   └── module.ts            # Module type definitions
└── composables/              # Composition functions (future)
    └── index.ts
```

## Responsibilities

This feature module is responsible for:

1. **Module Discovery**: Listing available PrismQ modules
2. **Module Configuration**: Managing module parameter configurations
3. **Module Launch**: Providing UI for launching modules with parameters
4. **Module Display**: Showing module metadata and status
5. **Parameter Validation**: Validating module parameters before launch

## Components

### ModuleCard

Displays a module as a card with its metadata, status, and launch button.

**Props:**
- `module`: Module object
- `readonly`: Whether the card is read-only (no launch button)

**Events:**
- `launch`: Emitted when user clicks launch button

**Usage:**
```vue
<ModuleCard :module="module" @launch="handleLaunch" />
```

### ModuleLaunchModal

Modal dialog for launching a module with parameter configuration.

**Props:**
- `module`: Module to launch
- `visible`: Whether modal is visible

**Events:**
- `close`: Emitted when modal is closed
- `launch`: Emitted when module is launched with parameters

**Usage:**
```vue
<ModuleLaunchModal 
  :module="selectedModule" 
  :visible="showModal" 
  @close="showModal = false"
  @launch="handleLaunch"
/>
```

### ModuleTabs

Tab navigation for module categories.

**Props:**
- `modules`: Array of modules
- `activeCategory`: Currently active category

**Events:**
- `category-change`: Emitted when category is changed

**Usage:**
```vue
<ModuleTabs 
  :modules="modules" 
  :activeCategory="category"
  @category-change="handleCategoryChange"
/>
```

## Services

### moduleService

API service for module operations.

**Methods:**

- `listModules()`: List all available modules
- `getModule(moduleId)`: Get details for a specific module
- `getConfig(moduleId)`: Get saved configuration for a module
- `saveConfig(moduleId, parameters)`: Save configuration for a module
- `deleteConfig(moduleId)`: Delete saved configuration
- `validateParameters(moduleId, parameters)`: Validate parameters

**Usage:**
```typescript
import { moduleService } from '@/features/modules'

// List modules
const modules = await moduleService.listModules()

// Get module
const module = await moduleService.getModule('youtube_channel_download')

// Get config
const config = await moduleService.getConfig('youtube_channel_download')

// Save config
await moduleService.saveConfig('youtube_channel_download', {
  channel_url: 'https://youtube.com/@example',
  max_videos: 10
})
```

## Types

### Module

Main module type definition.

**Fields:**
- `id`: string - Unique module identifier
- `name`: string - Human-readable name
- `description`: string - Module description
- `category`: string - Module category
- `parameters`: ModuleParameter[] - Parameter definitions
- `status`: 'active' | 'inactive' | 'maintenance'
- `enabled`: boolean - Whether module can be launched
- `lastRun`: string | null - Timestamp of last run
- `totalRuns`: number - Total number of runs
- `successRate`: number - Success rate percentage

### ModuleParameter

Parameter definition for module inputs.

**Fields:**
- `name`: string - Parameter name
- `type`: 'text' | 'number' | 'select' | 'checkbox' | 'password'
- `default`: any - Default value
- `required`: boolean - Whether parameter is required
- `description`: string - Parameter description
- `options`: string[] | null - Options for select type
- `min`: number | null - Minimum value for number type
- `max`: number | null - Maximum value for number type
- `placeholder`: string | null - Placeholder text
- `label`: string | null - Human-readable label
- `conditionalDisplay`: object | null - Conditional display rules
- `validation`: object | null - Validation rules
- `warning`: string | null - Warning message

### ModuleConfig

Configuration data for a module.

**Fields:**
- `module_id`: string - Module identifier
- `parameters`: Record<string, any> - Parameter values
- `updated_at`: string - Last update timestamp

## Integration

The modules feature is integrated into the main application through the Dashboard view:

```vue
<script setup lang="ts">
import { ModuleCard, ModuleLaunchModal, moduleService } from '@/features/modules'
import type { Module } from '@/features/modules'

const modules = ref<Module[]>([])
const selectedModule = ref<Module | null>(null)

onMounted(async () => {
  modules.value = await moduleService.listModules()
})
</script>

<template>
  <div>
    <ModuleCard 
      v-for="module in modules" 
      :key="module.id"
      :module="module"
      @launch="selectedModule = module"
    />
    
    <ModuleLaunchModal
      v-if="selectedModule"
      :module="selectedModule"
      :visible="!!selectedModule"
      @close="selectedModule = null"
    />
  </div>
</template>
```

## Single Responsibility Principle

This feature module follows the single responsibility principle by:

1. **Focused Scope**: Only handles module-related UI and operations
2. **Clear Boundaries**: Does not handle run execution (that's in the runs feature)
3. **Separated Concerns**: Components, services, and types are clearly separated
4. **Minimal Dependencies**: Only depends on shared utilities and base API service

## Future Enhancements

Potential future improvements:

1. **Composables**: Add composition functions for common module operations
2. **Validation**: Enhanced client-side parameter validation
3. **Search**: Module search and filtering functionality
4. **Favorites**: Mark favorite modules for quick access
5. **Recent**: Track recently launched modules
6. **Templates**: Save parameter templates for common configurations

## See Also

- [Backend Modules Module](../../../Backend/Modules/README.md)
- [Runs Feature](../runs/README.md) (when created)
- [System Feature](../system/README.md) (when created)
