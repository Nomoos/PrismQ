# Screenshots Directory

This directory contains UI screenshots for the PrismQ Web Client documentation.

## Required Screenshots

The following screenshots are needed to complete Issue #112:

### 1. dashboard.png
- **Status**: Pending
- **Description**: Full dashboard showing module cards, search bar, and filter options
- **Size**: 1920x1080 (full screen)
- **Purpose**: USER_GUIDE.md - Dashboard Overview section

### 2. module-card.png
- **Status**: Pending
- **Description**: Single module card with details (name, description, category, tags, launch button)
- **Size**: ~600x400 (cropped to card)
- **Purpose**: USER_GUIDE.md - Module Cards section

### 3. launch-modal.png
- **Status**: Pending
- **Description**: Launch modal with parameter form and launch button
- **Size**: ~800x600 (cropped to modal)
- **Purpose**: USER_GUIDE.md - Launching Modules section

### 4. run-details.png
- **Status**: Pending
- **Description**: Run details page showing status, parameters, and log viewer
- **Size**: 1920x1080 (full screen)
- **Purpose**: USER_GUIDE.md - Monitoring Execution section

### 5. log-viewer.png
- **Status**: Pending
- **Description**: Log viewer with streaming logs showing timestamps and log levels
- **Size**: ~1200x600 (cropped to log section)
- **Purpose**: USER_GUIDE.md - Real-Time Log Streaming section

### 6. active-runs.png
- **Status**: Pending
- **Description**: List of active/running modules with progress indicators
- **Size**: ~1000x400 (cropped to runs list)
- **Purpose**: USER_GUIDE.md - Managing Runs section

### 7. api-docs.png
- **Status**: Pending
- **Description**: Swagger UI at http://localhost:8000/docs
- **Size**: 1920x1080 (full screen)
- **Purpose**: API.md - Interactive Documentation section

## Capture Instructions

Follow the guide in `../SCREENSHOTS_GUIDE.md` for detailed instructions on:
- Starting the Backend and Frontend servers
- Using browser DevTools to capture screenshots
- Platform-specific screenshot tools
- Quality guidelines and optimization

## Automated Capture

A Playwright script is available to automate screenshot capture:

```bash
# From the Client directory
npm install --save-dev playwright
npx playwright install chromium

# Run the capture script
node scripts/capture-screenshots.js
```

See `../SCREENSHOTS_GUIDE.md` for manual capture instructions.

---

**Note**: Screenshots are pending capture and will be added once the application is running.
