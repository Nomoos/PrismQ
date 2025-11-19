"""HackerNews story fetching worker."""

import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
_src_path = Path(__file__).resolve().parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from workers.base_worker import BaseWorker
from workers import Task, TaskResult
from client import HackerNewsClient

logger = logging.getLogger(__name__)


class HackerNewsStoryWorker(BaseWorker):
    """Worker for fetching HackerNews stories.
    
    Follows SRP: Only handles HackerNews story fetching.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize HackerNews story worker.
        
        Args:
            *args: Positional arguments passed to BaseWorker
            **kwargs: Keyword arguments passed to BaseWorker
        """
        super().__init__(*args, **kwargs)
        
        # Initialize HackerNews API client
        self.hn_client = HackerNewsClient(
            timeout=10,
            rate_limit_delay=0.1
        )
        
        logger.info(f"HackerNewsStoryWorker initialized with worker_id: {self.worker_id}")
    
    def process_task(self, task: Task) -> TaskResult:
        """Process HackerNews story fetching task.
        
        Args:
            task: Task with parameters:
                - story_type: "top", "best", "new", "ask", "show", "job"
                - limit: Number of stories to fetch (default: 30)
                
        Returns:
            TaskResult with fetched stories
        """
        try:
            story_type = task.parameters.get("story_type", "top")
            limit = task.parameters.get("limit", 30)
            
            logger.info(
                f"Fetching {limit} {story_type} stories from HackerNews"
            )
            
            # Fetch story IDs
            story_ids = self._fetch_story_ids(story_type, limit)
            
            # Fetch story details
            stories = []
            for story_id in story_ids[:limit]:
                story = self.hn_client.get_item(story_id)
                if story:
                    stories.append(story)
            
            # Store in database
            self._store_stories(stories, story_type)
            
            logger.info(f"Successfully fetched {len(stories)} stories")
            
            return TaskResult(
                success=True,
                items_processed=len(stories),
                data={"stories": stories, "story_type": story_type}
            )
            
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            return TaskResult(
                success=False,
                error=str(e)
            )
    
    def _fetch_story_ids(self, story_type: str, limit: int) -> list:
        """Fetch story IDs from HackerNews API.
        
        Args:
            story_type: Type of stories to fetch
            limit: Number of IDs to fetch
            
        Returns:
            List of story IDs
        """
        story_type_methods = {
            "top": self.hn_client.get_top_stories,
            "best": self.hn_client.get_best_stories,
            "new": self.hn_client.get_new_stories,
            "ask": self.hn_client.get_ask_stories,
            "show": self.hn_client.get_show_stories,
            "job": self.hn_client.get_job_stories
        }
        
        method = story_type_methods.get(story_type, self.hn_client.get_top_stories)
        return method(limit)
    
    def _store_stories(self, stories: list, story_type: str):
        """Store stories in database.
        
        Args:
            stories: List of story data
            story_type: Type of stories (for categorization)
        """
        # Use IdeaProcessor to store stories
        from core.idea_processor import IdeaProcessor, ContentType
        
        try:
            processor = IdeaProcessor(self.results_db)
            
            for story in stories:
                # Extract relevant fields
                title = story.get('title', '')
                url = story.get('url', f"https://news.ycombinator.com/item?id={story.get('id')}")
                text = story.get('text', '')
                by = story.get('by', '')
                score = story.get('score', 0)
                time_posted = story.get('time', 0)
                
                # Create content text combining title and text
                content = title
                if text:
                    content += f"\n\n{text}"
                
                # Store in database
                processor.process_idea(
                    title=title,
                    content=content,
                    url=url,
                    source_platform="HackerNews",
                    source_type=story_type,
                    author=by,
                    content_type=ContentType.TEXT,
                    metadata={
                        'score': score,
                        'time': time_posted,
                        'story_id': story.get('id'),
                        'descendants': story.get('descendants', 0),
                        'story_type': story_type
                    }
                )
            
            logger.info(f"Stored {len(stories)} stories in database")
            
        except Exception as e:
            logger.error(f"Failed to store stories: {e}")
            # Don't raise - we still fetched the stories successfully
    
    def stop(self):
        """Stop the worker gracefully and close resources."""
        super().stop()
        self.hn_client.close()
        logger.info(f"HackerNewsStoryWorker {self.worker_id} closed")


__all__ = ["HackerNewsStoryWorker"]
