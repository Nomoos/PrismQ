"""Data models for queue database entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import json


class SchedulingStrategy(str, Enum):
    """
    Task queue scheduling strategies.
    
    Defines different approaches for claiming tasks from the queue.
    Each strategy provides different ordering guarantees and fairness characteristics.
    """
    
    FIFO = "fifo"                       # First-In-First-Out (oldest first)
    LIFO = "lifo"                       # Last-In-First-Out (newest first)
    PRIORITY = "priority"               # Priority-based (lower number = higher priority)
    WEIGHTED_RANDOM = "weighted_random" # Probabilistic selection weighted by priority


@dataclass
class WorkerConfig:
    """
    Worker configuration including scheduling strategy.
    
    Follows SOLID principles:
    - Single Responsibility: Represents worker configuration only
    - Open/Closed: Can be extended without modification
    """
    
    worker_id: str
    capabilities: Dict[str, Any] = field(default_factory=dict)
    scheduling_strategy: SchedulingStrategy = SchedulingStrategy.PRIORITY
    lease_duration_seconds: int = 60
    poll_interval_seconds: int = 1
    max_retries: int = 3


@dataclass
class Task:
    """
    Represents a task in the queue.
    
    Follows SOLID principles:
    - Single Responsibility: Represents task data only
    - Open/Closed: Can be extended without modification
    """

    id: Optional[int] = None
    type: str = ""
    priority: int = 100
    payload: str = "{}"
    compatibility: str = "{}"
    status: str = "queued"
    attempts: int = 0
    max_attempts: int = 5
    run_after_utc: Optional[datetime] = None
    lease_until_utc: Optional[datetime] = None
    reserved_at_utc: Optional[datetime] = None
    processing_started_utc: Optional[datetime] = None
    finished_at_utc: Optional[datetime] = None
    locked_by: Optional[str] = None
    error_message: Optional[str] = None
    idempotency_key: Optional[str] = None
    created_at_utc: Optional[datetime] = None
    updated_at_utc: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "type": self.type,
            "priority": self.priority,
            "payload": self.payload,
            "compatibility": self.compatibility,
            "status": self.status,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "run_after_utc": (
                self.run_after_utc.isoformat() if self.run_after_utc else None
            ),
            "lease_until_utc": (
                self.lease_until_utc.isoformat() if self.lease_until_utc else None
            ),
            "reserved_at_utc": (
                self.reserved_at_utc.isoformat() if self.reserved_at_utc else None
            ),
            "processing_started_utc": (
                self.processing_started_utc.isoformat()
                if self.processing_started_utc
                else None
            ),
            "finished_at_utc": (
                self.finished_at_utc.isoformat() if self.finished_at_utc else None
            ),
            "locked_by": self.locked_by,
            "error_message": self.error_message,
            "idempotency_key": self.idempotency_key,
            "created_at_utc": (
                self.created_at_utc.isoformat() if self.created_at_utc else None
            ),
            "updated_at_utc": (
                self.updated_at_utc.isoformat() if self.updated_at_utc else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create Task from dictionary representation."""

        def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
            """Parse datetime string to datetime object."""
            if dt_str is None:
                return None
            # Handle both ISO format and SQLite datetime format
            if "T" in dt_str:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            else:
                # SQLite datetime format: YYYY-MM-DD HH:MM:SS
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

        return cls(
            id=data.get("id"),
            type=data.get("type", ""),
            priority=data.get("priority", 100),
            payload=data.get("payload", "{}"),
            compatibility=data.get("compatibility", "{}"),
            status=data.get("status", "queued"),
            attempts=data.get("attempts", 0),
            max_attempts=data.get("max_attempts", 5),
            run_after_utc=parse_datetime(data.get("run_after_utc")),
            lease_until_utc=parse_datetime(data.get("lease_until_utc")),
            reserved_at_utc=parse_datetime(data.get("reserved_at_utc")),
            processing_started_utc=parse_datetime(data.get("processing_started_utc")),
            finished_at_utc=parse_datetime(data.get("finished_at_utc")),
            locked_by=data.get("locked_by"),
            error_message=data.get("error_message"),
            idempotency_key=data.get("idempotency_key"),
            created_at_utc=parse_datetime(data.get("created_at_utc")),
            updated_at_utc=parse_datetime(data.get("updated_at_utc")),
        )

    def get_payload_dict(self) -> Dict[str, Any]:
        """Get payload as dictionary."""
        try:
            return json.loads(self.payload)
        except json.JSONDecodeError:
            return {}

    def get_compatibility_dict(self) -> Dict[str, Any]:
        """Get compatibility as dictionary."""
        try:
            return json.loads(self.compatibility)
        except json.JSONDecodeError:
            return {}


@dataclass
class Worker:
    """
    Represents a worker in the system.
    
    Follows SOLID principles:
    - Single Responsibility: Represents worker data only
    """

    worker_id: str = ""
    capabilities: str = "{}"
    heartbeat_utc: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert worker to dictionary representation."""
        return {
            "worker_id": self.worker_id,
            "capabilities": self.capabilities,
            "heartbeat_utc": (
                self.heartbeat_utc.isoformat() if self.heartbeat_utc else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Worker":
        """Create Worker from dictionary representation."""

        def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
            """Parse datetime string to datetime object."""
            if dt_str is None:
                return None
            if "T" in dt_str:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            else:
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

        return cls(
            worker_id=data.get("worker_id", ""),
            capabilities=data.get("capabilities", "{}"),
            heartbeat_utc=parse_datetime(data.get("heartbeat_utc")),
        )

    def get_capabilities_dict(self) -> Dict[str, Any]:
        """Get capabilities as dictionary."""
        try:
            return json.loads(self.capabilities)
        except json.JSONDecodeError:
            return {}


@dataclass
class TaskLog:
    """
    Represents a log entry for a task.
    
    Follows SOLID principles:
    - Single Responsibility: Represents log entry data only
    """

    log_id: Optional[int] = None
    task_id: int = 0
    at_utc: Optional[datetime] = None
    level: str = "INFO"
    message: Optional[str] = None
    details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task log to dictionary representation."""
        return {
            "log_id": self.log_id,
            "task_id": self.task_id,
            "at_utc": self.at_utc.isoformat() if self.at_utc else None,
            "level": self.level,
            "message": self.message,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskLog":
        """Create TaskLog from dictionary representation."""

        def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
            """Parse datetime string to datetime object."""
            if dt_str is None:
                return None
            if "T" in dt_str:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            else:
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

        return cls(
            log_id=data.get("log_id"),
            task_id=data.get("task_id", 0),
            at_utc=parse_datetime(data.get("at_utc")),
            level=data.get("level", "INFO"),
            message=data.get("message"),
            details=data.get("details"),
        )
