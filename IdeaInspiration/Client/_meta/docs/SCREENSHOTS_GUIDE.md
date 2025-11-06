# Screenshots Guide for PrismQ Web Client

This guide explains how to capture and add screenshots to the documentation.

## Required Screenshots

To complete the visual documentation, we need screenshots of:

### 1. Dashboard View
- **File**: `screenshots/dashboard.png`
- **What to capture**: 
  - Full dashboard showing module cards
  - Search bar
  - Filter options
  - At least 3-4 module cards visible
- **Purpose**: Show main interface in USER_GUIDE.md
- **Size**: 1920x1080 or similar (full screen)

### 2. Module Card Detail
- **File**: `screenshots/module-card.png`
- **What to capture**:
  - Single module card with all details
  - Name, description, category
  - Tags and status badge
  - Launch button
- **Purpose**: Show module information in USER_GUIDE.md
- **Size**: Crop to just the card (~600x400)

### 3. Launch Modal
- **File**: `screenshots/launch-modal.png`
- **What to capture**:
  - Launch modal dialog
  - Parameter form fields
  - "Remember parameters" checkbox
  - Launch button
- **Purpose**: Show parameter configuration in USER_GUIDE.md
- **Size**: Crop to modal (~800x600)

### 4. Run Details Page
- **File**: `screenshots/run-details.png`
- **What to capture**:
  - Full run details page
  - Status section
  - Parameters section
  - Real-time log viewer with logs
- **Purpose**: Show monitoring interface in USER_GUIDE.md
- **Size**: 1920x1080 or similar (full screen)

### 5. Log Viewer
- **File**: `screenshots/log-viewer.png`
- **What to capture**:
  - Log viewer with streaming logs
  - Timestamps visible
  - Different log levels (INFO, WARNING, ERROR)
  - Auto-scroll toggle
- **Purpose**: Show log streaming in USER_GUIDE.md
- **Size**: Crop to log section (~1200x600)

### 6. Active Runs List
- **File**: `screenshots/active-runs.png`
- **What to capture**:
  - List of active/running modules
  - Progress indicators
  - Status badges
  - Duration timers
- **Purpose**: Show multi-run monitoring in USER_GUIDE.md
- **Size**: Crop to runs list (~1000x400)

### 7. API Documentation (Swagger UI)
- **File**: `screenshots/api-docs.png`
- **What to capture**:
  - Swagger UI at http://localhost:8000/docs
  - Expanded endpoint showing request/response
  - Try-it-out functionality
- **Purpose**: Show API documentation in API.md
- **Size**: 1920x1080 or similar (full screen)

## How to Capture Screenshots

### Prerequisites

1. **Start Backend**:
   ```bash
   cd Client/Backend
   source venv/bin/activate  # Windows: venv\Scripts\activate
   uvicorn src.main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd Client/Frontend
   npm run dev
   ```

3. **Open Browser**:
   - Navigate to http://localhost:5173
   - Open DevTools (F12) and set responsive view to 1920x1080
   - Ensure modules are configured in `Backend/configs/modules.json`

### Capture Steps

#### On Windows

**Method 1: Snipping Tool**
1. Press `Win + Shift + S`
2. Select area to capture
3. Screenshot copies to clipboard
4. Open Paint or image editor
5. Paste (Ctrl+V)
6. Save as PNG

**Method 2: Full Screen**
1. Press `PrtScn` for full screen
2. Or `Alt + PrtScn` for active window
3. Paste into image editor
4. Crop if needed
5. Save as PNG

**Method 3: Browser DevTools**
1. Open DevTools (F12)
2. Press `Ctrl + Shift + P`
3. Type "screenshot"
4. Choose "Capture full size screenshot" or "Capture screenshot"
5. Image downloads automatically

#### On Linux

**Method 1: GNOME Screenshot**
```bash
gnome-screenshot -a  # Select area
gnome-screenshot -w  # Window
gnome-screenshot     # Full screen
```

**Method 2: scrot**
```bash
scrot screenshot.png          # Full screen
scrot -s screenshot.png       # Select area
scrot -u screenshot.png       # Active window
```

**Method 3: Browser DevTools**
1. Open DevTools (F12)
2. Press `Ctrl + Shift + P`
3. Type "screenshot"
4. Choose "Capture full size screenshot"

#### On macOS

**Method 1: Built-in Tool**
- `Cmd + Shift + 3` - Full screen
- `Cmd + Shift + 4` - Select area
- `Cmd + Shift + 4` then `Space` - Window

**Method 2: Browser DevTools**
1. Open DevTools (Cmd + Option + I)
2. Press `Cmd + Shift + P`
3. Type "screenshot"
4. Choose screenshot type

### Screenshot Quality Guidelines

1. **Resolution**: Minimum 1920x1080 for full-screen shots
2. **Format**: PNG (not JPEG - better for UI screenshots)
3. **Compression**: Optimize with tools like TinyPNG if needed
4. **Content**: 
   - Remove any personal information
   - Use placeholder data (no real API keys)
   - Ensure text is readable
   - Show realistic but not sensitive data

5. **Consistency**:
   - Same browser (Chrome recommended)
   - Same zoom level (100%)
   - Same theme/styling
   - Consistent data across screenshots

## Screenshot Organization

Create the following directory structure:

```
Client/
├── docs/
│   ├── screenshots/
│   │   ├── dashboard.png
│   │   ├── module-card.png
│   │   ├── launch-modal.png
│   │   ├── run-details.png
│   │   ├── log-viewer.png
│   │   ├── active-runs.png
│   │   └── api-docs.png
│   └── USER_GUIDE.md
```

## Adding Screenshots to Documentation

### In USER_GUIDE.md

Add screenshots using Markdown image syntax:

```markdown
## Dashboard Overview

The dashboard is your main control center for managing PrismQ modules.

![Dashboard Screenshot](screenshots/dashboard.png)

### Module Cards

Each module is displayed as a card showing key information:

![Module Card](screenshots/module-card.png)

### Launching Modules

Click the "Launch" button to configure and run a module:

![Launch Modal](screenshots/launch-modal.png)
```

### In README.md

Add a screenshot showcase section:

```markdown
## Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Module Execution
![Run Details](docs/screenshots/run-details.png)

### Real-Time Logs
![Log Viewer](docs/screenshots/log-viewer.png)
```

### In API.md

Add Swagger UI screenshot:

```markdown
## Interactive Documentation

Access the Swagger UI at http://localhost:8000/docs:

![API Documentation](screenshots/api-docs.png)
```

## Creating Demo Data

To make screenshots more realistic, create demo data:

### 1. Configure Test Modules

Edit `Backend/configs/modules.json` to include several modules:

```json
{
  "modules": [
    {
      "id": "youtube-shorts",
      "name": "YouTube Shorts Source",
      "description": "Collect trending YouTube Shorts videos",
      "category": "Sources/Content/Shorts",
      "tags": ["youtube", "shorts", "video", "trending"]
    },
    {
      "id": "tiktok-trends",
      "name": "TikTok Trends Collector",
      "description": "Track trending TikTok content and hashtags",
      "category": "Sources/Content/Shorts",
      "tags": ["tiktok", "trends", "social"]
    },
    {
      "id": "reddit-posts",
      "name": "Reddit Posts Scraper",
      "description": "Collect posts from specified subreddits",
      "category": "Sources/Community/Forums",
      "tags": ["reddit", "forum", "community"]
    }
  ]
}
```

### 2. Launch Test Runs

Launch modules to populate run history and active runs:

```bash
# Use the web interface or API to launch 2-3 modules
curl -X POST http://localhost:8000/api/runs \
  -H "Content-Type: application/json" \
  -d '{
    "module_id": "youtube-shorts",
    "parameters": {"max_results": 50},
    "save_config": false
  }'
```

### 3. Prepare Log Data

For log viewer screenshots, you may want a module that outputs visible logs. Create a test script if needed:

```python
# test_module.py
import time
import sys

for i in range(1, 51):
    print(f"[INFO] Processing item {i}/50")
    if i % 10 == 0:
        print(f"[WARNING] Checkpoint reached: {i} items processed")
    time.sleep(1)
    sys.stdout.flush()

print("[INFO] Collection complete!")
```

## Automation (Optional)

For automated screenshot capture, use tools like:

### Playwright (Node.js)

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // Set viewport
  await page.setViewportSize({ width: 1920, height: 1080 });
  
  // Dashboard
  await page.goto('http://localhost:5173');
  await page.waitForLoadState('networkidle');
  await page.screenshot({ path: 'docs/screenshots/dashboard.png' });
  
  // Module card (click to open modal)
  await page.click('button:has-text("Launch")');
  await page.waitForSelector('.modal');
  await page.screenshot({ path: 'docs/screenshots/launch-modal.png' });
  
  await browser.close();
})();
```

### Puppeteer (Node.js)

```javascript
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  await page.setViewport({ width: 1920, height: 1080 });
  await page.goto('http://localhost:5173');
  await page.screenshot({ path: 'docs/screenshots/dashboard.png', fullPage: true });
  
  await browser.close();
})();
```

## Screenshot Checklist

Before considering screenshots complete:

- [ ] Dashboard screenshot shows module cards
- [ ] Module card detail is clear and readable
- [ ] Launch modal shows parameter form
- [ ] Run details page shows all sections
- [ ] Log viewer shows actual log entries
- [ ] Active runs list shows multiple runs
- [ ] API docs screenshot shows Swagger UI
- [ ] All screenshots are PNG format
- [ ] All screenshots are properly sized
- [ ] All text in screenshots is readable
- [ ] Screenshots are added to documentation
- [ ] Screenshots are committed to git (if size appropriate)

## Alternative: Placeholder Images

If you cannot capture screenshots immediately, add placeholders:

```markdown
## Dashboard Overview

![Dashboard Screenshot - Coming Soon](https://via.placeholder.com/1920x1080.png?text=Dashboard+Screenshot+Coming+Soon)

> **Note**: Screenshot will be added once the application is deployed.
```

Or use descriptive text blocks:

```markdown
## Dashboard Overview

**Screenshot Description**:
The dashboard displays a grid of module cards. Each card shows:
- Module name and description
- Category badge
- Status indicator
- Launch button
- Tags for filtering
```

## Next Steps

After capturing all screenshots:

1. **Optimize Images**:
   ```bash
   # Using ImageMagick
   mogrify -resize 1920x1080 -quality 85 docs/screenshots/*.png
   
   # Using pngquant
   pngquant --quality=85 docs/screenshots/*.png
   ```

2. **Update Documentation**:
   - Add images to USER_GUIDE.md
   - Add images to README.md
   - Add images to API.md
   - Test that images display correctly

3. **Commit to Repository**:
   ```bash
   git add docs/screenshots/
   git add docs/USER_GUIDE.md docs/README.md docs/API.md
   git commit -m "Add UI screenshots to documentation"
   ```

4. **Verify in GitHub**:
   - Push changes
   - Check that images display in GitHub's Markdown viewer
   - Verify image links work

---

**Status**: Screenshots pending  
**Priority**: Medium  
**Blocked by**: None (can be done anytime after UI is running)  
**Last Updated**: 2025-10-31
