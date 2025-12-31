# PrismQ.T.Script.From.Title.Review.Script

Module for generating improved script versions based on review feedback.

## Overview

This module takes:
- Original script (any version)
- Title (corresponding version)
- Script review feedback
- Title review feedback

And generates:
- Improved script (next version) that addresses review feedback
- Maintains narrative quality while improving alignment

## Workflow Position

```
Script vN + Title vN + Reviews → Script v(N+1) (improved)

Examples:
- MVP-007: Script v1 + Title v1 + Reviews → Script v2
- MVP-010: Script v2 + Title v2 + Reviews → Script v3
- Iteration: Script v3 + Title v3 + Reviews → Script v4, v5, v6, v7, etc.
```

## Usage

### Interactive Mode
```bash
python script_from_review_interactive.py
```

### Preview Mode (no database save)
```bash
python script_from_review_interactive.py --preview --debug
```

### Using Batch Files (Windows)
```batch
PrismQ.T.Script.From.Title.Review.Script.bat
PrismQ.T.Script.From.Title.Review.Script.Preview.bat
```
