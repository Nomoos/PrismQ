# T-Module Manual Tests Index

**Parent Issue**: [MANUAL-TEST-001-T-Module.md](../MANUAL-TEST-001-T-Module.md)  
**Module**: PrismQ.T  
**Type**: Manual Testing Subissues  

---

## Overview

This directory contains individual manual testing subissues for each stage of the T (Text Generation Pipeline) module.

## Subissues

### Core Pipeline (Stages 1-4)
| # | Issue | Module | Status |
|---|-------|--------|--------|
| 01 | [T-TEST-01-Idea-Creation.md](T-TEST-01-Idea-Creation.md) | PrismQ.T.Idea.From.User | 🧪 Ready |
| 02 | [T-TEST-02-Story-From-Idea.md](T-TEST-02-Story-From-Idea.md) | PrismQ.T.Story.From.Idea | 🧪 Ready |
| 03 | [T-TEST-03-Title-From-Idea.md](T-TEST-03-Title-From-Idea.md) | PrismQ.T.Title.From.Idea | 🧪 Ready |
| 04 | [T-TEST-04-Script-From-Title-Idea.md](T-TEST-04-Script-From-Title-Idea.md) | PrismQ.T.Script.From.Title.Idea | 🧪 Ready |

### Review Stages (Stages 5-10)
| # | Issue | Module | Status |
|---|-------|--------|--------|
| 05 | [T-TEST-05-Review-Title-By-Script-Idea.md](T-TEST-05-Review-Title-By-Script-Idea.md) | PrismQ.T.Review.Title.By.Script.Idea | 🧪 Ready |
| 06 | [T-TEST-06-Review-Script-By-Title-Idea.md](T-TEST-06-Review-Script-By-Title-Idea.md) | PrismQ.T.Review.Script.By.Title.Idea | 🧪 Ready |
| 07 | [T-TEST-07-Review-Title-By-Script.md](T-TEST-07-Review-Title-By-Script.md) | PrismQ.T.Review.Title.By.Script | 🧪 Ready |
| 08 | [T-TEST-08-Title-From-Script-Review-Title.md](T-TEST-08-Title-From-Script-Review-Title.md) | PrismQ.T.Title.From.Script.Review.Title | 🧪 Ready |
| 09 | [T-TEST-09-Script-From-Title-Review-Script.md](T-TEST-09-Script-From-Title-Review-Script.md) | PrismQ.T.Script.From.Title.Review.Script | 🧪 Ready |
| 10 | [T-TEST-10-Review-Script-By-Title.md](T-TEST-10-Review-Script-By-Title.md) | PrismQ.T.Review.Script.By.Title | 🧪 Ready |

### Quality Reviews (Stages 11-17)
| # | Issue | Module | Status |
|---|-------|--------|--------|
| 11 | [T-TEST-11-Review-Script-Grammar.md](T-TEST-11-Review-Script-Grammar.md) | PrismQ.T.Review.Script.Grammar | 🧪 Ready |
| 12 | [T-TEST-12-Review-Script-Tone.md](T-TEST-12-Review-Script-Tone.md) | PrismQ.T.Review.Script.Tone | 🧪 Ready |
| 13 | [T-TEST-13-Review-Script-Content.md](T-TEST-13-Review-Script-Content.md) | PrismQ.T.Review.Script.Content | 🧪 Ready |
| 14 | [T-TEST-14-Review-Script-Consistency.md](T-TEST-14-Review-Script-Consistency.md) | PrismQ.T.Review.Script.Consistency | 🧪 Ready |
| 15 | [T-TEST-15-Review-Script-Editing.md](T-TEST-15-Review-Script-Editing.md) | PrismQ.T.Review.Script.Editing | 🧪 Ready |
| 16 | [T-TEST-16-Review-Title-Readability.md](T-TEST-16-Review-Title-Readability.md) | PrismQ.T.Review.Title.Readability | 🧪 Ready |
| 17 | [T-TEST-17-Review-Script-Readability.md](T-TEST-17-Review-Script-Readability.md) | PrismQ.T.Review.Script.Readability | 🧪 Ready |

### Expert Review & Publishing (Stages 18-20)
| # | Issue | Module | Status |
|---|-------|--------|--------|
| 18 | [T-TEST-18-Story-Review.md](T-TEST-18-Story-Review.md) | PrismQ.T.Story.Review | 🧪 Ready |
| 19 | [T-TEST-19-Story-Polish.md](T-TEST-19-Story-Polish.md) | PrismQ.T.Story.Polish | 🧪 Ready |
| 20 | [T-TEST-20-Publishing.md](T-TEST-20-Publishing.md) | PrismQ.T.Publishing | 🧪 Ready |

---

## Preview Mode Behavior

In **Preview Mode**, all scripts behave the same as **Run Mode** except:

1. **No Database Write**: Instead of writing to the database, the new state is displayed
2. **Wait for Keystroke**: After displaying the new state, the script waits for user to press any key
3. **Extensive Logging**: Debug logging is enabled for troubleshooting

---

**Created**: 2025-12-04
