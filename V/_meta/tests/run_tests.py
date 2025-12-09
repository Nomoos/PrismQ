"""Simple test runner for video generation example (no pytest required)."""

import os
import sys

# Add parent directories to path for imports
# Note: This pattern is consistent with existing test structure in the PrismQ project
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../examples"))

from video_generation_example import (
    CameraMovement,
    Keyframe,
    SceneDescription,
    SubtitleSegment,
    TransitionType,
    VideoComposition,
    create_example_video,
)


def test_keyframe_creation():
    """Test creating a keyframe."""
    print("Testing keyframe creation...", end=" ")
    kf = Keyframe(
        id="kf_001",
        image_prompt="Test prompt",
        style="cinematic",
        mood="hopeful",
        timestamp=0.0,
        duration=10.0,
    )

    assert kf.id == "kf_001"
    assert kf.image_prompt == "Test prompt"
    assert kf.timestamp == 0.0
    assert kf.duration == 10.0
    print("✓")


def test_scene_creation():
    """Test creating a scene."""
    print("Testing scene creation...", end=" ")
    scene = SceneDescription(
        id="scene_001",
        start_time=0.0,
        end_time=10.0,
        keyframe_id="kf_001",
        narration="Test narration",
        camera_movement=CameraMovement.ZOOM_IN,
        transition_in=TransitionType.FADE,
        transition_out=TransitionType.CUT,
    )

    assert scene.id == "scene_001"
    assert scene.duration == 10.0
    print("✓")


def test_subtitle_creation():
    """Test creating a subtitle."""
    print("Testing subtitle creation...", end=" ")
    sub = SubtitleSegment(text="Hello world", start_time=0.0, end_time=1.5)

    assert sub.text == "Hello world"
    assert sub.duration == 1.5
    print("✓")


def test_video_composition():
    """Test creating a video composition."""
    print("Testing video composition...", end=" ")
    keyframes = [Keyframe("kf_001", "prompt1", "style", "mood", 0.0, 10.0)]
    scenes = [
        SceneDescription(
            "scene_001",
            0.0,
            10.0,
            "kf_001",
            "narration",
            CameraMovement.STATIC,
            TransitionType.FADE,
            TransitionType.FADE,
        )
    ]
    subtitles = [SubtitleSegment("Test", 0.0, 1.0)]

    video = VideoComposition(
        title="Test Video",
        duration=10.0,
        keyframes=keyframes,
        scenes=scenes,
        subtitles=subtitles,
        metadata={"test": "data"},
    )

    assert video.title == "Test Video"
    assert len(video.keyframes) == 1
    assert len(video.scenes) == 1
    assert len(video.subtitles) == 1
    print("✓")


def test_video_validation():
    """Test video validation."""
    print("Testing video validation...", end=" ")
    keyframes = [Keyframe("kf_001", "prompt", "style", "mood", 0.0, 10.0)]
    scenes = [
        SceneDescription(
            "scene_001",
            0.0,
            10.0,
            "kf_001",
            "narration",
            CameraMovement.STATIC,
            TransitionType.FADE,
            TransitionType.FADE,
        )
    ]

    video = VideoComposition(
        title="Test", duration=10.0, keyframes=keyframes, scenes=scenes, subtitles=[], metadata={}
    )

    errors = video.validate()
    assert len(errors) == 0, f"Unexpected validation errors: {errors}"
    print("✓")


def test_missing_keyframe_detection():
    """Test validation catches missing keyframe."""
    print("Testing missing keyframe detection...", end=" ")
    keyframes = [Keyframe("kf_001", "prompt", "style", "mood", 0.0, 10.0)]
    scenes = [
        SceneDescription(
            "scene_001",
            0.0,
            10.0,
            "kf_999",  # Non-existent
            "narration",
            CameraMovement.STATIC,
            TransitionType.FADE,
            TransitionType.FADE,
        )
    ]

    video = VideoComposition(
        title="Test", duration=10.0, keyframes=keyframes, scenes=scenes, subtitles=[], metadata={}
    )

    errors = video.validate()
    assert len(errors) > 0, "Should detect missing keyframe"
    assert any("kf_999" in error for error in errors)
    print("✓")


def test_get_scene_at_timestamp():
    """Test getting scene at timestamp."""
    print("Testing scene query...", end=" ")
    keyframes = [Keyframe("kf_001", "prompt", "style", "mood", 0.0, 20.0)]
    scenes = [
        SceneDescription(
            "scene_001",
            0.0,
            10.0,
            "kf_001",
            "narration1",
            CameraMovement.STATIC,
            TransitionType.FADE,
            TransitionType.FADE,
        ),
        SceneDescription(
            "scene_002",
            10.0,
            20.0,
            "kf_001",
            "narration2",
            CameraMovement.STATIC,
            TransitionType.FADE,
            TransitionType.FADE,
        ),
    ]

    video = VideoComposition(
        title="Test", duration=20.0, keyframes=keyframes, scenes=scenes, subtitles=[], metadata={}
    )

    scene_at_5 = video.get_scene_at(5.0)
    assert scene_at_5 is not None
    assert scene_at_5.id == "scene_001"

    scene_at_15 = video.get_scene_at(15.0)
    assert scene_at_15 is not None
    assert scene_at_15.id == "scene_002"
    print("✓")


def test_create_example_video():
    """Test creating the example video."""
    print("Testing example video creation...", end=" ")
    video = create_example_video()

    assert isinstance(video, VideoComposition)
    assert video.title == "The Future of AI"
    assert video.duration == 60.0
    assert len(video.keyframes) == 5
    assert len(video.scenes) == 5
    assert len(video.subtitles) > 0
    print("✓")


def test_example_video_validation():
    """Test example video validation."""
    print("Testing example video validation...", end=" ")
    video = create_example_video()

    errors = video.validate()
    assert len(errors) == 0, f"Example video has validation errors: {errors}"
    print("✓")


def test_example_video_metadata():
    """Test example video metadata."""
    print("Testing example video metadata...", end=" ")
    video = create_example_video()

    assert "format" in video.metadata
    assert video.metadata["format"] == "short_form"
    assert video.metadata["aspect_ratio"] == "9:16"
    assert video.metadata["target_platform"] == "youtube_shorts"
    print("✓")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running Video Generation Example Tests")
    print("=" * 60)
    print()

    tests = [
        test_keyframe_creation,
        test_scene_creation,
        test_subtitle_creation,
        test_video_composition,
        test_video_validation,
        test_missing_keyframe_detection,
        test_get_scene_at_timestamp,
        test_create_example_video,
        test_example_video_validation,
        test_example_video_metadata,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ - {e}")
            failed += 1
        except Exception as e:
            print(f"✗ - Unexpected error: {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
