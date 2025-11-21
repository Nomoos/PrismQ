"""YouTube subtitle/caption extraction utility using yt-dlp.

This module provides functionality to download and extract subtitles from YouTube videos,
converting them to plain text for use in IdeaInspiration content.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SubtitleExtractor:
    """Extract subtitles from YouTube videos using yt-dlp."""
    
    def __init__(self):
        """Initialize subtitle extractor."""
        if not self._check_ytdlp():
            raise ValueError("yt-dlp is not installed. Install with: pip install yt-dlp")
    
    def _check_ytdlp(self) -> bool:
        """Check if yt-dlp is installed.
        
        Returns:
            True if yt-dlp is available
        """
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def extract_subtitles(self, video_id: str) -> Optional[str]:
        """Extract subtitles for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Plain text subtitles or None if not available
        """
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Use temporary directory for subtitle files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_template = str(temp_path / f"yt_{video_id}")
            
            # Use yt-dlp to download subtitles only (no video)
            cmd = [
                "yt-dlp",
                "--skip-download",
                "--write-auto-sub",  # Download auto-generated subtitles
                "--sub-lang", "en",  # Prefer English
                "--sub-format", "srt",  # SRT format
                "-o", output_template,
                "--quiet",  # Suppress output
                video_url
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    logger.warning(f"yt-dlp failed for video {video_id}: {result.stderr}")
                    return None
                
                # Find downloaded SRT files
                srt_files = list(temp_path.glob(f"yt_{video_id}*.srt"))
                
                if not srt_files:
                    logger.info(f"No subtitles available for video {video_id}")
                    return None
                
                # Read and parse the first SRT file
                with open(srt_files[0], 'r', encoding='utf-8') as f:
                    srt_content = f.read()
                
                # Convert SRT to plain text
                subtitle_text = self._parse_srt_to_text(srt_content)
                
                logger.info(f"Successfully extracted subtitles for video {video_id} ({len(subtitle_text)} chars)")
                return subtitle_text
                
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout while extracting subtitles for video {video_id}")
                return None
            except Exception as e:
                logger.error(f"Error extracting subtitles for video {video_id}: {e}")
                return None
    
    def _parse_srt_to_text(self, srt_content: str) -> str:
        """Parse SRT subtitle file to plain text.
        
        Args:
            srt_content: Raw SRT file content
            
        Returns:
            Plain text of subtitles
        """
        lines = srt_content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines, numbers, and timestamp lines
            if not line or line.isdigit() or '-->' in line:
                continue
            text_lines.append(line)
        
        return ' '.join(text_lines)
