# Development Documentation

This directory contains developer guides and implementation documentation.

## Documents

### Development Tools
- **[QUERY_PROFILER_GUIDE.md](QUERY_PROFILER_GUIDE.md)** - Query profiling and performance analysis

### Implementation History
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Overall implementation summary
- **[IMPLEMENTATION_SUMMARY_CLAIM_ENHANCEMENT.md](IMPLEMENTATION_SUMMARY_CLAIM_ENHANCEMENT.md)** - Task claiming enhancement details

## For Developers

These documents provide context on how features were implemented and tools available for development and debugging.

### Adding New Endpoints

Since TaskManager uses a data-driven architecture, you can add endpoints via SQL:

```sql
INSERT INTO api_endpoints (method, route, action_type, action_config) 
VALUES ('POST', '/api/my-endpoint', 'query', '{"query": "..."}');
```

See [Architecture Documentation](../architecture/) for more details.

### Profiling Queries

Use the Query Profiler to analyze database performance:
- See [QUERY_PROFILER_GUIDE.md](QUERY_PROFILER_GUIDE.md) for details
- Example code in `../../examples/query_profiler_example.php`
