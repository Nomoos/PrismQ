# HackerNews Stories Scripts

Utility scripts for HackerNews Stories module setup and management.

## Scripts

### register_task_types.py

Registers HackerNews task types with the external TaskManager API service.

**Usage:**
```bash
python scripts/register_task_types.py
```

**Prerequisites:**
- TaskManager module installed and accessible
- TaskManager API service running (if using external service)
- Environment variables configured (see config.example.env)

**Task Types Registered:**

1. **PrismQ.Text.HackerNews.Story.Fetch**
   - Fetch stories by type from HackerNews
   - Parameters: story_type (top/best/new/ask/show/job), limit

2. **PrismQ.Text.HackerNews.Story.FrontPage**
   - Fetch front page stories
   - Parameters: limit (default: 30)

3. **PrismQ.Text.HackerNews.Story.Best**
   - Fetch best stories
   - Parameters: limit (default: 30)

4. **PrismQ.Text.HackerNews.Story.New**
   - Fetch newest stories
   - Parameters: limit (default: 30)

5. **PrismQ.Text.HackerNews.Story.Ask**
   - Fetch Ask HN stories
   - Parameters: limit (default: 30)

6. **PrismQ.Text.HackerNews.Story.Show**
   - Fetch Show HN stories
   - Parameters: limit (default: 30)

7. **PrismQ.Text.HackerNews.Story.Job**
   - Fetch job postings
   - Parameters: limit (default: 30)

**Output:**
```
✅ Registered: PrismQ.Text.HackerNews.Story.Fetch
✅ Registered: PrismQ.Text.HackerNews.Story.FrontPage
✅ Registered: PrismQ.Text.HackerNews.Story.Best
✅ Registered: PrismQ.Text.HackerNews.Story.New
✅ Registered: PrismQ.Text.HackerNews.Story.Ask
✅ Registered: PrismQ.Text.HackerNews.Story.Show
✅ Registered: PrismQ.Text.HackerNews.Story.Job

Registered 7/7 task types
```

**Error Handling:**
- If TaskManager is not available, exits with error message
- If registration fails, shows which task types failed
- Returns exit code 0 on success, 1 on failure

**Note:** This script only needs to be run once during initial setup or when task type definitions change.

## Adding New Scripts

When adding new utility scripts:
1. Follow the existing script structure
2. Add documentation here in README.md
3. Include error handling and user-friendly output
4. Test with and without dependencies available
5. Return appropriate exit codes (0 = success, 1 = error)
