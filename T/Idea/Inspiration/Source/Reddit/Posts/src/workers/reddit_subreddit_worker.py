"""Reddit Subreddit Worker for scraping subreddit posts using TaskManager API.

This worker uses pure TaskManager API pattern - no local queue.
Tasks are claimed from external TaskManager API, processed, and results
are saved to IdeaInspiration database.

Following SOLID principles:
- Single Responsibility: Only handles Reddit subreddit scraping
- Dependency Inversion: Depends on abstractions (BaseWorker, Config)
- Liskov Substitution: Can substitute BaseWorker in any context
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Add parent directory to path for imports
_src_path = Path(__file__).resolve().parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from workers.base_worker import BaseWorker
from core.config import Config
from plugins.reddit_subreddit import RedditSubredditPlugin

# Import IdeaInspiration model
model_path = Path(__file__).resolve().parents[6] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration import IdeaInspiration
from idea_inspiration_db import IdeaInspirationDatabase


logger = logging.getLogger(__name__)


class RedditSubredditWorker(BaseWorker):
    """Worker for scraping Reddit subreddit posts using TaskManager API.
    
    This worker:
    1. Registers task types with TaskManager API on startup
    2. Claims tasks from TaskManager API
    3. Scrapes Reddit subreddit posts
    4. Saves results to IdeaInspiration database
    5. Reports completion to TaskManager API
    
    Task Parameters (from TaskManager API):
        subreddit: Subreddit name (required, default: 'all')
        limit: Number of posts to scrape (default: 10)
        sort: Sort method - 'hot', 'new', 'top', 'rising' (default: 'hot')
        time_filter: Time filter for 'top' sort (optional)
    
    Task Types:
        - PrismQ.Text.Reddit.Post.Subreddit: Scrape posts from a subreddit
    
    Example Task (from TaskManager API):
        {
            "id": 123,
            "type": "PrismQ.Text.Reddit.Post.Subreddit",
            "params": {
                "subreddit": "python",
                "limit": 50,
                "sort": "hot"
            }
        }
    """
    
    def __init__(
        self,
        worker_id: str,
        config: Config,
        idea_db_path: Optional[str] = None,
        **kwargs
    ):
        """Initialize Reddit Subreddit Worker with TaskManager API.
        
        Args:
            worker_id: Unique worker identifier
            config: Configuration object
            idea_db_path: Path to IdeaInspiration database (optional)
            **kwargs: Additional arguments passed to BaseWorker
        """
        super().__init__(
            worker_id=worker_id,
            config=config,
            **kwargs
        )
        
        # Initialize Reddit plugin
        try:
            self.reddit_plugin = RedditSubredditPlugin(config)
        except ValueError as e:
            logger.error(f"Failed to initialize Reddit plugin: {e}")
            raise ValueError(f"Reddit API credentials not configured: {e}")
        
        # Initialize IdeaInspiration database
        self.idea_db_path = idea_db_path or getattr(config, 'database_path', 'ideas.db')
        self.idea_db = IdeaInspirationDatabase(self.idea_db_path, interactive=False)
        
        logger.info(
            f"RedditSubredditWorker {worker_id} initialized "
            f"(TaskManager API, idea_db: {self.idea_db_path})"
        )
    
    def register_task_types(self) -> None:
        """Register Reddit task types with TaskManager API."""
        logger.info("Registering Reddit task types with TaskManager API...")
        
        # Define task type for subreddit scraping
        task_type_def = {
            "name": "PrismQ.Text.Reddit.Post.Subreddit",
            "version": "1.0.0",
            "param_schema": {
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Subreddit name (e.g., 'python', 'machinelearning')",
                        "default": "all"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10,
                        "description": "Number of posts to scrape"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["hot", "new", "top", "rising"],
                        "default": "hot",
                        "description": "Sort method for posts"
                    },
                    "time_filter": {
                        "type": "string",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "description": "Time filter (for 'top' sort only)"
                    }
                },
                "required": []
            }
        }
        
        try:
            # Register with TaskManager API (idempotent)
            result = self.taskmanager_client.register_task_type(
                name=task_type_def["name"],
                version=task_type_def["version"],
                param_schema=task_type_def["param_schema"]
            )
            
            task_type_id = result['id']
            self.task_type_ids.append(task_type_id)
            
            status = "created" if result.get('created') else "exists"
            logger.info(
                f"Task type '{task_type_def['name']}' {status} "
                f"(ID: {task_type_id})"
            )
            
        except Exception as e:
            logger.error(
                f"Failed to register task type '{task_type_def['name']}': {e}"
            )
            raise
    
    def process_task(self, task: Dict) -> Dict:
        """Process a Reddit subreddit scraping task from TaskManager API.
        
        Args:
            task: Task dictionary from TaskManager API with:
                - id: Task ID
                - type: Task type name
                - params: Task parameters
            
        Returns:
            Result dictionary with:
                - success: bool
                - idea_inspiration_id: ID of first saved idea (if successful)
                - processed_at: timestamp
                - items_processed: number of ideas saved
                - error: error message (if failed)
        """
        try:
            task_id = task['id']
            task_type = task.get('type', '')
            params = task.get('params', {})
            
            logger.info(f"Processing Reddit task {task_id} (type: {task_type})")
            logger.debug(f"Task parameters: {params}")
            
            # Extract parameters with defaults
            subreddit = params.get('subreddit', 'all')
            limit = params.get('limit', 10)
            sort = params.get('sort', 'hot')
            time_filter = params.get('time_filter')
            
            # Scrape posts using plugin
            ideas = self.reddit_plugin.scrape(
                subreddit=subreddit,
                limit=limit,
                sort=sort,
                time_filter=time_filter
            )
            
            if not ideas:
                logger.warning(f"No posts found for r/{subreddit} with sort={sort}")
                return {
                    'success': True,
                    'processed_at': datetime.now(timezone.utc).isoformat(),
                    'items_processed': 0,
                    'message': 'No posts found'
                }
            
            # Save ideas to IdeaInspiration database
            ideas_saved = []
            first_idea_id = None
            
            for idea in ideas:
                try:
                    idea_id = self.idea_db.insert(idea)
                    if first_idea_id is None:
                        first_idea_id = idea_id
                    ideas_saved.append({
                        'idea_id': idea_id,
                        'title': idea.title,
                        'source_id': idea.source_id
                    })
                except Exception as e:
                    logger.error(f"Failed to save idea: {e}")
                    continue
            
            logger.info(
                f"Successfully scraped r/{subreddit}, "
                f"saved {len(ideas_saved)}/{len(ideas)} ideas"
            )
            
            return {
                'success': True,
                'idea_inspiration_id': first_idea_id,
                'processed_at': datetime.now(timezone.utc).isoformat(),
                'items_processed': len(ideas_saved),
                'subreddit': subreddit,
                'sort': sort,
                'posts_scraped': len(ideas),
                'posts_saved': len(ideas_saved)
            }
            
        except Exception as e:
            error_msg = f"Error processing Reddit task: {e}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'error': error_msg
            }


__all__ = ['RedditSubredditWorker']
