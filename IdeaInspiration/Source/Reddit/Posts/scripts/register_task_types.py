"""Register Reddit task types with TaskManager API.

This script registers the Reddit Posts task types with the external TaskManager
service. It should be run once during setup or when task type definitions change.

Task types defined:
- PrismQ.Text.Reddit.Post.Fetch: Fetch posts from a specific subreddit
- PrismQ.Text.Reddit.Post.Search: Search for posts across Reddit
- PrismQ.Text.Reddit.Post.Trending: Fetch trending posts

Usage:
    python scripts/register_task_types.py
"""

import sys
from pathlib import Path
import logging
"""Register Reddit task types with TaskManager API."""

import sys
from pathlib import Path

# Add parent directories to path
_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_root))

# Add TaskManager to path
_taskmanager_path = _root / 'TaskManager'
if str(_taskmanager_path) not in sys.path:
    sys.path.insert(0, str(_taskmanager_path))

try:
    from src.client import TaskManagerClient
    _taskmanager_available = True
except ImportError:
    _taskmanager_available = False
    print("ERROR: TaskManager client not available")
    print("Make sure TaskManager module is installed and accessible")
    sys.exit(1)
from TaskManager import TaskManagerClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_reddit_task_types():
    """Register Reddit Posts task types with TaskManager API.
    
    This function defines and registers three task types:
    1. Fetch: Get posts from a specific subreddit
    2. Search: Search for posts across Reddit
    3. Trending: Get trending posts from Reddit
    
    Each task type includes a JSON schema for parameter validation.
    """
    """Register Reddit Posts task types with TaskManager API."""
    
    client = TaskManagerClient()
    
    task_types = [
        {
            "name": "PrismQ.Text.Reddit.Post.Fetch",
            "version": "1.0.0",
            "description": "Fetch posts from a Reddit subreddit",
            "param_schema": {
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Subreddit name (without r/)"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["hot", "new", "top", "rising"],
                        "default": "hot",
                        "description": "Sort order for posts"
                    },
                    "time_filter": {
                        "type": "string",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "default": "day",
                        "description": "Time filter for 'top' sort"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1000,
                        "default": 100,
                        "description": "Maximum number of posts to fetch"
                    }
                },
                "required": ["subreddit"]
            }
        },
        {
            "name": "PrismQ.Text.Reddit.Post.Search",
            "version": "1.0.0",
            "description": "Search for posts across Reddit",
            "param_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "subreddit": {
                        "type": "string",
                        "description": "Optional: Limit search to specific subreddit"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["relevance", "hot", "top", "new", "comments"],
                        "default": "relevance",
                        "description": "Sort order for search results"
                    },
                    "time_filter": {
                        "type": "string",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "default": "week",
                        "description": "Time filter for search"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 25,
                        "description": "Maximum number of results"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "PrismQ.Text.Reddit.Post.Trending",
            "version": "1.0.0",
            "description": "Fetch trending posts from Reddit",
            "param_schema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 50,
                        "description": "Maximum number of trending posts"
                    }
                }
            }
        }
    ]
    
    success_count = 0
                        "default": 50
                    }
                }
            }
        }
    ]
    
    for task_type in task_types:
        try:
            client.register_task_type(**task_type)
            logger.info(f"✅ Registered: {task_type['name']}")
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Failed to register {task_type['name']}: {e}")
    
    logger.info(f"\nRegistration complete: {success_count}/{len(task_types)} task types registered")
    return success_count == len(task_types)


if __name__ == "__main__":
    print("=" * 70)
    print("Reddit Posts Task Type Registration")
    print("=" * 70)
    print()
    
    if not _taskmanager_available:
        print("ERROR: TaskManager client is not available")
        sys.exit(1)
    
    success = register_reddit_task_types()
    
    print()
    print("=" * 70)
    if success:
        print("✅ All task types registered successfully")
        sys.exit(0)
    else:
        print("⚠️  Some task types failed to register")
        sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Failed to register {task_type['name']}: {e}")


if __name__ == "__main__":
    register_reddit_task_types()
