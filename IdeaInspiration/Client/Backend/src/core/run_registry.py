"""Registry for tracking module runs."""

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from ..models.run import Run, RunStatus

logger = logging.getLogger(__name__)


class RunRegistry:
    """
    Registry for tracking module runs.
    
    Responsibilities:
    - Store active and completed runs
    - Query runs by status, module, time
    - Persist run history to disk
    - Cleanup old runs
    
    This class follows SOLID principles:
    - Single Responsibility: Only handles run storage and retrieval
    - Open/Closed: Can be extended with new query methods
    - Liskov Substitution: Could be swapped with a database-backed implementation
    - Interface Segregation: Provides focused methods for different query needs
    """
    
    def __init__(self, history_file: Optional[Path] = None):
        """
        Initialize run registry.
        
        Args:
            history_file: Path to JSON file for persisting run history.
                         Defaults to ./data/run_history.json
        """
        self.runs: Dict[str, Run] = {}
        self.history_file = history_file or Path("./data/run_history.json")
        self._load_history()
    
    def add_run(self, run: Run):
        """
        Add a new run to the registry.
        
        Args:
            run: Run object to add
        """
        self.runs[run.run_id] = run
        self._save_history()
    
    def update_run(self, run: Run):
        """
        Update an existing run.
        
        Args:
            run: Run object with updated information
        """
        self.runs[run.run_id] = run
        self._save_history()
    
    def get_run(self, run_id: str) -> Optional[Run]:
        """
        Get a run by ID.
        
        Args:
            run_id: Run identifier
            
        Returns:
            Run object if found, None otherwise
        """
        return self.runs.get(run_id)
    
    def get_active_runs(self) -> List[Run]:
        """
        Get all active (queued or running) runs.
        
        Returns:
            List of runs that are currently queued or running
        """
        return [
            run for run in self.runs.values()
            if run.status in [RunStatus.QUEUED, RunStatus.RUNNING]
        ]
    
    def get_runs_by_module(self, module_id: str) -> List[Run]:
        """
        Get all runs for a specific module.
        
        Args:
            module_id: Module identifier
            
        Returns:
            List of runs for the specified module
        """
        return [
            run for run in self.runs.values()
            if run.module_id == module_id
        ]
    
    def get_runs_by_status(self, status: RunStatus) -> List[Run]:
        """
        Get all runs with a specific status.
        
        Args:
            status: Run status to filter by
            
        Returns:
            List of runs with the specified status
        """
        return [
            run for run in self.runs.values()
            if run.status == status
        ]
    
    def get_recent_runs(self, limit: int = 50) -> List[Run]:
        """
        Get most recent runs.
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            List of most recent runs, sorted by creation time (newest first)
        """
        sorted_runs = sorted(
            self.runs.values(),
            key=lambda r: r.created_at,
            reverse=True
        )
        return sorted_runs[:limit]
    
    def cleanup_old_runs(self, days: int = 30):
        """
        Remove runs older than specified days.
        
        Only removes completed runs (successful, failed, or cancelled).
        
        Args:
            days: Number of days to keep runs
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        to_remove = [
            run_id for run_id, run in self.runs.items()
            if run.completed_at and run.completed_at < cutoff
        ]
        for run_id in to_remove:
            del self.runs[run_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old runs")
            self._save_history()
    
    def _save_history(self):
        """Persist runs to disk as JSON."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w') as f:
                data = {
                    run_id: run.model_dump(mode='json')
                    for run_id, run in self.runs.items()
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save run history: {e}")
    
    def _load_history(self):
        """Load runs from disk."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.runs = {}
                    for run_id, run_data in data.items():
                        run = Run.model_validate(run_data)
                        # Ensure datetime fields are timezone-aware
                        if run.created_at and run.created_at.tzinfo is None:
                            run.created_at = run.created_at.replace(tzinfo=timezone.utc)
                        if run.started_at and run.started_at.tzinfo is None:
                            run.started_at = run.started_at.replace(tzinfo=timezone.utc)
                        if run.completed_at and run.completed_at.tzinfo is None:
                            run.completed_at = run.completed_at.replace(tzinfo=timezone.utc)
                        self.runs[run_id] = run
                logger.info(f"Loaded {len(self.runs)} runs from history")
            except Exception as e:
                logger.error(f"Failed to load run history: {e}")
                self.runs = {}
