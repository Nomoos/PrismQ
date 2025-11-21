# Video Generation Examples

This directory contains reference examples demonstrating the PrismQ video generation workflow.

## Examples

### [video_generation_example.py](./video_generation_example.py)

A comprehensive example demonstrating the **three-layer approach** to video generation:

**Reference**: [YouTube Short](https://youtube.com/shorts/NMMAZGYy_Eg?si=hRULhkvt0nmqKwH4)

**Core Principle**: `Video = Keyframes + Scene Descriptions + Subtitles`

#### The Three Layers

1. **VISUAL LAYER (Keyframes)**
   - Core images defining look, mood, and style
   - Establishes visual atmosphere
   - Provides shot transitions and cinematic pacing
   - Sets emotional tone

2. **STRUCTURAL LAYER (Scene Descriptions)**
   - Timeline skeleton with precise timing
   - Defines when keyframes appear
   - Specifies camera movements (zoom, pan, tilt)
   - Controls transitions between shots
   - Links visuals with narration

3. **TIMING LAYER (Subtitles)**
   - Word-level timing for precise synchronization
   - Exact timestamp alignment
   - Beat matching and micro transitions
   - Dramatic pause visualization

#### Running the Example

```bash
# From the repository root:
python3 V/_meta/examples/video_generation_example.py

# Or from the examples directory:
cd V/_meta/examples
python3 video_generation_example.py
```

#### Example Output

The example creates a 60-second video titled "The Future of AI" with:
- 5 keyframes defining visual moments
- 5 scenes with narration and camera movements
- 34 word-level subtitle segments
- Full metadata for rendering

#### What You'll Learn

- How to structure a video composition with three distinct layers
- The dependency chain: Keyframes → Scenes → Subtitles
- How to validate video composition for consistency
- How to query video state at any timestamp
- The complete rendering workflow

#### Use Cases

This example demonstrates the workflow for:
- **Short-form video** (YouTube Shorts, TikTok, Instagram Reels)
- **Educational content** with clear narration
- **AI-driven video generation** with structured data
- **Multi-platform optimization** (9:16 vertical format)

#### Key Classes

- `Keyframe`: Represents a single visual frame with timing and mood
- `SceneDescription`: Links keyframes with narration and camera work
- `SubtitleSegment`: Word-level subtitle with precise timing
- `VideoComposition`: Complete video with all three layers

#### Production Integration

In a production environment, you would:

1. Generate keyframes using AI image generation (DALL-E, Midjourney, Stable Diffusion)
2. Extract narration timing from audio analysis
3. Auto-generate word-level subtitles from speech-to-text
4. Render using FFmpeg, DaVinci Resolve, or custom pipeline
5. Optimize for target platform (aspect ratio, resolution, bitrate)

#### Extension Points

The example can be extended to:
- Add music and sound effects layers
- Include B-roll footage alongside keyframes
- Support multiple subtitle tracks (languages)
- Add motion graphics and effects
- Implement A/B testing variations

---

## Contributing Examples

When adding new examples to this directory:

1. **Follow the existing structure** - Use dataclasses and clear type hints
2. **Include comprehensive docstrings** - Explain the purpose and usage
3. **Make it runnable** - Examples should execute without external dependencies
4. **Add validation** - Include checks for data consistency
5. **Document well** - Update this README with new example details

## Related Documentation

- [V Module README](../../README.md) - Video pipeline overview
- [Video README](../../Video/README.md) - Video assembly details
- [Scene README](../../Scene/README.md) - Scene planning workflow
- [Keyframe README](../../Keyframe/README.md) - Keyframe generation

---

*Part of the PrismQ Video Generation Pipeline*
