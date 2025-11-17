"""Register HackerNews task types with TaskManager API."""

import sys
from pathlib import Path
import logging

# Add parent directories to path
_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_root))

try:
    from TaskManager import TaskManagerClient
except ImportError:
    print("ERROR: TaskManager module not found. Please ensure it's installed.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_hackernews_task_types():
    """Register HackerNews Stories task types with TaskManager API."""
    
    try:
        client = TaskManagerClient()
    except Exception as e:
        logger.error(f"Failed to initialize TaskManager client: {e}")
        return False
    
    task_types = [
        {
            "name": "PrismQ.Text.HackerNews.Story.Fetch",
            "version": "1.0.0",
            "description": "Fetch stories from HackerNews",
            "param_schema": {
                "type": "object",
                "properties": {
                    "story_type": {
                        "type": "string",
                        "enum": ["top", "best", "new", "ask", "show", "job"],
                        "default": "top",
                        "description": "Type of stories to fetch"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 500,
                        "default": 30,
                        "description": "Maximum number of stories to fetch"
                    }
                }
            }
        },
        {
            "name": "PrismQ.Text.HackerNews.Story.FrontPage",
            "version": "1.0.0",
            "description": "Fetch front page stories from HackerNews",
            "param_schema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 30,
                        "default": 30,
                        "description": "Number of front page stories"
                    }
                }
            }
        },
        {
            "name": "PrismQ.Text.HackerNews.Story.Best",
            "version": "1.0.0",
            "description": "Fetch best stories from HackerNews",
            "param_schema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 30,
                        "description": "Number of best stories to fetch"
                    }
                }
            }
        },
        {
            "name": "PrismQ.Text.HackerNews.Story.New",
            "version": "1.0.0",
            "description": "Fetch new stories from HackerNews",
            "param_schema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 30,
                        "description": "Number of new stories to fetch"
                    }
                }
            }
        },
        {
            "name": "PrismQ.Text.HackerNews.Story.Ask",
            "version": "1.0.0",
            "description": "Fetch Ask HN stories from HackerNews",
            "param_schema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 30,
                        "description": "Number of Ask HN stories to fetch"
                    }
                }
            }
        },
        {
            "name": "PrismQ.Text.HackerNews.Story.Show",
            "version": "1.0.0",
            "description": "Fetch Show HN stories from HackerNews",
            "param_schema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 30,
                        "description": "Number of Show HN stories to fetch"
                    }
                }
            }
        },
        {
            "name": "PrismQ.Text.HackerNews.Story.Job",
            "version": "1.0.0",
            "description": "Fetch job postings from HackerNews",
            "param_schema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 30,
                        "description": "Number of job postings to fetch"
                    }
                }
            }
        }
    ]
    
    success_count = 0
    for task_type in task_types:
        try:
            client.register_task_type(**task_type)
            logger.info(f"✅ Registered: {task_type['name']}")
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Failed to register {task_type['name']}: {e}")
    
    logger.info(f"\nRegistered {success_count}/{len(task_types)} task types")
    return success_count == len(task_types)


if __name__ == "__main__":
    success = register_hackernews_task_types()
    sys.exit(0 if success else 1)
