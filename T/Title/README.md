# T/Title - Title Creation Module

**Namespace**: `PrismQ.T.Title`

Create compelling, SEO-optimized titles through testing, optimization, and refinement.

## Current State Note

This module implements a comprehensive title development workflow with the following structure:
- **Namespace**: All titles in this module use the `PrismQ.T.Title` namespace
- **Submodules**: `FromIdea` (initial drafts) and `FromOriginalTitleAndReviewAndScript` (improvements)
- **Integration**: Works with `PrismQ.T.Review.Title` for review-based optimization
- **Workflow**: Titles are co-improved with scripts through iterative review cycles

## Purpose

Develop attention-grabbing titles that maximize click-through rates while maintaining SEO value.

## Submodules

#### [FromIdea](./FromIdea/)
**Stage 2: Initial title draft from idea** (v1)

Generate initial title variants directly from the idea concept.

**[→ View FromIdea Documentation](./FromIdea/README.md)**
**[→ View FromIdea Metadata](./FromIdea/_meta/)**

#### [FromOriginalTitleAndReviewAndScript](./FromOriginalTitleAndReviewAndScript/)
**Stages 6, 9, 19: All title improvements** (v2, v3, v4, v5...)

Generate improved title versions using review feedback, original title, and script context.

This state handles:
- **Stage 6**: First improvements (v1 → v2) using both reviews
- **Stage 9**: Iterative refinements (v2 → v3+) until accepted
- **Stage 19 Feedback**: Final readability polish

**[→ View FromOriginalTitleAndReviewAndScript Documentation](./FromOriginalTitleAndReviewAndScript/README.md)**
**[→ View FromOriginalTitleAndReviewAndScript Metadata](./FromOriginalTitleAndReviewAndScript/_meta/)**

## Module Metadata

**[→ View Title/_meta/docs/](./_meta/docs/)**
**[→ View Title/_meta/examples/](./_meta/examples/)**
**[→ View Title/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to T](../README.md)** | **[→ T/_meta](../_meta/)**
