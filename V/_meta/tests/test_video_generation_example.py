"""Tests for Video Generation Example."""

import sys
import os
import pytest

# Add parent directories to path for imports
# Note: This pattern is consistent with existing test structure in the PrismQ project
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../examples'))

from video_generation_example import (
    Keyframe,
    SceneDescription,
    SubtitleSegment,
    VideoComposition,
    TransitionType,
    CameraMovement,
    create_example_video
)


class TestKeyframe:
    """Tests for Keyframe class."""
    
    def test_create_keyframe(self):
        """Test creating a keyframe."""
        kf = Keyframe(
            id="kf_001",
            image_prompt="Test prompt",
            style="cinematic",
            mood="hopeful",
            timestamp=0.0,
            duration=10.0
        )
        
        assert kf.id == "kf_001"
        assert kf.image_prompt == "Test prompt"
        assert kf.style == "cinematic"
        assert kf.mood == "hopeful"
        assert kf.timestamp == 0.0
        assert kf.duration == 10.0
        assert kf.source == "ai_generated"  # default
    
    def test_keyframe_string_representation(self):
        """Test keyframe string representation."""
        kf = Keyframe(
            id="kf_test",
            image_prompt="Test",
            style="test",
            mood="test",
            timestamp=5.0,
            duration=10.0
        )
        
        str_repr = str(kf)
        assert "kf_test" in str_repr
        assert "5.0s" in str_repr
        assert "15.0s" in str_repr  # 5.0 + 10.0


class TestSceneDescription:
    """Tests for SceneDescription class."""
    
    def test_create_scene(self):
        """Test creating a scene description."""
        scene = SceneDescription(
            id="scene_001",
            start_time=0.0,
            end_time=10.0,
            keyframe_id="kf_001",
            narration="Test narration",
            camera_movement=CameraMovement.ZOOM_IN,
            transition_in=TransitionType.FADE,
            transition_out=TransitionType.CUT
        )
        
        assert scene.id == "scene_001"
        assert scene.start_time == 0.0
        assert scene.end_time == 10.0
        assert scene.keyframe_id == "kf_001"
        assert scene.narration == "Test narration"
        assert scene.camera_movement == CameraMovement.ZOOM_IN
        assert scene.transition_in == TransitionType.FADE
        assert scene.transition_out == TransitionType.CUT
    
    def test_scene_duration_property(self):
        """Test scene duration calculation."""
        scene = SceneDescription(
            id="scene_test",
            start_time=5.0,
            end_time=15.0,
            keyframe_id="kf_001",
            narration="Test",
            camera_movement=CameraMovement.STATIC,
            transition_in=TransitionType.CUT,
            transition_out=TransitionType.CUT
        )
        
        assert scene.duration == 10.0


class TestSubtitleSegment:
    """Tests for SubtitleSegment class."""
    
    def test_create_subtitle(self):
        """Test creating a subtitle segment."""
        sub = SubtitleSegment(
            text="Hello world",
            start_time=0.0,
            end_time=1.5
        )
        
        assert sub.text == "Hello world"
        assert sub.start_time == 0.0
        assert sub.end_time == 1.5
        assert sub.position == "bottom"  # default
        assert sub.style == "default"  # default
    
    def test_subtitle_duration_property(self):
        """Test subtitle duration calculation."""
        sub = SubtitleSegment(
            text="Test",
            start_time=2.0,
            end_time=4.5
        )
        
        assert sub.duration == 2.5


class TestVideoComposition:
    """Tests for VideoComposition class."""
    
    def test_create_video_composition(self):
        """Test creating a video composition."""
        keyframes = [
            Keyframe("kf_001", "prompt1", "style", "mood", 0.0, 10.0)
        ]
        scenes = [
            SceneDescription(
                "scene_001", 0.0, 10.0, "kf_001", "narration",
                CameraMovement.STATIC, TransitionType.FADE, TransitionType.FADE
            )
        ]
        subtitles = [
            SubtitleSegment("Test", 0.0, 1.0)
        ]
        
        video = VideoComposition(
            title="Test Video",
            duration=10.0,
            keyframes=keyframes,
            scenes=scenes,
            subtitles=subtitles,
            metadata={"test": "data"}
        )
        
        assert video.title == "Test Video"
        assert video.duration == 10.0
        assert len(video.keyframes) == 1
        assert len(video.scenes) == 1
        assert len(video.subtitles) == 1
        assert video.metadata["test"] == "data"
    
    def test_validate_valid_composition(self):
        """Test validation of a valid video composition."""
        keyframes = [
            Keyframe("kf_001", "prompt", "style", "mood", 0.0, 10.0)
        ]
        scenes = [
            SceneDescription(
                "scene_001", 0.0, 10.0, "kf_001", "narration",
                CameraMovement.STATIC, TransitionType.FADE, TransitionType.FADE
            )
        ]
        
        video = VideoComposition(
            title="Test",
            duration=10.0,
            keyframes=keyframes,
            scenes=scenes,
            subtitles=[],
            metadata={}
        )
        
        errors = video.validate()
        assert len(errors) == 0
    
    def test_validate_missing_keyframe(self):
        """Test validation catches missing keyframe reference."""
        keyframes = [
            Keyframe("kf_001", "prompt", "style", "mood", 0.0, 10.0)
        ]
        scenes = [
            SceneDescription(
                "scene_001", 0.0, 10.0, "kf_999",  # Non-existent keyframe
                "narration", CameraMovement.STATIC,
                TransitionType.FADE, TransitionType.FADE
            )
        ]
        
        video = VideoComposition(
            title="Test",
            duration=10.0,
            keyframes=keyframes,
            scenes=scenes,
            subtitles=[],
            metadata={}
        )
        
        errors = video.validate()
        assert len(errors) > 0
        assert any("kf_999" in error for error in errors)
    
    def test_validate_overlapping_scenes(self):
        """Test validation catches overlapping scenes."""
        keyframes = [
            Keyframe("kf_001", "prompt", "style", "mood", 0.0, 20.0)
        ]
        scenes = [
            SceneDescription(
                "scene_001", 0.0, 10.0, "kf_001", "narration1",
                CameraMovement.STATIC, TransitionType.FADE, TransitionType.FADE
            ),
            SceneDescription(
                "scene_002", 8.0, 15.0, "kf_001", "narration2",  # Overlaps at 8.0-10.0
                CameraMovement.STATIC, TransitionType.FADE, TransitionType.FADE
            )
        ]
        
        video = VideoComposition(
            title="Test",
            duration=20.0,
            keyframes=keyframes,
            scenes=scenes,
            subtitles=[],
            metadata={}
        )
        
        errors = video.validate()
        assert len(errors) > 0
        assert any("overlap" in error.lower() for error in errors)
    
    def test_get_scene_at_timestamp(self):
        """Test getting scene at specific timestamp."""
        keyframes = [
            Keyframe("kf_001", "prompt", "style", "mood", 0.0, 20.0)
        ]
        scenes = [
            SceneDescription(
                "scene_001", 0.0, 10.0, "kf_001", "narration1",
                CameraMovement.STATIC, TransitionType.FADE, TransitionType.FADE
            ),
            SceneDescription(
                "scene_002", 10.0, 20.0, "kf_001", "narration2",
                CameraMovement.STATIC, TransitionType.FADE, TransitionType.FADE
            )
        ]
        
        video = VideoComposition(
            title="Test",
            duration=20.0,
            keyframes=keyframes,
            scenes=scenes,
            subtitles=[],
            metadata={}
        )
        
        # Test timestamps
        scene_at_5 = video.get_scene_at(5.0)
        assert scene_at_5 is not None
        assert scene_at_5.id == "scene_001"
        
        scene_at_15 = video.get_scene_at(15.0)
        assert scene_at_15 is not None
        assert scene_at_15.id == "scene_002"
        
        scene_at_25 = video.get_scene_at(25.0)
        assert scene_at_25 is None
    
    def test_get_subtitles_at_timestamp(self):
        """Test getting subtitles at specific timestamp."""
        subtitles = [
            SubtitleSegment("Word1", 0.0, 1.0),
            SubtitleSegment("Word2", 1.0, 2.0),
            SubtitleSegment("Word3", 2.0, 3.0)
        ]
        
        video = VideoComposition(
            title="Test",
            duration=10.0,
            keyframes=[],
            scenes=[],
            subtitles=subtitles,
            metadata={}
        )
        
        # Test at 0.5s (should show Word1)
        subs_at_0_5 = video.get_subtitles_at(0.5)
        assert len(subs_at_0_5) == 1
        assert subs_at_0_5[0].text == "Word1"
        
        # Test at 1.5s (should show Word2)
        subs_at_1_5 = video.get_subtitles_at(1.5)
        assert len(subs_at_1_5) == 1
        assert subs_at_1_5[0].text == "Word2"
        
        # Test at 5.0s (no subtitles)
        subs_at_5 = video.get_subtitles_at(5.0)
        assert len(subs_at_5) == 0


class TestCreateExampleVideo:
    """Tests for the create_example_video function."""
    
    def test_create_example_video_success(self):
        """Test that create_example_video returns a valid composition."""
        video = create_example_video()
        
        assert isinstance(video, VideoComposition)
        assert video.title == "The Future of AI"
        assert video.duration == 60.0
        assert len(video.keyframes) == 5
        assert len(video.scenes) == 5
        assert len(video.subtitles) > 0
    
    def test_example_video_validation(self):
        """Test that the example video passes validation."""
        video = create_example_video()
        
        errors = video.validate()
        assert len(errors) == 0, f"Example video has validation errors: {errors}"
    
    def test_example_video_metadata(self):
        """Test that example video has correct metadata."""
        video = create_example_video()
        
        assert "format" in video.metadata
        assert video.metadata["format"] == "short_form"
        assert video.metadata["aspect_ratio"] == "9:16"
        assert video.metadata["target_platform"] == "youtube_shorts"
    
    def test_example_video_keyframes_cover_duration(self):
        """Test that keyframes cover the entire video duration."""
        video = create_example_video()
        
        # Check first keyframe starts at 0
        assert video.keyframes[0].timestamp == 0.0
        
        # Check last keyframe covers to end
        last_kf = video.keyframes[-1]
        assert last_kf.timestamp + last_kf.duration == video.duration
    
    def test_example_video_scenes_sequential(self):
        """Test that scenes are sequential without gaps."""
        video = create_example_video()
        
        for i in range(len(video.scenes) - 1):
            current_scene = video.scenes[i]
            next_scene = video.scenes[i + 1]
            
            # Next scene should start where current scene ends
            assert current_scene.end_time == next_scene.start_time


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
