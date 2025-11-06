# YouTube Channel Download Integration Tests

## Overview

This directory contains comprehensive integration tests for YouTube channel downloading through the PrismQ Backend API. These tests are specifically designed to generate extensive logs for Agent analysis and debugging.

## Test File

- **`test_youtube_channel_download.py`** - Main test suite for YouTube channel downloads

## Test Coverage

### 1. `test_youtube_channel_download_workflow`

**Purpose**: Complete end-to-end test of YouTube channel download workflow with extensive logging.

**What it tests**:
- Backend health check
- Module discovery (finding YouTube Shorts module)
- Module configuration for channel mode
- Module execution launch
- Real-time status monitoring
- Comprehensive log capture and analysis
- Result verification

**Key Features**:
- Tests with a reliable channel (@TED)
- Downloads small number of videos (5) for quick testing
- Generates detailed console output for debugging
- Analyzes log content for key indicators:
  - Channel detection
  - Video processing
  - Metadata extraction
  - Database persistence
  - Error detection

**Expected Output**:
```
================================================================================
YOUTUBE CHANNEL DOWNLOAD TEST - START
================================================================================

[Step 1] Checking Backend health...
✓ Backend status: healthy
✓ Total modules available: 42
✓ Backend version: 1.0.0

[Step 2] Discovering YouTube Shorts module...
✓ Found module: YouTube Shorts Source
  - ID: youtube-shorts
  - Version: 2.0.0
  - Category: Content/Shorts
  ...

[Step 5] Launching YouTube channel download...
✓ Module launched successfully
  - Run ID: abc123...

[Step 6] Monitoring execution status...
  [  0s] Status: queued
  [  2s] Status: running
  [ 45s] Status: completed

[Step 7] Retrieving execution logs...
✓ Retrieved 127 log entries

--------------------------------------------------------------------------------
EXECUTION LOGS (for Agent analysis)
--------------------------------------------------------------------------------
[  1] 2025-11-04T20:30:00 | INFO     | Starting YouTube Shorts scraper...
[  2] 2025-11-04T20:30:01 | INFO     | Mode: channel
[  3] 2025-11-04T20:30:01 | INFO     | Channel: @TED
...
--------------------------------------------------------------------------------

[Step 8] Analyzing log content...
✓ Log statistics:
  - INFO: 120
  - WARNING: 5
  - ERROR: 2

✓ Log indicators:
  ✓ Channel Detected
  ✓ Video Processing
  ✓ Metadata Extracted
  ✓ Database Saved
  ✗ Errors Found

================================================================================
YOUTUBE CHANNEL DOWNLOAD TEST - SUMMARY
================================================================================
✓ Module: YouTube Shorts Source
✓ Run ID: abc123...
✓ Status: completed
✓ Logs captured: 127 entries
✓ Execution time: ~45s
✓ TEST PASSED - Channel download completed successfully
================================================================================
```

### 2. `test_youtube_channel_download_error_handling`

**Purpose**: Verify error handling and logging for invalid inputs.

**What it tests**:
- Invalid channel URL handling
- Missing required parameter handling
- Error log capture
- Graceful failure behavior

**Test Scenarios**:
1. Invalid channel URL: `"this-is-not-a-valid-channel"`
2. Missing `channel_url` parameter in channel mode

### 3. `test_youtube_channel_log_streaming`

**Purpose**: Test real-time log polling/streaming functionality.

**What it tests**:
- Log polling at regular intervals
- Progressive log accumulation
- Log availability during execution

**Note**: Full SSE (Server-Sent Events) streaming test would require additional setup.

### 4. `test_youtube_channel_configuration_persistence`

**Purpose**: Verify configuration save/load/delete functionality.

**What it tests**:
- Saving custom YouTube channel configurations
- Retrieving saved configurations
- Configuration persistence between requests
- Configuration deletion/reset

**Test Configuration**:
```json
{
  "parameters": {
    "mode": "channel",
    "channel_url": "@TestChannel",
    "max_results": 25,
    "category": "Education"
  }
}
```

## Running the Tests

### Prerequisites

1. **Install dependencies**:
   ```bash
   cd /home/runner/work/PrismQ.IdeaInspiration/PrismQ.IdeaInspiration/Client/Backend
   pip install -r requirements.txt
   ```

2. **Ensure YouTube module is available**:
   - The YouTube Shorts module should be configured in `configs/modules.json`
   - The module ID should be `youtube-shorts`

3. **Optional - Install yt-dlp** (for actual downloads):
   ```bash
   pip install yt-dlp
   ```

### Run All YouTube Tests

```bash
cd /home/runner/work/PrismQ.IdeaInspiration/PrismQ.IdeaInspiration/Client/Backend
pytest _meta/tests/integration/test_youtube_channel_download.py -v -s
```

The `-s` flag shows all print statements for detailed log analysis.

### Run Specific Test

```bash
# Main workflow test
pytest _meta/tests/integration/test_youtube_channel_download.py::test_youtube_channel_download_workflow -v -s

# Error handling test
pytest _meta/tests/integration/test_youtube_channel_download.py::test_youtube_channel_download_error_handling -v -s

# Log streaming test
pytest _meta/tests/integration/test_youtube_channel_download.py::test_youtube_channel_log_streaming -v -s

# Config persistence test
pytest _meta/tests/integration/test_youtube_channel_download.py::test_youtube_channel_configuration_persistence -v -s
```

## Test Behavior

### With yt-dlp Installed

If `yt-dlp` is installed, the tests will:
- Actually download YouTube channel metadata
- Process real video information
- Save data to the database
- Generate authentic logs from the scraping process

### Without yt-dlp Installed

If `yt-dlp` is NOT installed, the tests will:
- Still execute the full workflow
- Generate logs showing the error
- Verify error handling works correctly
- Complete with `failed` status (which is expected)

The test assertions are designed to pass in both scenarios, as the primary goal is to verify the Backend API workflow and log generation.

## Log Analysis for Agents

The tests generate comprehensive logs that are useful for:

1. **Debugging Issues**:
   - Detailed step-by-step execution logs
   - Error messages and stack traces
   - Configuration values used

2. **Performance Analysis**:
   - Execution timestamps
   - Time spent in each phase
   - Resource usage patterns

3. **Integration Verification**:
   - API endpoint responses
   - Module discovery process
   - Configuration persistence
   - Run lifecycle management

4. **Learning Patterns**:
   - How YouTube scraping works
   - Error scenarios and handling
   - Module execution flow
   - Log structure and content

## Example Log Output Structure

Each log entry contains:
```json
{
  "timestamp": "2025-11-04T20:30:00.123Z",
  "level": "INFO",
  "message": "Scraping YouTube channel: @TED (max: 5)..."
}
```

Common log levels:
- **INFO**: Normal operational messages
- **WARNING**: Non-critical issues (e.g., some videos skipped)
- **ERROR**: Errors that don't stop execution
- **CRITICAL**: Fatal errors

## Integration with Backend API

These tests use the actual Backend API endpoints:

- `GET /api/health` - Health check
- `GET /api/modules` - List modules
- `GET /api/modules/{id}` - Module details
- `GET /api/modules/{id}/config` - Get configuration
- `POST /api/modules/{id}/config` - Save configuration
- `DELETE /api/modules/{id}/config` - Delete configuration
- `POST /api/modules/{id}/run` - Launch module
- `GET /api/runs` - List runs
- `GET /api/runs/{id}` - Run details
- `GET /api/runs/{id}/logs` - Get logs

## Troubleshooting

### Test Hangs or Times Out

- Check if Backend is running
- Verify module configuration exists
- Increase `max_wait_time` in test if downloads are slow
- Check network connectivity for YouTube access

### Module Not Found

- Verify `configs/modules.json` contains `youtube-shorts` module
- Check module `enabled` is `true`
- Verify `script_path` points to valid location

### No Logs Generated

- Check if module actually executes
- Verify log capture is configured in Backend
- Check run status - may have failed before logging

### Tests Pass but Downloads Don't Work

- Install `yt-dlp`: `pip install yt-dlp`
- Check YouTube API access
- Verify network allows YouTube connections
- Check channel URL is valid

## Future Enhancements

Potential improvements to these tests:

1. **Mock YouTube Responses**: Test without network dependency
2. **SSE Streaming**: Full real-time log streaming test
3. **Performance Benchmarks**: Track execution time metrics
4. **Database Verification**: Check actual data saved
5. **Concurrent Downloads**: Test multiple simultaneous channel downloads
6. **Rate Limiting**: Test handling of YouTube rate limits
7. **Resume Capability**: Test interrupted download recovery

## Contributing

When adding new YouTube-related tests:

1. Follow existing test patterns
2. Include comprehensive logging
3. Document expected behavior
4. Test both success and failure scenarios
5. Update this README with new test descriptions

## Related Documentation

- [Backend API Reference](../../../API_REFERENCE.md)
- [Integration Guide](../../../INTEGRATION_GUIDE.md)
- [Log Streaming Guide](../../../LOG_STREAMING_GUIDE.md)
- [YouTube Module Documentation](../../../../../Sources/Content/Shorts/YouTube/README.md)

## Contact

For issues or questions about these tests:
- Open an issue on GitHub
- Check existing test documentation
- Review Backend logs for debugging
