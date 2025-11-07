"""Core module runner service."""

import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, TYPE_CHECKING

from ..models.run import Run, RunStatus
from .output_capture import OutputCapture
from .process_manager import ProcessManager
from .run_registry import RunRegistry
from .subprocess_wrapper import SubprocessWrapper, RunMode
from .exceptions import (
    ModuleExecutionException,
    ResourceLimitException,
    SubprocessPolicyException,
)

if TYPE_CHECKING:
    from .config_storage import ConfigStorage
    from .resource_manager import ResourceManager

logger = logging.getLogger(__name__)


class ModuleRunner:
    """
    Core service for executing PrismQ modules asynchronously.
    
    Responsibilities:
    - Launch module scripts with parameters
    - Track run lifecycle (queued -> running -> completed/failed)
    - Manage concurrent executions
    - Capture and store output logs
    
    This class follows SOLID principles:
    - Single Responsibility: Orchestrates module execution lifecycle
    - Open/Closed: Can be extended with hooks for monitoring/notifications
    - Liskov Substitution: Interface could be abstracted for different runners
    - Interface Segregation: Provides minimal, focused methods
    - Dependency Inversion: Depends on abstractions (ProcessManager, RunRegistry)
    """
    
    def __init__(
        self,
        registry: RunRegistry,
        process_manager: ProcessManager,
        config_storage: Optional["ConfigStorage"] = None,
        output_capture: Optional[OutputCapture] = None,
        resource_manager: Optional["ResourceManager"] = None,
        max_concurrent_runs: int = 10,
        run_mode: Optional[RunMode] = None
    ):
        """
        Initialize module runner.
        
        Args:
            registry: Run registry for state management
            process_manager: Process manager for subprocess execution
            config_storage: Optional configuration storage for saving parameters
            output_capture: Optional output capture service for log streaming
            resource_manager: Optional resource manager for system resource checks
            max_concurrent_runs: Maximum number of concurrent runs allowed
            run_mode: Subprocess execution mode (auto-detected if None)
        """
        self.registry = registry
        self.process_manager = process_manager
        self.config_storage = config_storage
        self.output_capture = output_capture
        self.resource_manager = resource_manager
        self.max_concurrent_runs = max_concurrent_runs
        
        # Initialize subprocess wrapper with run mode
        # Check environment variable for override
        env_mode = os.environ.get('PRISMQ_RUN_MODE')
        if env_mode:
            try:
                run_mode = RunMode(env_mode.lower())
                logger.info(f"Using run mode from environment: {run_mode}")
            except ValueError:
                logger.warning(f"Invalid PRISMQ_RUN_MODE '{env_mode}', using auto-detection")
        
        self.subprocess_wrapper = SubprocessWrapper(mode=run_mode)
        logger.info(f"ModuleRunner initialized with subprocess mode: {self.subprocess_wrapper.mode}")
        
        # Add diagnostic logging for event loop policy (Windows deployment validation)
        policy = asyncio.get_event_loop_policy()
        logger.info(f"Event loop policy: {type(policy).__name__}")
        
        if sys.platform == 'win32':
            if not isinstance(policy, asyncio.WindowsProactorEventLoopPolicy):
                logger.error("=" * 70)
                logger.error("CRITICAL: Wrong event loop policy on Windows!")
                logger.error(f"Current policy: {type(policy).__name__}")
                logger.error("Expected: WindowsProactorEventLoopPolicy")
                logger.error("=" * 70)
                logger.error("Start server with: python -m src.uvicorn_runner")
                logger.error("Or set environment variable: PRISMQ_RUN_MODE=threaded")
                logger.error("=" * 70)
    
    async def execute_module(
        self,
        module_id: str,
        module_name: str,
        script_path: Path,
        parameters: Dict,
        run_id: Optional[str] = None,
        save_config: bool = True
    ) -> Run:
        """
        Execute a PrismQ module asynchronously.
        
        Args:
            module_id: Unique module identifier
            module_name: Human-readable module name
            script_path: Path to the module's main.py
            parameters: Dictionary of module parameters
            run_id: Optional custom run ID
            save_config: Whether to save parameters to config storage
            
        Returns:
            Run object with status and metadata
            
        Raises:
            ValueError: If module is invalid
            RuntimeError: If max concurrent runs exceeded
        """
        # Save configuration if requested and storage is available
        if save_config and self.config_storage:
            self.config_storage.save_config(module_id, parameters)
        
        # Generate run ID if not provided
        if not run_id:
            run_id = self._generate_run_id(module_id)
        
        # Check concurrent run limit
        if len(self.registry.get_active_runs()) >= self.max_concurrent_runs:
            raise ResourceLimitException(
                f"Max concurrent runs ({self.max_concurrent_runs}) exceeded",
                resource_type="concurrent_runs"
            )
        
        # Check system resources if resource manager is available
        if self.resource_manager:
            resources_available, reason = self.resource_manager.check_resources_available()
            if not resources_available:
                raise ResourceLimitException(
                    f"Insufficient system resources: {reason}",
                    resource_type="system"
                )
        
        # Create run record
        run = Run(
            run_id=run_id,
            module_id=module_id,
            module_name=module_name,
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters=parameters
        )
        
        # Register the run
        self.registry.add_run(run)
        
        # Start execution asynchronously (fire and forget)
        asyncio.create_task(self._execute_async(run, script_path, parameters))
        
        return run
    
    async def _execute_async(self, run: Run, script_path: Path, parameters: Dict):
        """
        Internal async execution handler.
        
        This method handles the full lifecycle of a module run.
        
        Args:
            run: Run object to update
            script_path: Path to module script
            parameters: Module parameters
        """
        try:
            # Small delay to allow API response to return before starting execution
            # This prevents race conditions in tests and gives time for status checks
            await asyncio.sleep(0.1)
            
            # Validate script exists
            if not script_path.exists():
                raise ModuleExecutionException(
                    f"Module script not found: {script_path}",
                    run_id=run.run_id
                )
            
            # Update status to running
            run.status = RunStatus.RUNNING
            run.started_at = datetime.now(timezone.utc)
            self.registry.update_run(run)
            
            # Build command
            command = self._build_command(script_path, parameters)
            
            # Create subprocess using wrapper (cross-platform)
            logger.debug(f"Creating subprocess with mode {self.subprocess_wrapper.mode}")
            process, stdout_reader, stderr_reader = await self.subprocess_wrapper.create_subprocess(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=script_path.parent
            )
            
            # Start output capture
            stdout_task, stderr_task = await self.output_capture.start_capture(
                run_id=run.run_id,
                stdout_stream=stdout_reader,
                stderr_stream=stderr_reader
            )
            
            # Wait for process completion
            exit_code = await process.wait()
            
            # Wait for output capture to complete
            await stdout_task
            await stderr_task
            
            # Update run with results
            run.status = RunStatus.COMPLETED if exit_code == 0 else RunStatus.FAILED
            run.completed_at = datetime.now(timezone.utc)
            run.exit_code = exit_code
            run.duration_seconds = int(
                (run.completed_at - run.started_at).total_seconds()
            )
            
            # Set error message if failed
            if exit_code != 0:
                # Get last few error lines from captured logs
                logs = self.output_capture.get_logs(run.run_id, tail=10)
                error_lines = [
                    log.message for log in logs
                    if log.stream == "stderr" or log.level == "ERROR"
                ]
                if error_lines:
                    run.error_message = "\n".join(error_lines[-5:])[:500]
                
        except asyncio.CancelledError:
            run.status = RunStatus.CANCELLED
            run.completed_at = datetime.now(timezone.utc)
            logger.info(f"Run {run.run_id} was cancelled")
        except SubprocessPolicyException as e:
            # Windows event loop policy not configured for subprocess execution
            run.status = RunStatus.FAILED
            run.error_message = (
                "Windows event loop not configured for subprocess execution. "
                "Restart server with: python -m src.uvicorn_runner"
            )
            run.completed_at = datetime.now(timezone.utc)
            logger.error(
                f"SubprocessPolicyException in run {run.run_id}: {e.message}. "
                f"Current policy: {e.current_policy}. "
                f"Restart server with: python -m src.uvicorn_runner"
            )
        except NotImplementedError as e:
            run.status = RunStatus.FAILED
            run.error_message = (
                "Subprocess creation not supported on this platform. "
                "On Windows, use THREADED mode or set ProactorEventLoopPolicy. "
                "Set PRISMQ_RUN_MODE=threaded environment variable."
            )
            run.completed_at = datetime.now(timezone.utc)
            logger.error(
                f"NotImplementedError in run {run.run_id}: {e}. "
                f"Current subprocess mode: {self.subprocess_wrapper.mode}. "
                f"Try setting PRISMQ_RUN_MODE=threaded"
            )
        except FileNotFoundError as e:
            run.status = RunStatus.FAILED
            run.error_message = f"File not found: {e.filename or str(e)}"
            run.completed_at = datetime.now(timezone.utc)
            logger.error(f"File not found in run {run.run_id}: {e}")
        except PermissionError as e:
            run.status = RunStatus.FAILED
            run.error_message = "Permission denied executing module"
            run.completed_at = datetime.now(timezone.utc)
            logger.error(f"Permission error in run {run.run_id}: {e}")
        except asyncio.TimeoutError:
            run.status = RunStatus.FAILED
            run.error_message = "Module execution timed out"
            run.completed_at = datetime.now(timezone.utc)
            logger.error(f"Timeout in run {run.run_id}")
        except ModuleExecutionException as e:
            run.status = RunStatus.FAILED
            run.error_message = e.message
            run.completed_at = datetime.now(timezone.utc)
            logger.error(f"Module execution error in run {run.run_id}: {e.message}")
        except Exception as e:
            run.status = RunStatus.FAILED
            run.error_message = f"Unexpected error: {str(e)}"
            run.completed_at = datetime.now(timezone.utc)
            logger.error(f"Run {run.run_id} failed with exception: {e}", exc_info=True)
        finally:
            self.registry.update_run(run)
            self.output_capture.cleanup_run(run.run_id)
    
    def _build_command(self, script_path: Path, parameters: Dict) -> list[str]:
        """
        Build command line arguments from parameters.
        
        Args:
            script_path: Path to the script
            parameters: Parameter dictionary
            
        Returns:
            Command as list of strings
        """
        command = ["python", str(script_path)]
        
        # Add parameters as command-line arguments
        for key, value in parameters.items():
            command.append(f"--{key}")
            command.append(str(value))
        
        return command
    
    def _generate_run_id(self, module_id: str) -> str:
        """
        Generate unique run ID.
        
        Format: run_YYYYMMDD_HHMMSS_<module_id>_<unique_id>
        
        Args:
            module_id: Module identifier
            
        Returns:
            Unique run ID string
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"run_{timestamp}_{module_id}_{unique_id}"
    
    async def cancel_run(self, run_id: str) -> bool:
        """
        Cancel a running module execution.
        
        Args:
            run_id: Run identifier
            
        Returns:
            True if run was cancelled, False if not found or already completed
        """
        run = self.registry.get_run(run_id)
        if not run:
            return False
        
        if run.status not in [RunStatus.QUEUED, RunStatus.RUNNING]:
            return False
        
        # Cancel the process
        await self.process_manager.cancel_process(run_id)
        
        # Update run status
        run.status = RunStatus.CANCELLED
        run.completed_at = datetime.now(timezone.utc)
        if run.started_at:
            run.duration_seconds = int(
                (run.completed_at - run.started_at).total_seconds()
            )
        self.registry.update_run(run)
        
        return True
    
    def get_run_status(self, run_id: str) -> Optional[Run]:
        """
        Get current status of a run.
        
        Args:
            run_id: Run identifier
            
        Returns:
            Run object if found, None otherwise
        """
        return self.registry.get_run(run_id)
