# MANUAL-TEST-006: Client (Web Management Interface) Manual Testing

**Module**: PrismQ.Client  
**Type**: Manual Testing  
**Priority**: High  
**Status**: 🧪 READY FOR TESTING

---

## Overview

Manual testing issue for the Client (Web Management Interface) module. The user will run the web client in a preview environment and provide logs for analysis.

---

## Module Description

The **Client** module is a web-based task queue management system built with the TaskManager module, providing a complete task queue system with backend API and frontend UI.

### Key Components

| Component | Path | Technology | Description |
|-----------|------|------------|-------------|
| **Backend** | `Client/Backend/TaskManager/` | PHP | Lightweight REST API for shared hosting |
| **Frontend** | `Client/Frontend/TaskManager/` | Vue 3 | Mobile-first web interface |

### Architecture Features

- **On-demand architecture**: All operations triggered by HTTP requests (no background processes)
- **JSON Schema validation**: Task parameters validated against schemas
- **Worker coordination**: Claim/complete workflow with timeout handling
- **Data-driven API**: REST endpoints defined in database, not code
- **Production ready**: Comprehensive test coverage and deployment automation

---

## Testing Checklist

### 1. Backend TaskManager Tests

#### REST API Tests
- [ ] **API Endpoints**: Test all REST endpoints
- [ ] **JSON Schema Validation**: Test task parameter validation
- [ ] **Authentication**: Test API authentication (if applicable)
- [ ] **Error Handling**: Test API error responses

#### Worker Coordination Tests
- [ ] **Task Claim**: Test worker claiming tasks
- [ ] **Task Complete**: Test task completion workflow
- [ ] **Timeout Handling**: Test timeout handling for stale tasks
- [ ] **Concurrent Workers**: Test multiple worker coordination

#### Database Tests
- [ ] **Data Persistence**: Test task data persistence
- [ ] **Query Performance**: Test database query performance
- [ ] **Data Integrity**: Test data integrity constraints

### 2. Frontend TaskManager Tests

#### UI Tests
- [ ] **Task List View**: Test task list display
- [ ] **Task Details View**: Test task detail view
- [ ] **Task Creation**: Test new task creation form
- [ ] **Task Editing**: Test task editing interface
- [ ] **Task Status Updates**: Test real-time status updates

#### Mobile-First Tests
- [ ] **Responsive Design**: Test on mobile viewport
- [ ] **Touch Interactions**: Test touch-friendly controls
- [ ] **Mobile Navigation**: Test mobile menu/navigation

#### Integration Tests
- [ ] **API Communication**: Test frontend-backend communication
- [ ] **Error Display**: Test error message display
- [ ] **Loading States**: Test loading indicators

### 3. Workflow Tests
- [ ] **Task Queue Management**: Test task queue operations
- [ ] **Worker Progress Tracking**: Test progress monitoring
- [ ] **Task Prioritization**: Test priority handling

---

## Test Commands

### Backend Tests
```bash
# Navigate to backend
cd /home/runner/work/PrismQ/PrismQ/Client/Backend/TaskManager

# Start local PHP server (for testing)
cd src
php -S localhost:8000

# Run backend tests
php vendor/bin/phpunit tests/
```

### Frontend Tests
```bash
# Navigate to frontend
cd /home/runner/work/PrismQ/PrismQ/Client/Frontend/TaskManager

# Install dependencies
npm install

# Run development server
npm run dev

# Run frontend tests
npm run test

# Run end-to-end tests
npm run test:e2e
```

### Playwright E2E Tests
```bash
# Navigate to Client directory
cd /home/runner/work/PrismQ/PrismQ/Client

# Run Playwright tests
npx playwright test
```

---

## Expected Logs to Capture

### Backend Logs
1. **HTTP Request Logs**: Incoming request details
2. **Database Query Logs**: SQL query execution
3. **Worker Activity Logs**: Worker claim/complete events
4. **Error Logs**: Any PHP errors or warnings
5. **API Response Logs**: Response data and status codes

### Frontend Logs
1. **Console Logs**: Browser console output
2. **Network Logs**: API call requests/responses
3. **Vue Component Logs**: Component lifecycle events
4. **Error Logs**: JavaScript errors
5. **Performance Logs**: Load times and rendering

---

## API Endpoints to Test

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | List all tasks |
| GET | `/tasks/{id}` | Get task details |
| POST | `/tasks` | Create new task |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| POST | `/tasks/{id}/claim` | Claim task for worker |
| POST | `/tasks/{id}/complete` | Mark task complete |

---

## Log Submission Format

Please provide logs in the following format:

```
### Environment
- Date: YYYY-MM-DD
- Node.js Version: X.X.X
- PHP Version: X.X.X
- OS: [Windows/Linux/macOS]
- Browser: [Chrome/Firefox/Safari]

### Backend Test Executed
[Description of backend tests]

### Backend Logs
[Paste backend logs here]

### Frontend Test Executed
[Description of frontend tests]

### Frontend Logs (Console)
[Paste browser console logs here]

### Network Logs
[Paste relevant network request/response data]

### Screenshots (if applicable)
[Attach or describe any UI screenshots]

### Observations
[Any observations or issues noted]

### Status
- [ ] Backend tests passed
- [ ] Frontend tests passed
- [ ] E2E tests passed
- [ ] Errors encountered (describe)
```

---

## Related Documentation

- [Client README](../../Client/README.md)
- [Backend TaskManager README](../../Client/Backend/TaskManager/README.md)
- [Frontend TaskManager README](../../Client/Frontend/TaskManager/README.md)
- [API Reference](../../Client/Backend/TaskManager/_meta/docs/api/API_REFERENCE.md)
- [Setup Guide](../../Client/_meta/docs/SETUP.md)
- [User Guide](../../Client/_meta/docs/USER_GUIDE.md)
- [Worker Examples](../../Client/_meta/examples/workers/README.md)

---

**Created**: 2025-12-04  
**Assigned To**: Human Tester  
**Status**: 🧪 READY FOR TESTING
