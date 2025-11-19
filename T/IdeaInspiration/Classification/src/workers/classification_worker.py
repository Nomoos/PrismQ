"""Classification Worker for processing classification tasks.

This worker processes classification tasks from TaskManager API,
enriches IdeaInspiration objects with classification metadata,
and saves results to the IdeaInspiration database.

Following SOLID principles:
- Single Responsibility: Only handles classification enrichment
- Dependency Inversion: Depends on abstractions (Config, Database)
- Liskov Substitution: Can substitute BaseWorker in any context
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import sys

# Import classification module
classification_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(classification_root))

from classification import TextClassifier, ClassificationEnrichment
from classification import IdeaInspiration, ContentType

# Import Model database
import sys
from pathlib import Path

# Add parent directory to import Model as package
# parents[3] is the repository root where Model and Classification are
parent_path = Path(__file__).resolve().parents[3]
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

# Import from Model package
from Model import IdeaInspirationDatabase

# Import worker base
from . import Task, TaskResult, TaskStatus


logger = logging.getLogger(__name__)


class ClassificationWorker:
    """Worker for processing classification enrichment tasks.
    
    This worker enriches IdeaInspiration objects with classification metadata
    including category, story detection, flags, and tags.
    
    Task Parameters:
        idea_inspiration_id: ID of IdeaInspiration object to classify (optional if idea_data provided)
        idea_data: IdeaInspiration data dictionary (optional if idea_inspiration_id provided)
        save_to_db: Whether to save enriched data back to database (default: True)
    
    Task Types:
        - classification_enrich: Classify and enrich an IdeaInspiration object
        - classification_batch: Batch classification of multiple IdeaInspiration objects
    
    Example Tasks:
        Single classification:
        {
            "task_type": "classification_enrich",
            "parameters": {
                "idea_inspiration_id": "12345"
            }
        }
        
        Classification with data:
        {
            "task_type": "classification_enrich",
            "parameters": {
                "idea_data": {
                    "title": "Amazing story",
                    "description": "...",
                    ...
                }
            }
        }
        
        Batch classification:
        {
            "task_type": "classification_batch",
            "parameters": {
                "idea_inspiration_ids": ["123", "456", "789"]
            }
        }
    """
    
    def __init__(
        self,
        worker_id: str,
        idea_db_path: Optional[str] = None,
    ):
        """Initialize Classification Worker.
        
        Args:
            worker_id: Unique worker identifier
            idea_db_path: Path to IdeaInspiration database
        """
        self.worker_id = worker_id
        
        # Initialize classifier
        self.classifier = TextClassifier()
        
        # Initialize IdeaInspiration database
        self.idea_db_path = idea_db_path or 'ideas.db'
        self.idea_db = IdeaInspirationDatabase(self.idea_db_path, interactive=False)
        
        # Statistics
        self.tasks_processed = 0
        self.tasks_failed = 0
        
        logger.info(
            f"ClassificationWorker {worker_id} initialized "
            f"(idea_db: {self.idea_db_path})"
        )
    
    def _update_classification_in_db(
        self,
        idea_id: int,
        category: str,
        subcategory_relevance: Dict[str, int],
        metadata: Dict[str, Any]
    ):
        """Update classification fields in database.
        
        Since IdeaInspirationDatabase doesn't have an update method,
        we directly execute SQL UPDATE.
        
        Args:
            idea_id: ID of IdeaInspiration to update
            category: Primary category
            subcategory_relevance: Subcategory relevance scores
            metadata: Metadata with classification info
        """
        import sqlite3
        
        conn = sqlite3.connect(self.idea_db_path)
        cursor = conn.cursor()
        
        try:
            # Convert dicts to JSON strings
            subcategory_json = json.dumps(subcategory_relevance)
            metadata_json = json.dumps(metadata)
            
            cursor.execute("""
                UPDATE IdeaInspiration 
                SET category = ?,
                    subcategory_relevance = ?,
                    metadata = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (category, subcategory_json, metadata_json, idea_id))
            
            conn.commit()
            
        finally:
            conn.close()
    
    def process_task(self, task: Task) -> TaskResult:
        """Process a classification task.
        
        Args:
            task: Task object with type and parameters
            
        Returns:
            TaskResult with success status and classification data
        """
        try:
            logger.info(f"Processing classification task {task.id} (type: {task.task_type})")
            
            # Route to appropriate handler based on task type
            if task.task_type == "classification_enrich":
                return self._process_single_classification(task)
            elif task.task_type == "classification_batch":
                return self._process_batch_classification(task)
            else:
                return TaskResult(
                    success=False,
                    data={},
                    error=f"Unknown task type: {task.task_type}"
                )
        
        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}", exc_info=True)
            self.tasks_failed += 1
            return TaskResult(
                success=False,
                data={},
                error=str(e)
            )
    
    def _process_single_classification(self, task: Task) -> TaskResult:
        """Process a single classification task.
        
        Args:
            task: Task with idea_inspiration_id or idea_data
            
        Returns:
            TaskResult with classification enrichment
        """
        params = task.params
        save_to_db = params.get('save_to_db', True)
        
        # Get IdeaInspiration object
        if 'idea_inspiration_id' in params:
            idea_id = params['idea_inspiration_id']
            logger.info(f"Fetching IdeaInspiration {idea_id} from database")
            
            # Convert idea_id to int if it's a string
            try:
                idea_id_int = int(idea_id)
            except (ValueError, TypeError):
                return TaskResult(
                    success=False,
                    data={},
                    error=f"Invalid idea_inspiration_id: {idea_id}"
                )
            
            idea = self.idea_db.get_by_id(idea_id_int)
            if not idea:
                return TaskResult(
                    success=False,
                    data={},
                    error=f"IdeaInspiration {idea_id} not found"
                )
        elif 'idea_data' in params:
            logger.info("Creating IdeaInspiration from provided data")
            idea = IdeaInspiration.from_dict(params['idea_data'])
            idea_id = None
        else:
            return TaskResult(
                success=False,
                data={},
                error="Either 'idea_inspiration_id' or 'idea_data' required"
            )
        
        # Classify the content
        logger.info(f"Classifying content: {idea.title[:50]}...")
        enrichment = self.classifier.enrich(idea)
        
        # Update IdeaInspiration with classification metadata
        idea.category = enrichment.category.value
        
        # Convert tags to subcategory_relevance scores
        if enrichment.tags:
            for tag in enrichment.tags:
                relevance_score = int(enrichment.category_confidence * 100)
                idea.subcategory_relevance[tag] = relevance_score
        
        # Add classification flags to metadata
        if not idea.metadata:
            idea.metadata = {}
        idea.metadata['classification'] = {
            'is_story': enrichment.flags.get('is_story', False),
            'is_usable': enrichment.flags.get('is_usable', True),
            'category_confidence': enrichment.category_confidence,
            'classified_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Save to database if requested
        if save_to_db:
            if idea_id:
                # Update classification fields for existing ideas
                # The database doesn't have an update method, so we do it directly
                try:
                    self._update_classification_in_db(
                        idea_id_int,
                        idea.category,
                        idea.subcategory_relevance,
                        idea.metadata
                    )
                    logger.info(f"Classification updated for IdeaInspiration {idea_id}")
                except Exception as e:
                    logger.warning(f"Failed to update classification in database: {e}")
            else:
                logger.info("Saving new IdeaInspiration to database")
                idea_id = self.idea_db.insert(idea)
                logger.info(f"Saved as IdeaInspiration {idea_id}")
        
        self.tasks_processed += 1
        
        return TaskResult(
            success=True,
            data={
                'idea_inspiration_id': idea_id,
                'category': enrichment.category.value,
                'category_confidence': enrichment.category_confidence,
                'flags': enrichment.flags,
                'tags': enrichment.tags,
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
        )
    
    def _process_batch_classification(self, task: Task) -> TaskResult:
        """Process batch classification of multiple IdeaInspiration objects.
        
        Args:
            task: Task with list of idea_inspiration_ids
            
        Returns:
            TaskResult with batch classification results
        """
        params = task.params
        idea_ids = params.get('idea_inspiration_ids', [])
        
        if not idea_ids:
            return TaskResult(
                success=False,
                data={},
                error="'idea_inspiration_ids' list is required"
            )
        
        logger.info(f"Processing batch classification for {len(idea_ids)} ideas")
        
        results = []
        successful = 0
        failed = 0
        
        for idea_id in idea_ids:
            try:
                # Create sub-task for single classification
                sub_task = Task(
                    id=f"{task.id}-{idea_id}",
                    task_type="classification_enrich",
                    params={
                        'idea_inspiration_id': idea_id,
                        'save_to_db': params.get('save_to_db', True)
                    },
                    status=TaskStatus.CLAIMED
                )
                
                result = self._process_single_classification(sub_task)
                
                if result.success:
                    successful += 1
                else:
                    failed += 1
                
                results.append({
                    'idea_inspiration_id': idea_id,
                    'success': result.success,
                    'data': result.data,
                    'error': result.error
                })
                
            except Exception as e:
                logger.error(f"Error classifying {idea_id}: {e}")
                failed += 1
                results.append({
                    'idea_inspiration_id': idea_id,
                    'success': False,
                    'error': str(e)
                })
        
        logger.info(
            f"Batch classification complete: "
            f"{successful} successful, {failed} failed"
        )
        
        return TaskResult(
            success=True,
            data={
                'total': len(idea_ids),
                'successful': successful,
                'failed': failed,
                'results': results,
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
        )
    
    def find_unclassified_ideas(self, limit: int = 10) -> list:
        """Find IdeaInspiration records without classification.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of IdeaInspiration IDs that need classification
        """
        import sqlite3
        
        try:
            conn = sqlite3.connect(self.idea_db_path)
            cursor = conn.cursor()
            
            # Find records where category is NULL or empty
            cursor.execute("""
                SELECT id FROM IdeaInspiration 
                WHERE category IS NULL OR category = ''
                ORDER BY created_at ASC
                LIMIT ?
            """, (limit,))
            
            ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return ids
            
        except Exception as e:
            logger.error(f"Error finding unclassified ideas: {e}")
            return []
    
    def process_unclassified_ideas(self, limit: int = 10) -> Dict[str, Any]:
        """Process unclassified IdeaInspiration records from database.
        
        This method is called when the worker is idle (no TaskManager tasks).
        It finds and classifies IdeaInspiration records that don't have
        classification yet.
        
        Args:
            limit: Maximum number of records to process
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Checking for unclassified IdeaInspiration records (limit: {limit})")
        
        # Find unclassified ideas
        unclassified_ids = self.find_unclassified_ideas(limit)
        
        if not unclassified_ids:
            logger.debug("No unclassified IdeaInspiration records found")
            return {
                'processed': 0,
                'successful': 0,
                'failed': 0
            }
        
        logger.info(f"Found {len(unclassified_ids)} unclassified records, processing...")
        
        # Process each unclassified idea
        successful = 0
        failed = 0
        
        for idea_id in unclassified_ids:
            try:
                # Create a task for this idea
                task = Task(
                    id=f"auto-{idea_id}",
                    task_type="classification_enrich",
                    params={
                        'idea_inspiration_id': str(idea_id),
                        'save_to_db': True
                    },
                    status=TaskStatus.CLAIMED
                )
                
                # Process the task
                result = self._process_single_classification(task)
                
                if result.success:
                    successful += 1
                    logger.debug(
                        f"Classified IdeaInspiration {idea_id}: "
                        f"{result.data.get('category')}"
                    )
                else:
                    failed += 1
                    logger.warning(f"Failed to classify IdeaInspiration {idea_id}: {result.error}")
                    
            except Exception as e:
                failed += 1
                logger.error(f"Error processing unclassified idea {idea_id}: {e}")
        
        logger.info(
            f"Processed {len(unclassified_ids)} unclassified records: "
            f"{successful} successful, {failed} failed"
        )
        
        return {
            'processed': len(unclassified_ids),
            'successful': successful,
            'failed': failed
        }


__all__ = ['ClassificationWorker']
