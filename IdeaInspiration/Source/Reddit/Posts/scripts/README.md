# Reddit Posts Scripts

Utility scripts for Reddit Posts module setup and management.

## Scripts

### register_task_types.py

Registers Reddit task types with the external TaskManager API service.

**Usage:**
```bash
python scripts/register_task_types.py
```

**Prerequisites:**
- TaskManager module installed and accessible
- TaskManager API service running (if using external service)
- Environment variables configured (see config.example.env)

**Task Types Registered:**

1. **PrismQ.Text.Reddit.Post.Fetch**
   - Fetch posts from a specific subreddit
   - Parameters: subreddit, sort, time_filter, limit

2. **PrismQ.Text.Reddit.Post.Search**
   - Search for posts across Reddit
   - Parameters: query, subreddit (optional), sort, time_filter, limit

3. **PrismQ.Text.Reddit.Post.Trending**
   - Fetch trending posts from Reddit
   - Parameters: limit

**Output:**
```
======================================================================
Reddit Posts Task Type Registration
======================================================================

✅ Registered: PrismQ.Text.Reddit.Post.Fetch
✅ Registered: PrismQ.Text.Reddit.Post.Search
✅ Registered: PrismQ.Text.Reddit.Post.Trending

Registration complete: 3/3 task types registered

======================================================================
✅ All task types registered successfully
======================================================================
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
