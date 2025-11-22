# PrismQ Web Client - Adding Modules Guide

Guide for registering and configuring PrismQ modules with the Web Client.

## Table of Contents

- [Overview](#overview)
- [Module Registration](#module-registration)
- [Module Configuration Format](#module-configuration-format)
- [Parameter Types](#parameter-types)
- [Testing Modules](#testing-modules)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

The PrismQ Web Client discovers and runs modules defined in `Backend/configs/modules.json`. This guide explains how to add new modules to make them available through the web interface.

### Prerequisites

- Module Python script exists in the repository
- Module accepts command-line parameters
- Module outputs logs to stdout/stderr
- Module returns exit code 0 on success

## Module Registration

### Step 1: Locate Your Module

Find the Python script for your module:
```
PrismQ.T.Idea.Inspiration/
├── Sources/
│   └── Content/
│       └── Shorts/
│           └── YouTubeShorts/
│               └── src/
│                   └── main.py  ← Your module
```

### Step 2: Determine the Script Path

Calculate the relative path from `Backend/` to your module:
```
Backend/  ← Base directory
  → ../../Sources/Content/Shorts/YouTubeShorts/src/main.py
```

### Step 3: Add Module Entry

Edit `Backend/configs/modules.json` and add your module to the `modules` array:

```json
{
  "modules": [
    {
      "id": "youtube-shorts",
      "name": "YouTube Shorts Source",
      "description": "Collect trending YouTube Shorts videos",
      "category": "Sources/Content/Shorts",
      "script_path": "../../Sources/Content/Shorts/YouTubeShorts/src/main.py",
      "parameters": [
        {
          "name": "max_results",
          "type": "number",
          "default": 50,
          "required": true,
          "description": "Maximum number of videos to collect",
          "min": 1,
          "max": 500
        }
      ],
      "tags": ["youtube", "shorts", "video", "trending"]
    }
  ]
}
```

### Step 4: Restart Backend

Restart the backend server to load the new module:
```bash
# Stop the server (Ctrl+C)
# Start it again
uvicorn src.main:app --reload
```

### Step 5: Verify Module Appears

1. Open the Web Client: http://localhost:5173
2. Check that your module appears on the dashboard
3. Click "Launch" to verify the parameter form works

## Module Configuration Format

### Complete Module Schema

```json
{
  "id": "unique-module-identifier",
  "name": "Human Readable Module Name",
  "description": "Brief description of what this module does. Should be 1-2 sentences.",
  "category": "Category/Subcategory/Type",
  "script_path": "../../path/to/module/main.py",
  "version": "1.0.0",
  "author": "Your Name or Team",
  "parameters": [
    {
      "name": "parameter_name",
      "type": "text|number|select|checkbox|password",
      "default": "default_value",
      "required": true,
      "description": "What this parameter does",
      "placeholder": "Hint for user",
      "min": 1,
      "max": 1000,
      "step": 1,
      "options": ["option1", "option2"],
      "pattern": "^[a-z]+$"
    }
  ],
  "tags": ["tag1", "tag2", "tag3"]
}
```

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Unique identifier (lowercase, hyphens only) | `"youtube-shorts"` |
| `name` | Display name shown in UI | `"YouTube Shorts Source"` |
| `description` | Brief description for users | `"Collect trending YouTube Shorts videos"` |
| `category` | Hierarchical category | `"Sources/Content/Shorts"` |
| `script_path` | Path to Python script | `"../../Sources/.../main.py"` |
| `parameters` | Array of parameter definitions | `[...]` |

### Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
| `version` | Module version | `"1.0.0"` |
| `author` | Module author/team | `""` |
| `tags` | Search and filter tags | `[]` |

## Parameter Types

### Text Parameter

For string inputs like search queries, filenames, or API endpoints.

```json
{
  "name": "search_query",
  "type": "text",
  "default": "",
  "required": true,
  "description": "Search query for finding videos",
  "placeholder": "Enter keywords..."
}
```

**Optional Properties:**
- `placeholder`: Hint text in empty field
- `maxLength`: Maximum character length
- `pattern`: Regex pattern for validation

**Example with Validation:**
```json
{
  "name": "username",
  "type": "text",
  "default": "",
  "required": true,
  "description": "Twitter username (without @)",
  "placeholder": "username",
  "maxLength": 15,
  "pattern": "^[A-Za-z0-9_]+$"
}
```

### Number Parameter

For integer or decimal inputs.

```json
{
  "name": "max_results",
  "type": "number",
  "default": 50,
  "required": true,
  "description": "Maximum number of results to fetch",
  "min": 1,
  "max": 500,
  "step": 1
}
```

**Optional Properties:**
- `min`: Minimum allowed value
- `max`: Maximum allowed value
- `step`: Increment step (default: 1, use 0.1 for decimals)

**Example with Decimals:**
```json
{
  "name": "confidence_threshold",
  "type": "number",
  "default": 0.75,
  "required": false,
  "description": "Minimum confidence score (0.0-1.0)",
  "min": 0.0,
  "max": 1.0,
  "step": 0.01
}
```

### Select Parameter

For choosing one option from a predefined list.

```json
{
  "name": "trending_category",
  "type": "select",
  "default": "Gaming",
  "required": true,
  "description": "YouTube trending category",
  "options": [
    "Gaming",
    "Music",
    "Sports",
    "News",
    "Education",
    "Entertainment"
  ]
}
```

**Required Properties:**
- `options`: Array of string options

**Notes:**
- User can only select from provided options
- Default must be one of the options
- Options are displayed in the order specified

### Checkbox Parameter

For boolean on/off options.

```json
{
  "name": "include_metadata",
  "type": "checkbox",
  "default": true,
  "required": false,
  "description": "Include extended metadata in results"
}
```

**Properties:**
- `default`: `true` (checked) or `false` (unchecked)
- Checkbox parameters are typically not required

**Module Receives:**
- `true` if checked
- `false` if unchecked

### Password Parameter

For sensitive data like API keys or credentials.

```json
{
  "name": "api_key",
  "type": "password",
  "default": "",
  "required": true,
  "description": "YouTube Data API key"
}
```

**Security Features:**
- Input is masked in UI (shown as •••)
- NOT saved when user saves configuration
- Must be entered each time

**Notes:**
- Use for any sensitive data
- Consider using environment variables in module instead
- Module should handle missing/invalid keys gracefully

## Testing Modules

### 1. Validate JSON Syntax

```bash
cd Backend
python -m json.tool configs/modules.json
```

If valid, outputs formatted JSON. If invalid, shows error line.

### 2. Check Module Exists

```bash
# From Backend directory
python ../../Sources/Content/Shorts/YouTubeShorts/src/main.py --help
```

Should show module help or run without error.

### 3. Test Through API

```bash
# Get module list
curl http://localhost:8000/api/modules

# Get specific module
curl http://localhost:8000/api/modules/youtube-shorts
```

### 4. Test Through UI

1. Open Web Client: http://localhost:5173
2. Find your module card
3. Click "Launch"
4. Verify:
   - All parameters appear
   - Default values are correct
   - Validation works
   - Required fields are marked

### 5. Test Execution

1. Fill in parameters
2. Click "Launch"
3. Verify:
   - Module starts successfully
   - Logs appear in real-time
   - Status updates correctly
   - Module completes with success

### 6. Test Error Handling

Try invalid inputs:
- Out of range numbers
- Invalid text patterns
- Missing required fields

Verify appropriate error messages appear.

## Best Practices

### Module ID

- Use lowercase letters only
- Separate words with hyphens
- Be descriptive but concise
- Examples:
  - ✅ `youtube-shorts`
  - ✅ `reddit-trending-posts`
  - ✅ `twitter-hashtag-tracker`
  - ❌ `YT_Shorts` (uppercase)
  - ❌ `module1` (not descriptive)

### Module Name

- Use title case
- Be clear and specific
- Include platform/source
- Examples:
  - ✅ `YouTube Shorts Source`
  - ✅ `Reddit Trending Posts Collector`
  - ✅ `Twitter Hashtag Tracker`
  - ❌ `Shorts` (too vague)
  - ❌ `YT` (abbreviation)

### Description

- Keep to 1-2 sentences
- Explain what, not how
- Include key features or limitations
- Examples:
  - ✅ `Collect trending YouTube Shorts videos with metadata and statistics`
  - ✅ `Track trending posts from specified subreddits`
  - ❌ `A module` (too vague)
  - ❌ Three paragraphs of details (too long)

### Categories

Use consistent hierarchical structure:

```
Sources/          ← Data collection
  Content/        ← Content from platforms
    Shorts/       ← Short-form video
    Videos/       ← Long-form video
    Posts/        ← Text posts
  Signals/        ← Trend signals
    Trends/
    Hashtags/
  
Scoring/          ← Content evaluation
  Quality/
  Relevance/

Classification/   ← Categorization
  Topics/
  Sentiment/
```

### Parameters

**Order by importance:**
1. Required parameters first
2. Most commonly changed
3. Advanced options last

**Provide good defaults:**
```json
{
  "name": "max_results",
  "default": 50,  ← Reasonable default
  "min": 1,
  "max": 500
}
```

**Use clear descriptions:**
```json
{
  "description": "Maximum number of videos to collect (higher values take longer)"
}
```

### Tags

**Be specific and relevant:**
- ✅ `["youtube", "shorts", "video", "trending"]`
- ❌ `["social", "media", "internet", "data"]` (too generic)

**Keep to 3-6 tags:**
- Platform name
- Content type
- Collection method
- Domain/topic

## Examples

### Example 1: Simple Collection Module

```json
{
  "id": "reddit-posts",
  "name": "Reddit Posts Collector",
  "description": "Collect posts from specified subreddits",
  "category": "Sources/Content/Posts",
  "script_path": "../../Sources/Content/Posts/Reddit/src/main.py",
  "parameters": [
    {
      "name": "subreddit",
      "type": "text",
      "default": "programming",
      "required": true,
      "description": "Subreddit name (without r/)",
      "placeholder": "programming"
    },
    {
      "name": "max_posts",
      "type": "number",
      "default": 100,
      "required": true,
      "description": "Maximum number of posts to collect",
      "min": 1,
      "max": 1000
    },
    {
      "name": "sort_by",
      "type": "select",
      "default": "hot",
      "required": true,
      "description": "How to sort posts",
      "options": ["hot", "new", "top", "rising"]
    }
  ],
  "tags": ["reddit", "posts", "social"]
}
```

### Example 2: API-Based Module

```json
{
  "id": "twitter-hashtag",
  "name": "Twitter Hashtag Tracker",
  "description": "Track tweets for a specific hashtag",
  "category": "Sources/Signals/Hashtags",
  "script_path": "../../Sources/Signals/Hashtags/Twitter/src/main.py",
  "parameters": [
    {
      "name": "hashtag",
      "type": "text",
      "default": "",
      "required": true,
      "description": "Hashtag to track (without #)",
      "placeholder": "trending",
      "pattern": "^[A-Za-z0-9_]+$"
    },
    {
      "name": "api_key",
      "type": "password",
      "default": "",
      "required": true,
      "description": "Twitter API key"
    },
    {
      "name": "max_tweets",
      "type": "number",
      "default": 100,
      "required": true,
      "description": "Maximum tweets to collect",
      "min": 1,
      "max": 10000
    },
    {
      "name": "include_retweets",
      "type": "checkbox",
      "default": false,
      "required": false,
      "description": "Include retweets in results"
    }
  ],
  "tags": ["twitter", "hashtags", "trending"]
}
```

### Example 3: Processing Module

```json
{
  "id": "content-scorer",
  "name": "Content Quality Scorer",
  "description": "Score content quality using ML models",
  "category": "Scoring/Quality",
  "script_path": "../../Scoring/src/main.py",
  "parameters": [
    {
      "name": "input_file",
      "type": "text",
      "default": "",
      "required": true,
      "description": "Path to input data file",
      "placeholder": "/path/to/data.json"
    },
    {
      "name": "model_type",
      "type": "select",
      "default": "quality",
      "required": true,
      "description": "Scoring model to use",
      "options": ["quality", "relevance", "engagement"]
    },
    {
      "name": "threshold",
      "type": "number",
      "default": 0.7,
      "required": false,
      "description": "Minimum score threshold (0.0-1.0)",
      "min": 0.0,
      "max": 1.0,
      "step": 0.01
    },
    {
      "name": "verbose",
      "type": "checkbox",
      "default": false,
      "required": false,
      "description": "Enable verbose logging"
    }
  ],
  "tags": ["scoring", "quality", "ml"]
}
```

## Troubleshooting

### Module Doesn't Appear

**Check:**
1. JSON syntax is valid
2. Backend was restarted
3. No duplicate IDs
4. Browser cache cleared

### Parameters Don't Validate

**Check:**
1. `type` matches parameter value
2. `min`/`max` are reasonable
3. `options` contains `default` value
4. `pattern` regex is valid

### Module Won't Execute

**Check:**
1. `script_path` is correct (relative to Backend/)
2. Python script exists and is executable
3. Script accepts command-line parameters
4. Script has required dependencies installed

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more help.

## See Also

- [Configuration Reference](CONFIGURATION.md) - Detailed configuration options
- [User Guide](USER_GUIDE.md) - How to use modules
- [Development Guide](DEVELOPMENT.md) - Creating new modules

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-31  
**Maintained by**: PrismQ Development Team
