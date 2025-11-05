# Issue #302: Improve Module Parameter Validation and Mode Switching in Web Client

**Priority**: MEDIUM  
**Type**: Enhancement  
**Module**: Client/Backend + Client/Frontend  
**Estimated**: 1 week  
**Assigned To**: Worker 3 - Full Stack Development  
**Dependencies**: None

---

## Problem Statement

The web client currently allows users to select different modes for the YouTube Shorts Source module (trending, channel, keyword), but the parameter validation and UI experience can be improved to better guide users and prevent invalid configurations.

### Current Behavior

1. **Static Parameter Form**: All parameters are shown regardless of selected mode
2. **No Dynamic Validation**: Required parameters for each mode are not clearly indicated
3. **No Mode-Specific Help**: Users don't get guidance on which parameters are needed for each mode
4. **Confusing UX**: Users might fill in parameters not used by the selected mode
5. **Limited Validation**: Only basic required field validation exists

### Example Issues

- User selects "trending" mode but fills in `channel_url` (which is ignored)
- User selects "channel" mode but doesn't fill in `channel_url` (required)
- User selects "keyword" mode but doesn't know it's not implemented yet
- No indication of which parameters are mode-specific vs. universal

---

## Requirements

### Functional Requirements

1. **Dynamic Parameter Display**
   - Show/hide parameters based on selected mode
   - Clearly indicate required vs. optional parameters
   - Update validation rules when mode changes
   - Provide mode-specific help text

2. **Mode-Specific Validation**
   - **Trending Mode**:
     - `max_results`: Optional (default: 50)
     - `category`: Optional (default: "All")
     - `channel_url`, `query`: Hide these (not used)
   
   - **Channel Mode**:
     - `channel_url`: Required, validate format
     - `max_results`: Optional (default: 50)
     - `query`, `category`: Hide these (not used)
   
   - **Keyword Mode**:
     - `query`: Required, validate non-empty
     - `max_results`: Optional (default: 50)
     - `channel_url`, `category`: Hide these (not used)
     - **Show warning**: "⚠️ Keyword search is currently in development (Issue #300)"

3. **Enhanced User Experience**
   - Mode selector with descriptions
   - Contextual help tooltips for each parameter
   - Real-time validation feedback
   - Clear error messages
   - Example values for parameters

4. **Backend Validation Enhancement**
   - Add mode-aware parameter validation
   - Return specific error messages for invalid combinations
   - Validate parameter formats (URLs, strings, numbers)
   - Prevent launching with incompatible parameter combinations

### Non-Functional Requirements

1. **User Experience**: Intuitive and guided parameter selection
2. **Consistency**: Follow existing web client UI patterns
3. **Performance**: Form updates should be instant (<100ms)
4. **Accessibility**: Proper labels and ARIA attributes

---

## Implementation Plan

### Phase 1: Backend Parameter Schema Enhancement (2 days)

1. **Extend Module Parameter Model**
   - [ ] Add `conditional_display` field to `ModuleParameter`
   - [ ] Add `validation_rules` field for mode-specific validation
   - [ ] Add `depends_on` field to indicate parameter dependencies
   - [ ] Update `modules.json` for YouTube Shorts with conditional logic

2. **Update Module Loader**
   - [ ] Modify `utils/module_loader.py` to parse conditional parameters
   - [ ] Support for parameter visibility rules
   - [ ] Support for mode-dependent validation

3. **Enhance Backend Validation**
   - [ ] Update `api/modules.py` validation function
   - [ ] Add mode-aware validation logic
   - [ ] Return mode-specific error messages
   - [ ] Add parameter format validation (URLs, etc.)

**Example Module Configuration:**

```json
{
  "id": "youtube-shorts",
  "parameters": [
    {
      "name": "mode",
      "type": "select",
      "options": ["trending", "channel", "keyword"],
      "default": "trending",
      "required": true,
      "label": "Scraping Mode",
      "description": "Choose how to collect YouTube Shorts"
    },
    {
      "name": "channel_url",
      "type": "text",
      "required": false,
      "label": "Channel URL",
      "description": "YouTube channel URL, handle (@username), or ID",
      "placeholder": "https://www.youtube.com/@channelname",
      "conditional_display": {
        "field": "mode",
        "value": "channel"
      },
      "validation": {
        "pattern": "^(https?://)?(www\\.)?youtube\\.com/(@[\\w-]+|channel/[\\w-]+)|@[\\w-]+|UC[\\w-]+$",
        "message": "Must be a valid YouTube channel URL, handle, or ID"
      }
    },
    {
      "name": "query",
      "type": "text",
      "required": false,
      "label": "Search Query",
      "description": "Keyword or phrase to search for",
      "placeholder": "startup ideas",
      "conditional_display": {
        "field": "mode",
        "value": "keyword"
      },
      "warning": "⚠️ Keyword search is in development. Currently shows trending results. (Issue #300)"
    },
    {
      "name": "max_results",
      "type": "number",
      "default": 50,
      "min": 1,
      "max": 100,
      "required": false,
      "label": "Maximum Results",
      "description": "Number of Shorts to collect"
    },
    {
      "name": "category",
      "type": "select",
      "options": ["All", "Gaming", "Music", "Entertainment", "Sports"],
      "default": "All",
      "required": false,
      "label": "Category Filter",
      "description": "Filter trending Shorts by category",
      "conditional_display": {
        "field": "mode",
        "value": "trending"
      }
    }
  ]
}
```

### Phase 2: Frontend Dynamic Form Implementation (2.5 days)

1. **Update Module Launch Modal**
   - [ ] Add mode selection prominently at top of form
   - [ ] Implement dynamic parameter visibility based on mode
   - [ ] Show/hide form fields when mode changes
   - [ ] Update validation rules dynamically

2. **Enhance Form Validation**
   - [ ] Implement mode-specific required field validation
   - [ ] Add real-time validation feedback (✓/✗ indicators)
   - [ ] Show validation errors inline
   - [ ] Disable launch button if validation fails

3. **Improve User Guidance**
   - [ ] Add mode descriptions (e.g., "Trending: Collect popular Shorts")
   - [ ] Add tooltips/help icons for each parameter
   - [ ] Show example values for complex parameters (channel URL)
   - [ ] Display warnings for known limitations (keyword mode)

4. **Visual Design**
   - [ ] Group mode selector separately from parameters
   - [ ] Use visual indicators for required fields (*)
   - [ ] Add icons for each mode (trending 📈, channel 👤, search 🔍)
   - [ ] Smooth transitions when showing/hiding fields

**Example Vue Component Structure:**

```vue
<template>
  <div class="module-launch-modal">
    <!-- Mode Selector Section -->
    <div class="mode-selector">
      <label>Scraping Mode</label>
      <select v-model="selectedMode" @change="onModeChange">
        <option value="trending">📈 Trending - Popular Shorts</option>
        <option value="channel">👤 Channel - Specific Creator</option>
        <option value="keyword">🔍 Keyword - Search (Beta)</option>
      </select>
      <p class="mode-description">{{ modeDescriptions[selectedMode] }}</p>
    </div>

    <!-- Dynamic Parameters Section -->
    <div class="parameters-form">
      <!-- Channel URL (only for channel mode) -->
      <div v-if="selectedMode === 'channel'" class="form-field required">
        <label>
          Channel URL *
          <TooltipIcon>YouTube channel URL, handle (@username), or ID</TooltipIcon>
        </label>
        <input
          v-model="parameters.channel_url"
          type="text"
          placeholder="https://www.youtube.com/@channelname"
          @blur="validateChannelUrl"
        />
        <ValidationMessage :errors="validationErrors.channel_url" />
      </div>

      <!-- Search Query (only for keyword mode) -->
      <div v-if="selectedMode === 'keyword'" class="form-field required">
        <label>Search Query *</label>
        <input v-model="parameters.query" type="text" placeholder="startup ideas" />
        <WarningMessage>
          ⚠️ Keyword search is in development. Currently shows trending results.
          <a href="#" @click="showIssue300">Learn more</a>
        </WarningMessage>
      </div>

      <!-- Category (only for trending mode) -->
      <div v-if="selectedMode === 'trending'" class="form-field">
        <label>Category Filter</label>
        <select v-model="parameters.category">
          <option>All</option>
          <option>Gaming</option>
          <option>Music</option>
          <!-- ... -->
        </select>
      </div>

      <!-- Max Results (always shown) -->
      <div class="form-field">
        <label>Maximum Results</label>
        <input v-model.number="parameters.max_results" type="number" min="1" max="100" />
      </div>
    </div>

    <!-- Actions -->
    <div class="modal-actions">
      <button @click="cancel">Cancel</button>
      <button @click="launch" :disabled="!isValid">Launch Module</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedMode: 'trending',
      parameters: {
        mode: 'trending',
        channel_url: '',
        query: '',
        max_results: 50,
        category: 'All'
      },
      validationErrors: {},
      modeDescriptions: {
        trending: 'Collect currently popular YouTube Shorts',
        channel: 'Collect Shorts from a specific channel',
        keyword: 'Search for Shorts by keyword (Beta - Issue #300)'
      }
    }
  },
  computed: {
    isValid() {
      if (this.selectedMode === 'channel') {
        return this.parameters.channel_url && !this.validationErrors.channel_url
      }
      if (this.selectedMode === 'keyword') {
        return this.parameters.query.trim() !== ''
      }
      return true // Trending mode has no required fields
    }
  },
  methods: {
    onModeChange() {
      this.parameters.mode = this.selectedMode
      this.clearUnusedParameters()
      this.validationErrors = {}
    },
    clearUnusedParameters() {
      // Clear parameters not used by current mode
      if (this.selectedMode !== 'channel') {
        this.parameters.channel_url = ''
      }
      if (this.selectedMode !== 'keyword') {
        this.parameters.query = ''
      }
      if (this.selectedMode !== 'trending') {
        this.parameters.category = 'All'
      }
    },
    validateChannelUrl() {
      const pattern = /^(https?:\/\/)?(www\.)?youtube\.com\/([@\w-]+|channel\/[\w-]+)|@[\w-]+|UC[\w-]+$/
      if (!pattern.test(this.parameters.channel_url)) {
        this.validationErrors.channel_url = 'Must be a valid YouTube channel URL, handle, or ID'
      } else {
        delete this.validationErrors.channel_url
      }
    },
    async launch() {
      // Clean parameters object before sending
      const cleanedParams = { mode: this.selectedMode }
      
      if (this.selectedMode === 'channel') {
        cleanedParams.channel_url = this.parameters.channel_url
      } else if (this.selectedMode === 'keyword') {
        cleanedParams.query = this.parameters.query
      } else if (this.selectedMode === 'trending') {
        cleanedParams.category = this.parameters.category
      }
      
      cleanedParams.max_results = this.parameters.max_results
      
      // Launch module with cleaned parameters
      await this.launchModule(cleanedParams)
    }
  }
}
</script>
```

### Phase 3: Testing (1.5 days)

1. **Frontend Tests**
   - [ ] Test mode switching shows/hides correct parameters
   - [ ] Test validation for each mode
   - [ ] Test form submission with valid/invalid data
   - [ ] Test parameter clearing when mode changes

2. **Backend Tests**
   - [ ] Test mode-aware parameter validation
   - [ ] Test invalid parameter combinations are rejected
   - [ ] Test format validation (channel URLs)
   - [ ] Test error message specificity

3. **Integration Tests**
   - [ ] Test launching each mode from web client
   - [ ] Test invalid launches are prevented
   - [ ] Test validation error messages display correctly
   - [ ] Test parameter persistence per mode

4. **User Acceptance Testing**
   - [ ] Verify UX is intuitive
   - [ ] Verify error messages are helpful
   - [ ] Verify warnings are clear (keyword mode)
   - [ ] Verify no confusion about parameter requirements

---

## Success Criteria

- [ ] Parameters show/hide based on selected mode
- [ ] Required parameters clearly indicated with validation
- [ ] Real-time validation feedback for user input
- [ ] Mode-specific help text and tooltips
- [ ] Warning shown for keyword mode limitation
- [ ] Backend rejects invalid parameter combinations
- [ ] Error messages are specific and helpful
- [ ] Form cannot be submitted with invalid data
- [ ] Smooth UX with no jarring transitions
- [ ] All tests passing with >80% coverage
- [ ] Documentation updated with new parameter behavior

---

## UI Mockup

### Mode Selection
```
┌────────────────────────────────────────────────────┐
│ Launch Module: YouTube Shorts Source               │
├────────────────────────────────────────────────────┤
│                                                     │
│  Scraping Mode                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │ ▼ 📈 Trending - Popular Shorts              │ │
│  └──────────────────────────────────────────────┘ │
│  Collect currently popular YouTube Shorts         │
│                                                     │
│  ─────────────────────────────────────────────────│
│                                                     │
│  Category Filter                                   │
│  ┌──────────────────────────────────────────────┐ │
│  │ ▼ All                                        │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  Maximum Results                                   │
│  ┌──────────────────────────────────────────────┐ │
│  │ 50                                           │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  ┌────────┐  ┌───────────────────┐               │
│  │ Cancel │  │ 🚀 Launch Module  │               │
│  └────────┘  └───────────────────┘               │
└────────────────────────────────────────────────────┘
```

### Channel Mode (After Switching)
```
┌────────────────────────────────────────────────────┐
│ Launch Module: YouTube Shorts Source               │
├────────────────────────────────────────────────────┤
│                                                     │
│  Scraping Mode                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │ ▼ 👤 Channel - Specific Creator             │ │
│  └──────────────────────────────────────────────┘ │
│  Collect Shorts from a specific channel           │
│                                                     │
│  ─────────────────────────────────────────────────│
│                                                     │
│  Channel URL * ⓘ                                  │
│  ┌──────────────────────────────────────────────┐ │
│  │ https://www.youtube.com/@channelname         │ │
│  └──────────────────────────────────────────────┘ │
│  ✓ Valid channel URL                              │
│                                                     │
│  Maximum Results                                   │
│  ┌──────────────────────────────────────────────┐ │
│  │ 50                                           │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  ┌────────┐  ┌───────────────────┐               │
│  │ Cancel │  │ 🚀 Launch Module  │               │
│  └────────┘  └───────────────────┘               │
└────────────────────────────────────────────────────┘
```

### Keyword Mode with Warning
```
┌────────────────────────────────────────────────────┐
│ Launch Module: YouTube Shorts Source               │
├────────────────────────────────────────────────────┤
│                                                     │
│  Scraping Mode                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │ ▼ 🔍 Keyword - Search (Beta)                │ │
│  └──────────────────────────────────────────────┘ │
│  Search for Shorts by keyword (Beta - Issue #300) │
│                                                     │
│  ─────────────────────────────────────────────────│
│                                                     │
│  Search Query * ⓘ                                 │
│  ┌──────────────────────────────────────────────┐ │
│  │ startup ideas                                │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  ⚠️  Keyword search is in development.            │
│     Currently shows trending results.              │
│     Learn more: Issue #300                        │
│                                                     │
│  Maximum Results                                   │
│  ┌──────────────────────────────────────────────┐ │
│  │ 50                                           │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  ┌────────┐  ┌───────────────────┐               │
│  │ Cancel │  │ 🚀 Launch Module  │               │
│  └────────┘  └───────────────────┘               │
└────────────────────────────────────────────────────┘
```

---

## Related Issues

- **Issue #300**: Implement YouTube Shorts Keyword Search Mode (warning references this)
- **Issue #301**: Document YouTube Shorts Module Flow (documents parameter flow)
- **Web Client #105**: Frontend Module UI (✅ Complete - will enhance this)
- **Web Client #106**: Parameter Persistence (✅ Complete - will integrate with)

---

## References

### Code Locations

- **Backend Module API**: `Client/Backend/src/api/modules.py`
- **Module Loader**: `Client/Backend/src/utils/module_loader.py`
- **Module Models**: `Client/Backend/src/models/module.py`
- **Frontend Module Component**: `Client/Frontend/src/components/ModuleLaunchModal.vue`
- **Module Configuration**: `Client/Backend/configs/modules.json`

### Design References

- Existing parameter forms in web client
- Vue 3 form validation patterns
- Material Design form guidelines

---

## Notes

- This enhancement significantly improves **user experience**
- Prevents common **user errors** (invalid parameter combinations)
- Makes **limitations clear** (keyword mode warning)
- Can be implemented **independently** without blocking other issues
- Works for **all modules** with mode-based parameters (extensible pattern)
- Estimated effort: **1 week** for full implementation with tests

---

**Status**: Ready to Start  
**Created**: 2025-11-04  
**Last Updated**: 2025-11-04
