# Testing Guide

This guide provides information on testing the YouTube Shorts scraping functionality with example channels and URLs.

## Test URLs

For testing and validation, we provide a set of example URLs from the **SnappyStories_1** channel:

| Type | URL | Purpose |
|------|-----|---------|
| **Channel** | `https://www.youtube.com/@SnappyStories_1` | Base channel URL for scraping |
| **Channel Shorts** | `https://www.youtube.com/@SnappyStories_1/shorts` | Direct link to channel's Shorts section |
| **Example Short #1** | `https://www.youtube.com/shorts/FpSdooOrmsU` | Single short for testing individual video scraping |
| **Example Short #2** | `https://youtube.com/shorts/3o0o5DTwTYU` | Additional test video with query parameters |
| **Channel Handle** | `@SnappyStories_1` | Alternative handle format |

## Quick Start Testing

### 1. Using Test Configuration

The easiest way to test is using the provided test configuration:

```bash
# Copy the test environment template
cp .env.test.example .env.test

# Run a test scrape (5 shorts from SnappyStories_1)
python -m src.cli scrape-channel --env-file .env.test --top 5

# View the results
python -m src.cli list --env-file .env.test

# Check statistics
python -m src.cli stats --env-file .env.test

# Clean up test database
python -m src.cli clear --env-file .env.test
```

### 2. Testing with Explicit Channel URL

You can also specify the channel directly without a config file:

```bash
# Test with full URL
python -m src.cli scrape-channel --channel "https://www.youtube.com/@SnappyStories_1" --top 5

# Test with handle format
python -m src.cli scrape-channel --channel "@SnappyStories_1" --top 5

# Test with plain name
python -m src.cli scrape-channel --channel "SnappyStories_1" --top 5
```

All three formats should work identically.

### 3. Testing Different Scraping Modes

Test various scraping modes with the example channel:

```bash
# Channel-based scraping (recommended)
python -m src.cli scrape-channel --channel "@SnappyStories_1" --top 5

# Trending scraping (doesn't target specific channel)
python -m src.cli scrape-trending --top 10

# Keyword search
python -m src.cli scrape-keyword --keyword "stories" --top 10
```

## Running Integration Tests

We provide integration tests that validate the scraping functionality:

```bash
# Run all tests
pytest _meta/tests/test_integration_snappystories.py -v

# Run only unit tests (no network required)
pytest _meta/tests/test_integration_snappystories.py -v -m "not skip"

# Run specific test
pytest _meta/tests/test_integration_snappystories.py::TestSnappyStoriesIntegration::test_channel_url_normalization -v
```

### Network-Dependent Tests

Some tests require network access and are skipped by default. To run them manually:

```bash
# Run all tests including network-dependent ones
pytest _meta/tests/test_integration_snappystories.py -v -k "scrape_snappy_stories"
```

⚠️ **Note**: Network-dependent tests require:
- Active internet connection
- yt-dlp installed
- Access to YouTube

## Validation Checklist

When testing with the SnappyStories_1 channel, verify:

- [ ] Channel URL normalization works with all formats (@handle, full URL, plain name)
- [ ] Videos are filtered to ≤180 seconds (Shorts duration limit)
- [ ] Videos are vertical format (height > width)
- [ ] Metadata extraction includes:
  - Title and description
  - View count, like count, comment count
  - Upload date
  - Video duration
  - Channel information
- [ ] Tags are properly extracted and formatted
- [ ] Engagement metrics are calculated correctly
- [ ] Subtitles are extracted (if available)
- [ ] Database deduplication works (same video isn't added twice)

## Expected Output

When scraping from SnappyStories_1, you should see output like:

```
Scraping from YouTube channel: https://www.youtube.com/@SnappyStories_1
Number of shorts to scrape: 5

Found 5 shorts from channel
  [1/5] Extracting metadata for: FpSdooOrmsU
  [2/5] Extracting metadata for: ...
  ...

Scraping complete!
Total shorts found: 5
Total shorts saved: 5
Database: ./test_db.s3db
```

## Troubleshooting

### No Shorts Found

If scraping returns 0 shorts:

1. Verify the channel has Shorts published
2. Check your internet connection
3. Ensure yt-dlp is up to date: `pip install --upgrade yt-dlp`
4. Try accessing the channel URL in a browser to confirm it's accessible

### yt-dlp Errors

If you get yt-dlp errors:

```bash
# Update yt-dlp
pip install --upgrade yt-dlp

# Verify installation
yt-dlp --version
```

### Timeout Issues

For slow connections, videos may timeout during metadata extraction. The plugin has a 60-second timeout per video. If you experience frequent timeouts:

1. Reduce the number of shorts to scrape (--top parameter)
2. Check your internet connection speed
3. Try again during off-peak hours

## Automated Testing

The test suite includes automated validation for the SnappyStories_1 channel:

```bash
# Run full test suite
pytest _meta/tests/ -v

# Run only integration tests
pytest _meta/tests/test_integration_snappystories.py -v

# Run with coverage
pytest _meta/tests/test_integration_snappystories.py --cov=src --cov-report=html
```

## Test Data Cleanup

After testing, clean up test data:

```bash
# Clear test database
python -m src.cli clear --env-file .env.test

# Or manually delete the test database file
rm test_db.s3db
```

## Advanced Testing

### Testing Individual Short

To test metadata extraction for the specific example shorts:

```python
from src.plugins.youtube_channel_plugin import YouTubeChannelPlugin
from src.core.config import Config

config = Config('.env.test')
plugin = YouTubeChannelPlugin(config)

# Extract metadata for specific video (Example #1)
video_id = "FpSdooOrmsU"  # From https://www.youtube.com/shorts/FpSdooOrmsU
metadata = plugin._extract_video_metadata(video_id)

if metadata:
    print(f"Title: {metadata['title']}")
    print(f"Duration: {metadata['duration']}s")
    print(f"Views: {metadata['view_count']}")

# Extract metadata for another test video (Example #2)
video_id_2 = "3o0o5DTwTYU"  # From https://youtube.com/shorts/3o0o5DTwTYU
metadata_2 = plugin._extract_video_metadata(video_id_2)

if metadata_2:
    print(f"Title: {metadata_2['title']}")
    print(f"Duration: {metadata_2['duration']}s")
    print(f"Views: {metadata_2['view_count']}")
```

### Testing with Custom Parameters

```bash
# Test with large number of shorts
python -m src.cli scrape-channel --channel "@SnappyStories_1" --top 50

# Test with different database
DATABASE_URL=sqlite:///custom_test.db python -m src.cli scrape-channel --channel "@SnappyStories_1" --top 5

# Test processing to IdeaInspiration format
python -m src.cli scrape-channel --env-file .env.test --top 5
python -m src.cli process --env-file .env.test
```

## Continuous Integration

For CI/CD pipelines, use the non-interactive mode:

```bash
# Run without prompts
python -m src.cli scrape-channel \
  --channel "@SnappyStories_1" \
  --top 5 \
  --no-interactive \
  --env-file .env.test
```

## Support

If you encounter issues while testing:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review the [SCRAPING_BEST_PRACTICES.md](SCRAPING_BEST_PRACTICES.md) guide
3. Consult the [README.md](../../README.md) for general usage
4. Report issues in the GitHub issue tracker

---

**Last Updated**: 2025-10-31  
**Test Channel**: SnappyStories_1 (https://www.youtube.com/@SnappyStories_1)
