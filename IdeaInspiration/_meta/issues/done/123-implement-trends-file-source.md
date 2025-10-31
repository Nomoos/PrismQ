# Implement TrendsFileSource

**Type**: Feature
**Priority**: Lower
**Status**: New
**Category**: Signals/Trends
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
**Estimated Effort**: 3-5 days
**Part of**: Issue #027 (Source Implementation Master Plan), Issue #021 (Signals Category)

## Description

Implement TrendsFileSource to import trend signals from CSV/JSON files. This source enables manual trend curation and integration of external trend data.

## Goals

- Import trends from CSV files
- Import trends from JSON files
- Validate imported data format
- Calculate universal signal metrics
- Store signals in SQLite with deduplication
- Provide CLI interface for management

## Reference Implementation

- **Template**: `Sources/Signals/Trends/GoogleTrends/`
- **Guide**: `Sources/Signals/IMPLEMENTATION_GUIDE.md`

## Technical Requirements

### Dependencies
- `pandas` - Data manipulation and CSV/JSON handling
- `ConfigLoad` - Configuration management
- `SQLite` - Data persistence
- `pytest`, `pytest-cov` - Testing

### Signal Type
`'trend'` - Manual/imported trends

### Key Features
- CSV file import
- JSON file import
- Data validation
- Format conversion
- Bulk import support
- Error handling for malformed files

### Expected File Format

**CSV:**
```csv
name,description,volume,tags,first_seen
TrendName,Description,1000000,"tag1,tag2",2025-10-30T00:00:00Z
```

**JSON:**
```json
[
  {
    "name": "TrendName",
    "description": "Description",
    "volume": 1000000,
    "tags": ["tag1", "tag2"],
    "first_seen": "2025-10-30T00:00:00Z"
  }
]
```

## Implementation Steps

1. Setup structure from template
2. Implement `trends_file_plugin.py`
3. Add CSV file parsing logic
4. Add JSON file parsing logic
5. Implement data validation
6. Map imported data to signal format
7. Implement metrics calculations
8. Write comprehensive tests (test files)
9. Document file formats and usage

## Success Criteria

- [ ] SOLID principles followed
- [ ] CSV import works correctly
- [ ] JSON import works correctly
- [ ] Data validation robust
- [ ] Universal metrics calculated
- [ ] CLI interface functional
- [ ] Tests >80% coverage
- [ ] Documentation complete
- [ ] Example files provided

## CLI Usage

```bash
# Import from CSV
python -m src.cli scrape --file trends.csv --format csv

# Import from JSON
python -m src.cli scrape --file trends.json --format json

# Validate file before import
python -m src.cli validate --file trends.csv
```

## Related Issues

- #027 - Source Implementation Master Plan
- #021 - Signals Category Implementation

## Notes

LOWER priority - Simplest implementation as it's file-based. Good starter project. Enables manual trend curation and external data integration.
