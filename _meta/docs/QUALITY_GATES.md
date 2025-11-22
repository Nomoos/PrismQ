# Quality Gates Guide

**Document Type**: Quality Assurance Framework  
**Scope**: Project-wide  
**Last Updated**: 2025-11-21

## Purpose

This document defines the quality gates and acceptance criteria used throughout the PrismQ content production pipeline to ensure professional output at each stage.

## Overview

Quality gates are **explicit checkpoints** where content must meet defined criteria before progressing to the next stage. They prevent quality issues from cascading and ensure each format builds on a solid foundation.

## Quality Gate Philosophy

### Key Principles
1. **Prevent, Don't Fix**: Catch issues early before they propagate
2. **Explicit Criteria**: Clear, measurable acceptance standards
3. **Review Before Progress**: No advancement without approval
4. **Iterative Refinement**: Allow backward transitions for improvements
5. **Progressive Standards**: Each stage has higher quality bars

## Quality Gates by Module

### T Module (Text Generation)

#### Gate 1: Idea Approval
**Entry**: Idea Creation  
**Exit**: Approved Idea → Script Draft

**Criteria**:
- ✓ Clear topic definition
- ✓ Target audience identified
- ✓ Content angle unique or valuable
- ✓ Keywords researched (SEO viability)
- ✓ Outline structure defined

**Review**: Self-review or peer review  
**Typical Issues**: Vague topic, oversaturated market, weak angle

---

#### Gate 2: Title Acceptance
**Entry**: Title Draft  
**Exit**: Approved Title → Script Draft

**Criteria**:
- ✓ Clear and specific (not vague)
- ✓ SEO-friendly (includes primary keyword)
- ✓ Compelling (creates curiosity or promise)
- ✓ Appropriate length (50-60 characters for SEO)
- ✓ A/B test variants prepared

**Review**: Editorial review  
**Typical Issues**: Clickbait, too generic, poor SEO, too long

---

#### Gate 3: Script Acceptance
**Entry**: Script Draft → Script Review  
**Exit**: Approved Script → Text Publishing

**Criteria**:
- ✓ Complete content (meets target word count)
- ✓ Logical structure (intro, body, conclusion)
- ✓ Readability score acceptable (Flesch-Kincaid 60+)
- ✓ Grammar and spelling clean (Grammarly score 90+)
- ✓ SEO optimized (keyword density, meta description)
- ✓ Facts verified and sources cited

**Review**: Editorial review + Technical review  
**Typical Issues**: Poor flow, grammar errors, weak conclusion, SEO gaps

---

#### Gate 4: Text Publishing Readiness
**Entry**: Script Approved  
**Exit**: Published Text

**Criteria**:
- ✓ Platform-specific formatting applied
- ✓ Images and media assets prepared
- ✓ Meta tags and descriptions set
- ✓ Social media snippets prepared
- ✓ Publication timing optimized
- ✓ Analytics tracking configured

**Review**: Publishing team review  
**Typical Issues**: Formatting errors, missing images, incorrect metadata

---

### A Module (Audio Generation)

#### Gate 5: Voiceover Quality
**Entry**: Voiceover Recording  
**Exit**: Approved Voiceover → Audio Processing

**Criteria**:
- ✓ Clear pronunciation and diction
- ✓ Consistent pacing and energy
- ✓ Minimal background noise (SNR >40dB)
- ✓ No mouth clicks or pops
- ✓ Emotional tone matches content
- ✓ Re-takes for all errors recorded

**Review**: Audio producer review  
**Typical Issues**: Flat delivery, audio noise, poor pacing, pronunciation errors

---

#### Gate 6: Audio Normalization
**Entry**: Voiceover Approved  
**Exit**: Normalized Audio → Enhancement

**Criteria**:
- ✓ Loudness normalized (-16 LUFS for podcasts)
- ✓ Peak levels controlled (-3dB ceiling)
- ✓ Consistent volume throughout
- ✓ No clipping or distortion
- ✓ Dynamic range appropriate

**Review**: Audio engineer review  
**Typical Issues**: Inconsistent volume, clipping, over-compression

---

#### Gate 7: Audio Publishing Readiness
**Entry**: Audio Enhanced  
**Exit**: Published Audio

**Criteria**:
- ✓ File format correct (MP3 320kbps or AAC)
- ✓ ID3 tags complete (title, artist, album, etc.)
- ✓ Cover art prepared (3000x3000px)
- ✓ Show notes and timestamps created
- ✓ RSS feed configured
- ✓ Platform-specific metadata set

**Review**: Publishing team review  
**Typical Issues**: Incorrect tags, missing artwork, format issues

---

### V Module (Video Generation)

#### Gate 8: Scene Plan Approval
**Entry**: Scene Planning  
**Exit**: Approved Scenes → Keyframe Planning

**Criteria**:
- ✓ Scenes aligned with audio timing
- ✓ Visual style consistent
- ✓ Keyframe moments identified
- ✓ Transition types specified
- ✓ Text overlays planned
- ✓ Visual hierarchy defined

**Review**: Creative director review  
**Typical Issues**: Poor timing, inconsistent style, too complex

---

#### Gate 9: Keyframe Quality
**Entry**: Keyframe Generation  
**Exit**: Approved Keyframes → Video Assembly

**Criteria**:
- ✓ Visual quality high (no pixelation)
- ✓ Brand consistency maintained
- ✓ Text legible at target resolution
- ✓ Color palette consistent
- ✓ Composition balanced
- ✓ Platform specifications met

**Review**: Art director review  
**Typical Issues**: Low quality assets, off-brand colors, poor composition

---

#### Gate 10: Video Finalization
**Entry**: Video Review  
**Exit**: Finalized Video → Publishing

**Criteria**:
- ✓ Audio-visual sync perfect
- ✓ No visual artifacts or glitches
- ✓ Color grading consistent
- ✓ Transitions smooth
- ✓ Text overlays timed correctly
- ✓ End screens and CTAs included
- ✓ Platform requirements met (resolution, codec, etc.)

**Review**: Video producer review + Platform specialist  
**Typical Issues**: Sync issues, compression artifacts, missing CTAs

---

#### Gate 11: Video Publishing Readiness
**Entry**: Video Finalized  
**Exit**: Published Video

**Criteria**:
- ✓ Thumbnail created (1280x720px, compelling)
- ✓ Title optimized for platform SEO
- ✓ Description complete with timestamps
- ✓ Tags and categories set
- ✓ Captions/subtitles uploaded
- ✓ Cards and end screens configured
- ✓ Premiere scheduled (if applicable)

**Review**: Publishing team review  
**Typical Issues**: Poor thumbnail CTR, incomplete metadata, missing captions

---

### P Module (Publishing)

#### Gate 12: Publishing Strategy
**Entry**: Content Ready (from T, A, or V)  
**Exit**: Publishing Plan → Distribution

**Criteria**:
- ✓ Target platforms identified
- ✓ Publishing schedule defined
- ✓ Platform-specific optimizations prepared
- ✓ Cross-promotion plan ready
- ✓ Analytics tracking configured

**Review**: Marketing team review  
**Typical Issues**: Poor timing, wrong platforms, no promotion plan

---

### M Module (Metrics/Analytics)

**Note**: M module monitors **published content metrics only**, not production-stage metrics.

#### Gate 13: Data Quality
**Entry**: Published Content Metrics Collection  
**Exit**: Validated Data → Analytics

**Criteria**:
- ✓ Data completeness (no missing fields)
- ✓ Data accuracy (matches platform dashboards)
- ✓ Tracking working correctly
- ✓ Attribution accurate
- ✓ Privacy compliance (GDPR, etc.)

**Review**: Data analyst review  
**Typical Issues**: Missing data, incorrect attribution, tracking errors

---

## Gate Enforcement

### Review Roles

| Role | Gates Reviewed | Authority |
|------|---------------|-----------|
| Self-Review | Idea, Title Draft | Can approve own work |
| Editor | Script, Text Publishing | Must approve before progression |
| Audio Producer | Voiceover, Audio Publishing | Must approve before progression |
| Audio Engineer | Normalization | Must approve before progression |
| Creative Director | Scene Plan | Must approve before progression |
| Art Director | Keyframes | Must approve before progression |
| Video Producer | Video Finalization, Publishing | Must approve before progression |
| Marketing Team | Publishing Strategy | Must approve before distribution |
| Data Analyst | Data Quality | Must approve before insights |

### Approval Process

1. **Self-Check**: Creator reviews against criteria
2. **Request Review**: Submit to appropriate reviewer
3. **Review**: Reviewer checks all criteria
4. **Feedback**: Issues documented if criteria not met
5. **Revision**: Creator addresses feedback
6. **Re-Review**: Repeat until all criteria met
7. **Approval**: Explicit approval granted
8. **Progression**: Content moves to next stage

### Backward Transitions

If issues are discovered after approval, content can move backward:

```
Script Approved → Script Review (issues found)
Voiceover Approved → Voiceover Recording (quality issues)
Video Finalized → Video Assembly (sync problems)
```

## Quality Metrics

### Success Criteria
- **First-Pass Approval Rate**: >70% (fewer revisions needed)
- **Time at Gate**: <24 hours (quick reviews)
- **Defect Escape Rate**: <5% (issues caught early)
- **Revision Cycles**: <2 per gate on average

### Red Flags
- ⚠️ Multiple revision cycles (3+) at same gate
- ⚠️ Backward transitions after approval
- ⚠️ Quality issues discovered post-publication
- ⚠️ Reviewer confusion about criteria

## Tools and Checklists

### Automated Tools
- **Text**: Grammarly, Hemingway Editor, Yoast SEO
- **Audio**: Loudness meters, spectral analyzers
- **Video**: Quality check tools, platform upload validators

### Manual Checklists
Each gate has a detailed checklist:
- **Idea Approval Checklist**: Topic, audience, angle, keywords
- **Script Acceptance Checklist**: Structure, readability, SEO, facts
- **Audio Quality Checklist**: Clarity, noise, pacing, levels
- **Video Quality Checklist**: Sync, visuals, metadata, platform specs

## Best Practices

### For Creators
1. Self-review against criteria before submitting
2. Use automated tools to catch issues early
3. Address feedback completely before re-submission
4. Learn from feedback to improve future work

### For Reviewers
1. Use checklists to ensure comprehensive review
2. Provide specific, actionable feedback
3. Review within 24 hours of submission
4. Approve only when all criteria met

### For Teams
1. Keep criteria up-to-date with platform changes
2. Track metrics to identify bottlenecks
3. Train creators on quality standards
4. Celebrate high first-pass approval rates

## Related Documentation

- **[WORKFLOW.md](../../WORKFLOW.md)** - State machine and transitions
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Overall system design
- **[PROGRESSIVE_ENRICHMENT.md](./PROGRESSIVE_ENRICHMENT.md)** - Multi-format strategy

---

*Quality gates ensure every piece of content meets professional standards before publication.*
