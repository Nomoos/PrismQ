# IMP-006: Platform-Specific Timing Optimization

**Type**: Improvement - Script Generation  
**Worker**: Worker02 (Python Specialist)  
**Priority**: High  
**Effort**: 2 days  
**Module**: `PrismQ.T.Script` (all submodules)  
**Category**: Script Generation  
**Status**: 🎯 PLANNED

---

## Description

Implement platform-specific timing optimization for scripts to ensure content meets exact duration requirements for different platforms (YouTube Shorts <60s, TikTok <60s/<180s, Instagram Reels <90s, YouTube standard, etc.). Add intelligent script length adjustment, pacing optimization, and real-time duration estimation.

Currently, scripts use generic timing guidelines (e.g., "< 180 seconds"). This enhancement adds precise platform-aware optimization with automatic script adjustment to meet platform constraints.

---

## Business Justification

- Platform-optimized content performs 30-50% better
- Reduces manual editing and re-recording
- Increases cross-platform distribution efficiency
- Improves algorithm favorability on each platform
- Enables automated multi-platform content adaptation

---

## Acceptance Criteria

- [ ] Define precise timing requirements for 8+ platforms
- [ ] Implement accurate script duration estimation (words-per-minute calculation)
- [ ] Add platform parameter to script generation
- [ ] Automatic script length adjustment to meet platform constraints
- [ ] Intelligent content compression (preserve key points)
- [ ] Pacing analysis and optimization per platform
- [ ] Real-time timing feedback during generation
- [ ] Support multi-platform script variants generation
- [ ] Add platform metadata to script records
- [ ] Provide timing warnings and optimization suggestions

---

## Platform Timing Specifications

### Short-Form Video
- **YouTube Shorts**: <60 seconds (optimal: 45-55s)
- **TikTok**: <60 seconds (optimal: 21-34s) OR <180 seconds
- **Instagram Reels**: <90 seconds (optimal: 30-60s)
- **Facebook Reels**: <60 seconds (optimal: 30-45s)
- **Snapchat Spotlight**: <60 seconds (optimal: 20-40s)

### Long-Form Video
- **YouTube Standard**: 8-15 minutes (optimal for mid-roll ads)
- **YouTube Extended**: 15+ minutes (allows chapters)
- **LinkedIn Video**: 3-10 minutes (optimal: 3-5 minutes)
- **IGTV**: 1-60 minutes (optimal: 5-10 minutes)

### Audio
- **Podcast Episode**: 20-60 minutes (varies by format)
- **Audio Snippet**: <2 minutes

---

## Input/Output

**Input**:
- Idea/concept
- Title
- Target platform(s)
- Content density preference (concise/detailed)
- Speaking pace preference (slow/medium/fast)

**Output**:
```python
{
    "platform": "youtube_shorts",
    "target_duration": 55,  # seconds
    "estimated_duration": 54.3,
    "word_count": 135,
    "speaking_pace": "medium",  # 150 WPM
    "script": "...",
    "sections": [
        {"type": "hook", "duration": 8, "words": 20},
        {"type": "body", "duration": 38, "words": 95},
        {"type": "conclusion", "duration": 8.3, "words": 20}
    ],
    "timing_analysis": {
        "meets_platform_requirement": True,
        "utilization": 98.7,  # % of available time used
        "buffer": 0.7,  # seconds of buffer
        "pacing_score": 92
    },
    "adjustments_made": [
        "Compressed middle section by 15%",
        "Optimized transitions to save 3 seconds",
        "Removed redundant intro"
    ]
}
```

---

## Dependencies

- **MVP-003**: T.Script.FromIdeaAndTitle (v1 generation)
- **MVP-007**: T.Script.FromOriginalScriptAndReviewAndTitle (improvements)
- Text-to-speech timing estimation library or WPM calculator

---

## Technical Notes

### Implementation Approach

1. **Duration Estimator** (`T/Script/timing/duration_estimator.py`):
```python
class DurationEstimator:
    # Speaking pace standards
    WPM_RATES = {
        "slow": 120,      # Deliberate, educational
        "medium": 150,    # Normal conversation
        "fast": 180,      # Energetic, engaging
        "very_fast": 200  # Rapid-fire, excitement
    }
    
    def estimate_duration(
        self,
        script: str,
        pace: str = "medium",
        include_pauses: bool = True
    ) -> float:
        """Estimate script duration in seconds."""
        
        words = self._count_words(script)
        wpm = self.WPM_RATES[pace]
        
        # Base duration
        base_duration = (words / wpm) * 60
        
        # Add pauses for punctuation
        if include_pauses:
            pauses = self._estimate_pauses(script)
            base_duration += pauses
        
        return base_duration
    
    def _estimate_pauses(self, script: str) -> float:
        """Estimate pause time based on punctuation."""
        # Period: 0.5s, Comma: 0.3s, Question: 0.6s
        periods = script.count('.') * 0.5
        commas = script.count(',') * 0.3
        questions = script.count('?') * 0.6
        return periods + commas + questions
```

2. **Platform Optimizer** (`T/Script/timing/platform_optimizer.py`):
```python
PLATFORM_CONFIGS = {
    "youtube_shorts": {
        "max_duration": 60,
        "optimal_min": 45,
        "optimal_max": 55,
        "preferred_pace": "medium",
        "hook_importance": "critical",  # First 3s crucial
        "cta_required": False
    },
    "tiktok": {
        "max_duration": 60,  # or 180 for longer
        "optimal_min": 21,
        "optimal_max": 34,
        "preferred_pace": "fast",
        "hook_importance": "critical",
        "cta_required": False
    },
    # ... more platforms
}

class PlatformOptimizer:
    def optimize_for_platform(
        self,
        script: str,
        platform: str,
        target_duration: Optional[float] = None
    ) -> OptimizedScript:
        """Optimize script for platform timing."""
        
        config = PLATFORM_CONFIGS[platform]
        
        # Estimate current duration
        current_duration = self.estimator.estimate_duration(
            script,
            pace=config["preferred_pace"]
        )
        
        # Determine target
        if target_duration is None:
            target_duration = (config["optimal_min"] + config["optimal_max"]) / 2
        
        # Adjust if needed
        if current_duration > config["max_duration"]:
            script = self._compress_script(script, target_duration, config)
        elif current_duration < config["optimal_min"]:
            script = self._expand_script(script, target_duration, config)
        
        return OptimizedScript(
            script=script,
            platform=platform,
            duration=self.estimator.estimate_duration(script),
            optimizations_applied=[...]
        )
```

3. **Content Compressor** (`T/Script/timing/content_compressor.py`):
```python
class ContentCompressor:
    def compress_script(
        self,
        script: str,
        target_duration: float,
        current_duration: float,
        preserve_key_points: bool = True
    ) -> str:
        """Intelligently compress script to target duration."""
        
        # Calculate compression ratio needed
        ratio = target_duration / current_duration
        
        # Parse into sections
        sections = self._parse_sections(script)
        
        # Identify compressible content
        compressible = self._identify_compressible(sections)
        
        # Apply compression strategies
        compressed_sections = []
        for section in sections:
            if section in compressible:
                # Remove redundancy
                section = self._remove_redundancy(section)
                
                # Shorten examples
                section = self._shorten_examples(section)
                
                # Tighten transitions
                section = self._optimize_transitions(section)
            
            compressed_sections.append(section)
        
        # Reassemble
        compressed_script = self._reassemble(compressed_sections)
        
        # Verify duration
        new_duration = self.estimator.estimate_duration(compressed_script)
        
        if abs(new_duration - target_duration) > 2:  # 2-second tolerance
            # Recursive compression if needed
            return self.compress_script(compressed_script, target_duration, new_duration)
        
        return compressed_script
```

### Files to Create

**New Files**:
- `T/Script/timing/duration_estimator.py` - Duration calculation
- `T/Script/timing/platform_optimizer.py` - Platform-specific optimization
- `T/Script/timing/content_compressor.py` - Intelligent compression
- `T/Script/timing/content_expander.py` - Intelligent expansion
- `T/Script/config/platforms.py` - Platform timing configurations

**Modified Files**:
- `T/Script/FromIdeaAndTitle/src/script_generator.py` - Add platform parameter
- `T/Script/FromOriginalScriptAndReviewAndTitle/src/script_improver.py` - Add timing awareness

### Database Schema Update

```sql
ALTER TABLE scripts ADD COLUMN platform VARCHAR(50);
ALTER TABLE scripts ADD COLUMN target_duration FLOAT;
ALTER TABLE scripts ADD COLUMN estimated_duration FLOAT;
ALTER TABLE scripts ADD COLUMN speaking_pace VARCHAR(20) DEFAULT 'medium';
```

### Testing Requirements

- [ ] Duration estimation accuracy tests (±5% margin)
- [ ] Platform timing compliance tests (>95% success rate)
- [ ] Compression preserves key points (validated by review)
- [ ] Multi-platform generation tests
- [ ] Performance tests (optimization <2 seconds)
- [ ] Edge cases: very short scripts, very long scripts

---

## Success Metrics

- Duration estimation accuracy within ±5% of actual recording
- Platform timing compliance >95%
- Compression quality score >85% (preserves key content)
- Multi-platform script generation time <5 seconds
- Manual timing adjustments reduce by 60%+
- Platform-specific engagement improves by 25%+

---

## Related Issues

- IMP-007: Hook Effectiveness (hook timing varies by platform)
- IMP-008: Pacing Analysis (pacing affects duration)
- IMP-010: Voice-Over Optimization (speaking pace affects duration)

---

**Created**: 2025-11-24  
**Owner**: Worker02 (Python Specialist)  
**Category**: Script Generation Improvements
