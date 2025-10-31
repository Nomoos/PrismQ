"""Run API endpoints."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from ..core import (
    ModuleRunner,
    OutputCapture,
    ProcessManager,
    get_module_runner,
    get_output_capture,
    get_process_manager,
)
from ..models.run import (
    LogEntry,
    LogResponse,
    OutputFile,
    ResultsResponse,
    ResultsSummary,
    Run,
    RunCreate,
    RunListResponse,
    RunStatus,
)

from ..api.modules import get_module

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/modules/{module_id}/run", response_model=Run, status_code=status.HTTP_202_ACCEPTED)
async def create_run(
    module_id: str,
    run_create: RunCreate,
    runner: ModuleRunner = Depends(get_module_runner)
):
    """
    Launch a module with specified parameters.
    
    Args:
        module_id: Module identifier
        run_create: Run configuration
        runner: Module runner service (injected)
        
    Returns:
        Run: Created run details
        
    Raises:
        HTTPException: If module not found or max concurrent runs exceeded
    """
    # Get module info to validate it exists
    module = await get_module(module_id)
    
    # Execute module
    try:
        run = await runner.execute_module(
            module_id=module_id,
            module_name=module.name,
            script_path=Path(module.script_path),
            parameters=run_create.parameters,
            save_config=run_create.save_config
        )
        return run
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/runs", response_model=RunListResponse)
async def list_runs(
    module_id: Optional[str] = Query(None, description="Filter by module"),
    status_filter: Optional[RunStatus] = Query(None, alias="status", description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    runner: ModuleRunner = Depends(get_module_runner)
):
    """
    List all runs (current and historical).
    
    Args:
        module_id: Optional module filter
        status_filter: Optional status filter
        limit: Number of results per page
        offset: Pagination offset
        runner: Module runner service (injected)
        
    Returns:
        RunListResponse: List of runs
    """
    # Get all runs from registry
    if module_id:
        filtered_runs = runner.registry.get_runs_by_module(module_id)
    elif status_filter:
        filtered_runs = runner.registry.get_runs_by_status(status_filter)
    else:
        filtered_runs = runner.registry.get_recent_runs(limit=1000)
    
    # Sort by created_at descending
    filtered_runs = sorted(filtered_runs, key=lambda r: r.created_at, reverse=True)
    
    # Apply pagination
    total = len(filtered_runs)
    paginated_runs = filtered_runs[offset : offset + limit]
    
    return RunListResponse(
        runs=paginated_runs,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/runs/{run_id}", response_model=Run)
async def get_run(
    run_id: str,
    runner: ModuleRunner = Depends(get_module_runner)
):
    """
    Get detailed status of a specific run.
    
    Args:
        run_id: Run identifier
        runner: Module runner service (injected)
        
    Returns:
        Run: Run details
        
    Raises:
        HTTPException: If run not found
    """
    run = runner.get_run_status(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    return run


@router.delete("/runs/{run_id}", response_model=Run)
async def cancel_run(
    run_id: str,
    runner: ModuleRunner = Depends(get_module_runner)
):
    """
    Cancel a running module execution.
    
    Args:
        run_id: Run identifier
        runner: Module runner service (injected)
        
    Returns:
        Run: Cancelled run details
        
    Raises:
        HTTPException: If run not found or cannot be cancelled
    """
    run = runner.get_run_status(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    if run.status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel run: already {run.status.value}",
        )
    
    success = await runner.cancel_run(run_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel run"
        )
    
    # Return updated run
    return runner.get_run_status(run_id)


@router.get("/runs/{run_id}/logs", response_model=LogResponse)
async def get_run_logs(
    run_id: str,
    tail: int = Query(500, ge=1, le=10000, description="Number of recent lines"),
    since: Optional[str] = Query(None, description="ISO timestamp to get logs after"),
    runner: ModuleRunner = Depends(get_module_runner),
    output_capture: OutputCapture = Depends(get_output_capture)
):
    """
    Retrieve logs for a specific run.
    
    Args:
        run_id: Run identifier
        tail: Number of recent lines to return
        since: ISO timestamp to get logs after (optional)
        runner: Module runner service (injected)
        output_capture: Output capture service (injected)
        
    Returns:
        LogResponse: Log entries
        
    Raises:
        HTTPException: If run not found
    """
    # Check if run exists
    run = runner.get_run_status(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # Parse since timestamp if provided
    since_dt = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid timestamp format. Use ISO 8601 format."
            )
    
    # Get logs from output capture
    log_entries = output_capture.get_logs(run_id, tail=tail, since=since_dt)
    all_logs = output_capture.get_logs(run_id)
    total_lines = len(all_logs)
    
    # Convert to LogEntry model objects
    logs = [
        LogEntry(
            timestamp=entry.timestamp,
            level=entry.level,
            message=entry.message
        )
        for entry in log_entries
    ]
    
    return LogResponse(
        run_id=run_id,
        logs=logs,
        total_lines=total_lines,
        truncated=tail is not None and len(log_entries) < total_lines,
    )


@router.get("/runs/{run_id}/logs/stream")
async def stream_run_logs(
    run_id: str,
    runner: ModuleRunner = Depends(get_module_runner),
    output_capture: OutputCapture = Depends(get_output_capture)
):
    """
    Stream logs in real-time using Server-Sent Events.
    
    Args:
        run_id: Run identifier
        runner: Module runner service (injected)
        output_capture: Output capture service (injected)
        
    Returns:
        EventSourceResponse: SSE stream
        
    Raises:
        HTTPException: If run not found
    """
    # Check if run exists
    run = runner.get_run_status(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    async def event_generator():
        """Generate SSE events for log streaming."""
        try:
            async for log_entry in output_capture.subscribe_sse(run_id):
                # Convert to LogEntry model
                log = LogEntry(
                    timestamp=log_entry.timestamp,
                    level=log_entry.level,
                    message=log_entry.message
                )
                yield {
                    "event": "log",
                    "data": log.model_dump_json(),
                }
                
                # Check if run is complete
                current_run = runner.get_run_status(run_id)
                if current_run and current_run.status in [
                    RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED
                ]:
                    # Send completion event and break
                    yield {
                        "event": "complete",
                        "data": json.dumps({"status": current_run.status.value}),
                    }
                    break
        except Exception as e:
            logger.error(f"Error in SSE stream for run {run_id}: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }
    
    return EventSourceResponse(
        event_generator(),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/runs/{run_id}/logs/download")
async def download_log_file(
    run_id: str,
    runner: ModuleRunner = Depends(get_module_runner),
    output_capture: OutputCapture = Depends(get_output_capture)
):
    """
    Download complete log file for a run.
    
    Args:
        run_id: Run identifier
        runner: Module runner service (injected)
        output_capture: Output capture service (injected)
        
    Returns:
        StreamingResponse: Log file as plain text download
        
    Raises:
        HTTPException: If run or log file not found
    """
    # Check if run exists
    run = runner.get_run_status(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # Read log file
    log_content = await output_capture.read_log_file(run_id)
    
    if not log_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log file not found"
        )
    
    return StreamingResponse(
        iter([log_content]),
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={run_id}.log"
        }
    )


@router.get("/runs/{run_id}/results", response_model=ResultsResponse)
async def get_run_results(
    run_id: str,
    runner: ModuleRunner = Depends(get_module_runner)
):
    """
    Get execution results and output artifacts.
    
    Args:
        run_id: Run identifier
        runner: Module runner service (injected)
        
    Returns:
        ResultsResponse: Execution results
        
    Raises:
        HTTPException: If run not found
    """
    run = runner.get_run_status(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # Mock results data (to be enhanced with real output file scanning)
    summary = ResultsSummary(
        items_collected=run.items_total or 0,
        items_saved=run.items_processed or 0,
        errors=0 if run.status == RunStatus.COMPLETED else 1,
        duration_seconds=run.duration_seconds or 0,
    )
    
    output_files = []
    if run.status == RunStatus.COMPLETED:
        # Mock output file
        output_files = [
            OutputFile(
                filename=f"{run.module_id}_{run.created_at.strftime('%Y%m%d')}.json",
                path=f"/outputs/{run.module_id}_{run.created_at.strftime('%Y%m%d')}.json",
                size_bytes=245680,
                created_at=run.completed_at or run.created_at,
            )
        ]
    
    return ResultsResponse(
        run_id=run_id,
        status=run.status,
        summary=summary,
        output_files=output_files,
        metrics={},
    )
