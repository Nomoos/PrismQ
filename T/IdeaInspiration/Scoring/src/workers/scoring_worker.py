"""Concrete scoring worker implementation.

Implements specific scoring logic for different task types:
- text_scoring: Score text content quality
- engagement_scoring: Score based on engagement metrics
- batch_scoring: Score multiple items in a batch
"""

import logging
from typing import Dict, Any, Optional

from . import Task, TaskResult
from .base_scoring_worker import BaseScoringWorker
from ..models import ScoreBreakdown

logger = logging.getLogger(__name__)


class ScoringWorker(BaseScoringWorker):
    """Concrete implementation of scoring worker.
    
    Processes scoring tasks using the ScoringEngine and reports results.
    Supports multiple task types for different scoring scenarios.
    """
    
    def register_task_types(self) -> None:
        """Register scoring task types with TaskManager API."""
        if not self.taskmanager_client:
            logger.info("TaskManager not available, skipping task type registration")
            return
        
        logger.info("Registering scoring task types with TaskManager API...")
        
        # Define task types this worker can process
        task_types = [
            {
                "name": "PrismQ.Scoring.TextScoring",
                "version": "1.0.0",
                "param_schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Content title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Content description"
                        },
                        "text_content": {
                            "type": "string",
                            "description": "Full text content to score"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Optional metadata (engagement stats, etc.)"
                        }
                    },
                    "required": ["title", "text_content"]
                }
            },
            {
                "name": "PrismQ.Scoring.EngagementScoring",
                "version": "1.0.0",
                "param_schema": {
                    "type": "object",
                    "properties": {
                        "views": {
                            "type": "integer",
                            "description": "View count"
                        },
                        "likes": {
                            "type": "integer",
                            "description": "Like count"
                        },
                        "comments": {
                            "type": "integer",
                            "description": "Comment count"
                        },
                        "shares": {
                            "type": "integer",
                            "description": "Share count"
                        },
                        "platform": {
                            "type": "string",
                            "enum": ["youtube", "reddit", "tiktok", "generic"],
                            "description": "Source platform"
                        }
                    },
                    "required": ["views", "likes", "comments"]
                }
            },
            {
                "name": "PrismQ.Scoring.BatchScoring",
                "version": "1.0.0",
                "param_schema": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "description": "Array of items to score",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "text_content": {"type": "string"},
                                    "metadata": {"type": "object"}
                                }
                            }
                        }
                    },
                    "required": ["items"]
                }
            }
        ]
        
        # Register each task type
        for task_type_def in task_types:
            try:
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
        
        logger.info(f"Registered {len(self.task_type_ids)} task types: {self.task_type_ids}")
    
    def process_task(self, task: Task) -> TaskResult:
        """Process a scoring task based on task type.
        
        Args:
            task: Task to process
            
        Returns:
            TaskResult with scoring data
        """
        try:
            task_type = task.task_type
            params = task.parameters
            
            logger.info(f"Processing task {task.id} (type: {task_type})")
            logger.debug(f"Task parameters: {params}")
            
            # Route to appropriate handler based on task type
            if "TextScoring" in task_type:
                result_data = self._process_text_scoring(params)
            elif "EngagementScoring" in task_type:
                result_data = self._process_engagement_scoring(params)
            elif "BatchScoring" in task_type:
                result_data = self._process_batch_scoring(params)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            return TaskResult(
                success=True,
                data=result_data,
                items_processed=result_data.get('items_processed', 1)
            )
            
        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}", exc_info=True)
            return TaskResult(
                success=False,
                error=str(e),
                items_processed=0
            )
    
    def _process_text_scoring(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process text scoring task.
        
        Args:
            params: Task parameters with title, description, text_content
            
        Returns:
            Scoring results dictionary
        """
        title = params.get('title', '')
        description = params.get('description', '')
        text_content = params.get('text_content', '')
        metadata = params.get('metadata', {})
        
        logger.info(f"Scoring text content (title: '{title[:50]}...')")
        
        # Create mock IdeaInspiration object for scoring
        class MockIdeaInspiration:
            def __init__(self, title, description, text_content, metadata):
                self.title = title
                self.description = description
                self.text_content = text_content
                self.metadata = metadata
        
        idea = MockIdeaInspiration(title, description, text_content, metadata)
        
        # Score using ScoringEngine
        score_breakdown: ScoreBreakdown = self.scoring_engine.score_idea_inspiration(idea)
        
        return {
            'score_breakdown': score_breakdown.to_dict(),
            'overall_score': score_breakdown.overall_score,
            'items_processed': 1
        }
    
    def _process_engagement_scoring(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process engagement scoring task.
        
        Args:
            params: Task parameters with engagement metrics
            
        Returns:
            Engagement scoring results
        """
        metrics = {
            'views': params.get('views', 0),
            'likes': params.get('likes', 0),
            'comments': params.get('comments', 0),
            'shares': params.get('shares', 0),
        }
        
        platform = params.get('platform', 'generic')
        
        logger.info(f"Scoring engagement metrics (platform: {platform})")
        
        # Calculate engagement score
        if platform == 'youtube':
            score, details = self.scoring_engine.calculate_youtube_score({
                'statistics': {
                    'viewCount': str(metrics['views']),
                    'likeCount': str(metrics['likes']),
                    'commentCount': str(metrics['comments'])
                }
            })
        elif platform == 'reddit':
            score, details = self.scoring_engine.calculate_reddit_score({
                'num_views': metrics['views'],
                'score': metrics['likes'],
                'num_comments': metrics['comments']
            })
        else:
            score, details = self.scoring_engine.calculate_score(metrics)
        
        return {
            'engagement_score': score,
            'score_details': details,
            'platform': platform,
            'items_processed': 1
        }
    
    def _process_batch_scoring(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process batch scoring task.
        
        Args:
            params: Task parameters with array of items to score
            
        Returns:
            Batch scoring results
        """
        items = params.get('items', [])
        
        logger.info(f"Scoring batch of {len(items)} items")
        
        results = []
        
        for idx, item in enumerate(items):
            try:
                # Score each item
                title = item.get('title', '')
                description = item.get('description', '')
                text_content = item.get('text_content', '')
                metadata = item.get('metadata', {})
                
                # Create mock IdeaInspiration
                class MockIdeaInspiration:
                    def __init__(self, title, description, text_content, metadata):
                        self.title = title
                        self.description = description
                        self.text_content = text_content
                        self.metadata = metadata
                
                idea = MockIdeaInspiration(title, description, text_content, metadata)
                
                # Score
                score_breakdown = self.scoring_engine.score_idea_inspiration(idea)
                
                results.append({
                    'index': idx,
                    'success': True,
                    'score': score_breakdown.overall_score,
                    'score_breakdown': score_breakdown.to_dict()
                })
                
            except Exception as e:
                logger.error(f"Error scoring item {idx}: {e}")
                results.append({
                    'index': idx,
                    'success': False,
                    'error': str(e)
                })
        
        successful = sum(1 for r in results if r['success'])
        
        return {
            'results': results,
            'total_items': len(items),
            'successful': successful,
            'failed': len(items) - successful,
            'items_processed': successful
        }


__all__ = ["ScoringWorker"]
