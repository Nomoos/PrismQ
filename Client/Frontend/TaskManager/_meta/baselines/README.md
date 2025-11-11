# Performance Baselines

This directory contains performance baseline data for the Frontend/TaskManager application.

## Files

### performance-baseline.json

The current performance baseline. This file contains:
- Build metrics (sizes, file counts, largest chunks)
- Git information (commit, branch, author)
- Timestamp
- Performance budgets

This file is **tracked in git** to share baselines across the team.

### baseline-history.json

Historical record of baselines. Contains the last 50 baseline captures with:
- Timestamp
- Git commit
- Total, JS, and CSS sizes

This file is **tracked in git** to enable trend analysis.

## Usage

See [PERFORMANCE.md](../docs/PERFORMANCE.md#performance-baseline-analysis) for detailed usage instructions.

### Quick Start

```bash
# Capture baseline
npm run baseline:capture

# Compare against baseline
npm run baseline:compare

# View baseline report
npm run baseline:report
```

## When to Update Baseline

1. After completing major features or releases
2. After performance optimization work
3. At regular intervals (weekly/sprint boundaries)
4. Before starting new development cycles

## Notes

- Baselines should be committed to git
- Compare before committing changes that affect bundle size
- Significant regressions (>10KB total, >5KB JS, >1KB CSS) should be investigated
- Use `npm run build:analyze` to investigate size increases
