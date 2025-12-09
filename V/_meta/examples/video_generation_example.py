"""Video Generation Reference Example

This example demonstrates the three-layer approach to video generation:
1. VISUAL LAYER (Keyframes) - Core images defining look, mood, and style
2. STRUCTURAL LAYER (Scene Descriptions) - Timeline skeleton with transitions
3. TIMING LAYER (Subtitles) - Word-level timing for precise synchronization

Reference: https://youtube.com/shorts/NMMAZGYy_Eg?si=hRULhkvt0nmqKwH4

The principle: Video = Keyframes + Scene Descriptions + Subtitles
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class TransitionType(Enum):
    """Types of transitions between scenes."""

    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    ZOOM = "zoom"
    PAN = "pan"
    SLIDE = "slide"


class CameraMovement(Enum):
    """Types of camera movements within a scene."""

    STATIC = "static"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"


@dataclass
class Keyframe:
    """Represents a single keyframe (visual foundation).

    Keyframes are the core images that define:
    - Visual atmosphere
    - Shot transitions
    - Cinematic pacing
    - Emotional tone

    Attributes:
        id: Unique keyframe identifier
        image_prompt: Text prompt describing the visual
        style: Visual style (e.g., "cinematic", "documentary", "animated")
        mood: Emotional mood (e.g., "mysterious", "uplifting", "tense")
        timestamp: Time in seconds when this keyframe appears
        duration: How long this keyframe is displayed (seconds)
        source: Origin of keyframe (e.g., "ai_generated", "stock", "custom")
    """

    id: str
    image_prompt: str
    style: str
    mood: str
    timestamp: float
    duration: float
    source: str = "ai_generated"

    def __str__(self):
        return (
            f"Keyframe({self.id}, {self.timestamp}s-{self.timestamp + self.duration}s, {self.mood})"
        )


@dataclass
class SceneDescription:
    """Represents a scene with visual and narrative elements.

    Scenes define:
    - When keyframes appear
    - Which visuals pair with narration
    - Camera movements
    - Transitions between shots
    - Emotional arc reinforcement

    Attributes:
        id: Unique scene identifier
        start_time: Scene start timestamp (seconds)
        end_time: Scene end timestamp (seconds)
        keyframe_id: ID of the keyframe to display
        narration: Text narration for this scene
        camera_movement: Type of camera movement
        transition_in: Transition when entering scene
        transition_out: Transition when leaving scene
        visual_notes: Additional visual direction notes
    """

    id: str
    start_time: float
    end_time: float
    keyframe_id: str
    narration: str
    camera_movement: CameraMovement
    transition_in: TransitionType
    transition_out: TransitionType
    visual_notes: str = ""

    @property
    def duration(self) -> float:
        """Calculate scene duration in seconds."""
        return self.end_time - self.start_time

    def __str__(self):
        return f"Scene({self.id}, {self.start_time}s-{self.end_time}s, keyframe={self.keyframe_id})"


@dataclass
class SubtitleSegment:
    """Represents a word-level subtitle segment.

    Subtitles provide the final, most precise timing layer:
    - Exact timestamp alignment
    - Fast cut sync
    - Beat matching
    - Micro transitions
    - Dramatic pauses visualization

    Attributes:
        text: The word or phrase to display
        start_time: When to show (seconds)
        end_time: When to hide (seconds)
        position: Screen position (e.g., "bottom", "center")
        style: Subtitle style (e.g., "default", "bold", "animated")
    """

    text: str
    start_time: float
    end_time: float
    position: str = "bottom"
    style: str = "default"

    @property
    def duration(self) -> float:
        """Calculate subtitle duration in seconds."""
        return self.end_time - self.start_time

    def __str__(self):
        return f"Subtitle('{self.text}', {self.start_time}s-{self.end_time}s)"


@dataclass
class VideoComposition:
    """Complete video composition with all three layers.

    This represents the final video assembly combining:
    1. Visual Layer (Keyframes)
    2. Structural Layer (Scene Descriptions)
    3. Timing Layer (Subtitles)

    Attributes:
        title: Video title
        duration: Total video duration (seconds)
        keyframes: List of keyframes (visual foundation)
        scenes: List of scene descriptions (timeline skeleton)
        subtitles: List of subtitle segments (precise timing)
        metadata: Additional video metadata
    """

    title: str
    duration: float
    keyframes: List[Keyframe]
    scenes: List[SceneDescription]
    subtitles: List[SubtitleSegment]
    metadata: Dict[str, Any]

    def validate(self) -> List[str]:
        """Validate the video composition for consistency.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check that scenes reference valid keyframes
        keyframe_ids = {kf.id for kf in self.keyframes}
        for scene in self.scenes:
            if scene.keyframe_id not in keyframe_ids:
                errors.append(
                    f"Scene {scene.id} references non-existent keyframe {scene.keyframe_id}"
                )

        # Check that scenes don't overlap
        for i, scene in enumerate(self.scenes[:-1]):
            next_scene = self.scenes[i + 1]
            if scene.end_time > next_scene.start_time:
                errors.append(f"Scene {scene.id} overlaps with {next_scene.id}")

        # Check that all content fits within video duration
        if self.scenes and self.scenes[-1].end_time > self.duration:
            errors.append(
                f"Last scene extends beyond video duration ({self.scenes[-1].end_time} > {self.duration})"
            )

        return errors

    def get_scene_at(self, timestamp: float) -> Optional[SceneDescription]:
        """Get the scene playing at a specific timestamp.

        Args:
            timestamp: Time in seconds

        Returns:
            Scene at that timestamp, or None if no scene
        """
        for scene in self.scenes:
            if scene.start_time <= timestamp < scene.end_time:
                return scene
        return None

    def get_subtitles_at(self, timestamp: float) -> List[SubtitleSegment]:
        """Get all subtitles visible at a specific timestamp.

        Args:
            timestamp: Time in seconds

        Returns:
            List of subtitles visible at that timestamp
        """
        return [sub for sub in self.subtitles if sub.start_time <= timestamp < sub.end_time]

    def __str__(self):
        return (
            f"VideoComposition('{self.title}', {self.duration}s, "
            f"{len(self.keyframes)} keyframes, {len(self.scenes)} scenes, "
            f"{len(self.subtitles)} subtitles)"
        )


def create_example_video() -> VideoComposition:
    """Create an example video composition demonstrating the three-layer approach.

    This example creates a 60-second video about "The Future of AI" with:
    - 5 keyframes defining visual moments
    - 5 scenes with narration and camera movements
    - Word-level subtitles for precise timing

    Returns:
        A complete VideoComposition ready for rendering
    """
    # LAYER 1: VISUAL LAYER (Keyframes)
    # Define the core images that establish visual foundation
    keyframes = [
        Keyframe(
            id="kf_001",
            image_prompt="Futuristic cityscape at dawn with holographic displays, cinematic lighting",
            style="cinematic",
            mood="hopeful",
            timestamp=0.0,
            duration=12.0,
            source="ai_generated",
        ),
        Keyframe(
            id="kf_002",
            image_prompt="Close-up of neural network visualization with glowing connections",
            style="technical",
            mood="intriguing",
            timestamp=12.0,
            duration=10.0,
            source="ai_generated",
        ),
        Keyframe(
            id="kf_003",
            image_prompt="Person working with AI interface, warm lighting, collaborative atmosphere",
            style="documentary",
            mood="collaborative",
            timestamp=22.0,
            duration=15.0,
            source="ai_generated",
        ),
        Keyframe(
            id="kf_004",
            image_prompt="Abstract data streams flowing through space, ethereal blue tones",
            style="abstract",
            mood="mysterious",
            timestamp=37.0,
            duration=11.0,
            source="ai_generated",
        ),
        Keyframe(
            id="kf_005",
            image_prompt="Bright future scene with diverse people and AI working together",
            style="cinematic",
            mood="inspiring",
            timestamp=48.0,
            duration=12.0,
            source="ai_generated",
        ),
    ]

    # LAYER 2: STRUCTURAL LAYER (Scene Descriptions)
    # Define how keyframes appear, transitions, and camera movements
    scenes = [
        SceneDescription(
            id="scene_001",
            start_time=0.0,
            end_time=12.0,
            keyframe_id="kf_001",
            narration="Imagine a world where artificial intelligence transforms everything we know.",
            camera_movement=CameraMovement.ZOOM_IN,
            transition_in=TransitionType.FADE,
            transition_out=TransitionType.DISSOLVE,
            visual_notes="Slow zoom into cityscape, establishing the future setting",
        ),
        SceneDescription(
            id="scene_002",
            start_time=12.0,
            end_time=22.0,
            keyframe_id="kf_002",
            narration="At its core, AI is about connections, patterns, and learning.",
            camera_movement=CameraMovement.STATIC,
            transition_in=TransitionType.DISSOLVE,
            transition_out=TransitionType.CUT,
            visual_notes="Hold on neural network, let viewer absorb the complexity",
        ),
        SceneDescription(
            id="scene_003",
            start_time=22.0,
            end_time=37.0,
            keyframe_id="kf_003",
            narration="But the real magic happens when humans and AI collaborate, creating possibilities we never imagined.",
            camera_movement=CameraMovement.PAN_RIGHT,
            transition_in=TransitionType.CUT,
            transition_out=TransitionType.FADE,
            visual_notes="Pan to reveal person interacting with AI, showing partnership",
        ),
        SceneDescription(
            id="scene_004",
            start_time=37.0,
            end_time=48.0,
            keyframe_id="kf_004",
            narration="The flow of information accelerates, opening new frontiers of understanding.",
            camera_movement=CameraMovement.ZOOM_OUT,
            transition_in=TransitionType.FADE,
            transition_out=TransitionType.DISSOLVE,
            visual_notes="Zoom out to show scale of data processing",
        ),
        SceneDescription(
            id="scene_005",
            start_time=48.0,
            end_time=60.0,
            keyframe_id="kf_005",
            narration="Together, we're not just building technology. We're shaping the future of humanity.",
            camera_movement=CameraMovement.STATIC,
            transition_in=TransitionType.DISSOLVE,
            transition_out=TransitionType.FADE,
            visual_notes="Final inspirational message, hold on unified vision",
        ),
    ]

    # LAYER 3: TIMING LAYER (Subtitles)
    # Word-level timing for precise synchronization
    # Note: In production, these would be automatically generated from audio analysis
    subtitles = [
        # Scene 1 subtitles
        SubtitleSegment("Imagine", 0.0, 0.5, "bottom", "default"),
        SubtitleSegment("a world", 0.5, 1.2, "bottom", "default"),
        SubtitleSegment("where artificial", 1.2, 2.0, "bottom", "default"),
        SubtitleSegment("intelligence", 2.0, 2.8, "bottom", "default"),
        SubtitleSegment("transforms", 2.8, 3.6, "bottom", "default"),
        SubtitleSegment("everything", 3.6, 4.4, "bottom", "default"),
        SubtitleSegment("we know.", 4.4, 5.2, "bottom", "default"),
        # Scene 2 subtitles
        SubtitleSegment("At its core,", 12.0, 13.0, "bottom", "default"),
        SubtitleSegment("AI is about", 13.0, 14.0, "bottom", "default"),
        SubtitleSegment("connections,", 14.0, 15.0, "bottom", "default"),
        SubtitleSegment("patterns,", 15.0, 16.0, "bottom", "default"),
        SubtitleSegment("and learning.", 16.0, 17.5, "bottom", "default"),
        # Scene 3 subtitles
        SubtitleSegment("But the real", 22.0, 23.0, "bottom", "default"),
        SubtitleSegment("magic happens", 23.0, 24.2, "bottom", "default"),
        SubtitleSegment("when humans", 24.2, 25.2, "bottom", "default"),
        SubtitleSegment("and AI", 25.2, 26.0, "bottom", "default"),
        SubtitleSegment("collaborate,", 26.0, 27.2, "bottom", "default"),
        SubtitleSegment("creating", 27.2, 28.0, "bottom", "default"),
        SubtitleSegment("possibilities", 28.0, 29.2, "bottom", "default"),
        SubtitleSegment("we never", 29.2, 30.0, "bottom", "default"),
        SubtitleSegment("imagined.", 30.0, 31.2, "bottom", "default"),
        # Scene 4 subtitles
        SubtitleSegment("The flow", 37.0, 37.8, "bottom", "default"),
        SubtitleSegment("of information", 37.8, 39.0, "bottom", "default"),
        SubtitleSegment("accelerates,", 39.0, 40.2, "bottom", "default"),
        SubtitleSegment("opening", 40.2, 41.0, "bottom", "default"),
        SubtitleSegment("new frontiers", 41.0, 42.2, "bottom", "default"),
        SubtitleSegment("of understanding.", 42.2, 43.8, "bottom", "default"),
        # Scene 5 subtitles
        SubtitleSegment("Together,", 48.0, 49.0, "bottom", "default"),
        SubtitleSegment("we're not just", 49.0, 50.2, "bottom", "default"),
        SubtitleSegment("building", 50.2, 51.0, "bottom", "default"),
        SubtitleSegment("technology.", 51.0, 52.2, "bottom", "default"),
        SubtitleSegment("We're shaping", 52.2, 53.4, "bottom", "default"),
        SubtitleSegment("the future", 53.4, 54.4, "bottom", "default"),
        SubtitleSegment("of humanity.", 54.4, 55.8, "bottom", "default"),
    ]

    # Combine all layers into complete composition
    video = VideoComposition(
        title="The Future of AI",
        duration=60.0,
        keyframes=keyframes,
        scenes=scenes,
        subtitles=subtitles,
        metadata={
            "format": "short_form",
            "aspect_ratio": "9:16",  # Vertical for shorts/reels
            "target_platform": "youtube_shorts",
            "genre": "educational",
            "target_audience": "tech_enthusiasts",
            "framerate": 30,
            "resolution": "1080x1920",
        },
    )

    return video


def demonstrate_video_layers():
    """Demonstrate the three-layer approach to video generation."""
    print("=" * 80)
    print("VIDEO GENERATION: THREE-LAYER APPROACH")
    print("=" * 80)
    print("\nPrinciple: Video = Keyframes + Scene Descriptions + Subtitles\n")

    # Create example video
    video = create_example_video()

    print(f"Created: {video}\n")

    # Validate composition
    errors = video.validate()
    if errors:
        print("⚠️  VALIDATION ERRORS:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Video composition is valid\n")

    # Display Layer 1: Keyframes
    print("-" * 80)
    print("LAYER 1: VISUAL LAYER (Keyframes)")
    print("-" * 80)
    print("These are the core images defining look, mood, and style.\n")
    for kf in video.keyframes:
        print(f"  {kf}")
        print(f"    Prompt: {kf.image_prompt}")
        print(f"    Style: {kf.style} | Mood: {kf.mood}")
        print()

    # Display Layer 2: Scene Descriptions
    print("-" * 80)
    print("LAYER 2: STRUCTURAL LAYER (Scene Descriptions)")
    print("-" * 80)
    print("These define timing, transitions, and camera movements.\n")
    for scene in video.scenes:
        print(f"  {scene}")
        print(f'    Narration: "{scene.narration}"')
        print(f"    Camera: {scene.camera_movement.value}")
        print(f"    Transitions: {scene.transition_in.value} → {scene.transition_out.value}")
        print(f"    Notes: {scene.visual_notes}")
        print()

    # Display Layer 3: Subtitles (sample)
    print("-" * 80)
    print("LAYER 3: TIMING LAYER (Subtitles)")
    print("-" * 80)
    print("Word-level timing for precise synchronization.\n")
    print(f"  Total subtitle segments: {len(video.subtitles)}")
    print("  Sample (first 10 segments):\n")
    for sub in video.subtitles[:10]:
        print(f"    {sub}")
    print()

    # Demonstrate querying at specific timestamps
    print("-" * 80)
    print("TIMESTAMP QUERY EXAMPLE")
    print("-" * 80)
    print("What's happening at different moments in the video?\n")

    test_timestamps = [5.0, 15.0, 30.0, 45.0, 55.0]
    for ts in test_timestamps:
        scene = video.get_scene_at(ts)
        subs = video.get_subtitles_at(ts)

        print(f"  At {ts}s:")
        if scene:
            print(f"    Scene: {scene.id} (keyframe: {scene.keyframe_id})")
            print(f"    Camera: {scene.camera_movement.value}")
        if subs:
            subtitle_texts = " | ".join([s.text for s in subs])
            print(f"    Subtitles: {subtitle_texts}")
        print()

    # Print rendering instructions
    print("-" * 80)
    print("RENDERING WORKFLOW")
    print("-" * 80)
    print(
        """
To render this video, follow these steps:

1. Generate/Acquire Keyframes
   - Use AI image generation (DALL-E, Midjourney, Stable Diffusion)
   - Or source from stock libraries
   - Ensure consistent visual style across all keyframes

2. Apply Scene Structure
   - Load keyframes at specified timestamps
   - Apply camera movements (zoom, pan, tilt)
   - Add transitions between scenes

3. Overlay Timing Layer
   - Sync subtitles with word-level precision
   - Add audio narration
   - Adjust timing for natural pacing

4. Final Assembly
   - Export in target format (e.g., 1080x1920 for shorts)
   - Add music/sound effects
   - Color grade for platform optimization
   - Add platform-specific elements (CTAs, end screens)

Tools: FFmpeg, DaVinci Resolve, Premiere Pro, or custom video pipeline
"""
    )

    print("=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


def demonstrate_layering_principle():
    """Explain why layers are applied in this specific order."""
    print("\n" + "=" * 80)
    print("WHY THIS LAYER ORDER?")
    print("=" * 80)
    print(
        """
The three-layer approach follows a specific dependency chain:

1. KEYFRAMES FIRST (Visual Foundation)
   ✓ Independent - can be created without other layers
   ✓ Defines overall visual aesthetic
   ✓ Establishes mood and atmosphere
   ✓ Provides the "canvas" for everything else

2. SCENES SECOND (Structural Skeleton)
   ✓ Depends on keyframes - references which keyframe to show
   ✓ Defines narrative flow and pacing
   ✓ Determines camera movements and transitions
   ✓ Creates the timeline structure

3. SUBTITLES LAST (Precise Timing)
   ✓ Depends on audio finalization - needs exact word timing
   ✓ Most precise layer - down to individual words
   ✓ Reveals micro-beats of performance
   ✓ Applied after video is nearly complete

This order ensures:
- Each layer builds on the previous foundation
- No rework needed when adding layers
- Maximum flexibility in production
- Clean separation of concerns
"""
    )
    print("=" * 80)


def main():
    """Run the complete video generation example."""
    print("\n" + "=" * 80)
    print("PRISMQ VIDEO GENERATION - REFERENCE EXAMPLE")
    print("=" * 80)
    print("\nReference: https://youtube.com/shorts/NMMAZGYy_Eg?si=hRULhkvt0nmqKwH4\n")

    # Demonstrate the three-layer approach
    demonstrate_video_layers()

    # Explain the layering principle
    demonstrate_layering_principle()

    print("\n✅ Example completed! You now understand the three-layer video approach.\n")


if __name__ == "__main__":
    main()
