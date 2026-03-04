# MANUAL-TEST-001: T (Text Generation Pipeline) Manual Testing

**Module**: PrismQ.T  
**Type**: Manual Testing  
**Priority**: High  
**Status**: 🧪 READY FOR TESTING

---

## Overview

Manual testing issue for the T (Text Generation Pipeline) module. The user will run the text generation workflow in a preview environment and provide logs for analysis.

---

## Module Description

The **T (Text Generation Pipeline)** is the foundation of the PrismQ content workflow. It transforms initial ideas into high-quality, published text content optimized for blogs, articles, and social media platforms.

### Key Components

| Component | Path | Description |
|-----------|------|-------------|
| **Idea** | `T/Idea/` | Idea development and structuring |
| **Script** | `T/Script/` | Script drafting and refinement |
| **Title** | `T/Title/` | Title creation and optimization |
| **Review** | `T/Review/` | Multi-dimensional content quality review |
| **Publishing** | `T/Publishing/` | Text content publication with SEO |
| **Database** | `T/Database/` | Data persistence layer |
| **State** | `T/State/` | Workflow state management |
| **Story** | `T/Story/` | Story generation capabilities |

### Workflow Stages

```
IdeaInspiration
    ↓
Idea (Creation → Outline → Skeleton → Title)
    ↓
ScriptDraft
    ↓
ScriptReview (Review modules)
    ↓
ScriptApproved
    ↓
TextPublishing (Publishing modules)
    ↓
PublishedText → Audio Pipeline (A)
```

---

## Testing Checklist

### 1. Idea Module Tests
- [ ] **Idea Creation**: Create a new idea from inspiration
- [ ] **Idea Outline**: Generate outline from idea
- [ ] **Idea Model**: Verify data model structure
- [ ] **Idea Review**: Review and validate idea

### 2. Title Module Tests
- [ ] **Title from Idea**: Generate initial title variants (v1) from idea
- [ ] **Title Review**: Review title against script content
- [ ] **Title Improvement**: Generate improved title (v2+) from review feedback

### 3. Script Module Tests
- [ ] **Script from Idea+Title**: Generate initial script (v1) from idea and title
- [ ] **Script Writer**: AI-powered script generation
- [ ] **Script Improvement**: Generate improved script (v2+) from review feedback

### 4. Review Module Tests
- [ ] **Grammar Review**: Validate grammar and syntax checks
- [ ] **Readability Review**: Validate reading level optimization
- [ ] **Tone Review**: Validate tone and voice consistency
- [ ] **Content Review**: Validate content accuracy checks
- [ ] **Consistency Review**: Validate style consistency checks
- [ ] **Editing Review**: Validate final editing pass

### 5. Publishing Module Tests
- [ ] **SEO Keywords**: Keyword research and targeting
- [ ] **SEO Tags**: Tag optimization
- [ ] **SEO Categories**: Content categorization
- [ ] **Finalization**: Final publication preparation

### 6. State Machine Tests
- [ ] **State Transitions**: Verify workflow state transitions
- [ ] **State Persistence**: Verify state is saved correctly
- [ ] **State Recovery**: Verify recovery from interrupted states

---

## Test Commands

```bash
# Navigate to repository
cd /home/runner/work/PrismQ/PrismQ

# Run T module tests
python -m pytest T/ -v

# Run specific submodule tests
python -m pytest T/Title/From/Idea/_meta/tests/ -v
python -m pytest T/Script/From/Idea/Title/_meta/tests/ -v

# Test integration
python -m pytest tests/test_integration.py -k "text" -v
```

---

## Expected Logs to Capture

When running the preview, please capture:

1. **Startup Logs**: Any initialization messages
2. **Workflow Execution Logs**: Step-by-step execution output
3. **Error Logs**: Any errors or warnings
4. **State Transition Logs**: Workflow state changes
5. **Output Logs**: Generated content output

---

## Log Submission Format

Please provide logs in the following format:

```
### Environment
- Date: YYYY-MM-DD
- Python Version: X.X.X
- OS: [Windows/Linux/macOS]

### Test Executed
[Description of what was tested]

### Logs
[Paste logs here]

### Observations
[Any observations or issues noted]

### Status
- [ ] All tests passed
- [ ] Some tests failed (list which)
- [ ] Errors encountered (describe)
```

---

## Related Documentation

- [T Module README](../../T/README.md)
- [Title & Script Workflow](../../T/TITLE_SCRIPT_WORKFLOW.md)
- [Detailed Workflow](../../T/WORKFLOW_DETAILED.md)
- [State Machine](../../T/WORKFLOW_STATE_MACHINE.md)
- [Visual Guide](../../T/WORKFLOW_VISUAL.md)

---

**Created**: 2025-12-04  
**Assigned To**: Human Tester  
**Status**: 🧪 READY FOR TESTING
